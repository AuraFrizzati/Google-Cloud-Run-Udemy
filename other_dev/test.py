import os
import datetime
import requests
import urllib3
from flask import Flask, render_template_string

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL1 = "https://www2.nphs.wales.nhs.uk/WHAIPDocs.nsf"
URL2 = "https://www.nhfd.co.uk/20/nhfdcharts.nsf/vwCharts/Mortality"

app = Flask(__name__)

# HTML template for displaying results
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Connection Check Dashboard</title>
    <style>
        body { font-family: Arial, fzsans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .result { margin: 20px 0; padding: 15px; border-radius: 5px; border-left: 5px solid #ccc; }
        .success { border-left-color: #28a745; background-color: #d4edda; }
        .failure { border-left-color: #dc3545; background-color: #f8d7da; }
        .url { font-weight: bold; color: #0066cc; word-break: break-all; }
        .status { font-size: 18px; margin: 10px 0; }
        .details { color: #666; margin-top: 10px; }
        .refresh-btn { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 20px 0; }
        .refresh-btn:hover { background-color: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="header">🌐 Connection Check Dashboard</h1>
        
        {% for result in results %}
        <div class="result {% if result.successful %}success{% else %}failure{% endif %}">
            <div class="url">{{ result.url }}</div>
            <div class="status">
                Status: {{ result.status }} 
                {% if result.successful %}✅ Success{% else %}❌ Failed{% endif %}
            </div>
            <div class="details">
                Response Time: {{ "%.3f"|format(result.response_time) }}s<br>
                Checked at: {{ result.timestamp }}
            </div>
        </div>
        {% endfor %}
        
        <button class="refresh-btn" onclick="window.location.reload()">🔄 Refresh Results</button>
    </div>
</body>
</html>
"""

def check_connection(target_url):
    """Check connection to a given URL and return results."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    local_file_name = f"/tmp/check_result_{timestamp}.txt"
    destination_blob_name = f"connection_logs/result_{timestamp}.txt"

    # Add headers to appear more like a regular browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(
        target_url, 
        timeout=10, 
        allow_redirects=True,
        headers=headers
        ,verify=False
    )
    status = response.status_code
    is_successful = 200 <= status < 400 
    result_content = (
        f"--- Connection Check Result ---\n"
        f"URL: {target_url}\n"
        f"Timestamp: {timestamp}\n"
        f"HTTP Status Code: {status}\n"
        f"Connection Successful: {is_successful}\n"
        f"Response Time (s): {response.elapsed.total_seconds():.3f}\n"
    )
    print(f"Connection check complete. Status: {status}")
    print(f"Result Content: {result_content}")
    
    return {
        'url': target_url,
        'status': status,
        'successful': is_successful,
        'response_time': response.elapsed.total_seconds(),
        'content': result_content,
        'timestamp': timestamp
    }

@app.route('/')
def dashboard():
    """Flask route to display connection check results."""
    results = []
    
    # Test both URLs
    for url in [URL1, URL2]:
        try:
            result = check_connection(url)
            results.append(result)
        except Exception as e:
            results.append({
                'url': url,
                'status': 'Error',
                'successful': False,
                'response_time': 0,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S"),
                'error': str(e)
            })
    
    return render_template_string(HTML_TEMPLATE, results=results)

if __name__ == "__main__":
    # Check if a specific URL is provided via environment variable
    target_url = os.environ.get('TARGET_URL')
    
    if target_url:
        print(f"Testing URL from environment variable: {target_url}")
        check_connection(target_url)
    else:
        # Check if Flask mode is requested
        flask_mode = os.environ.get('FLASK_MODE', 'true').lower() == 'true'
        
        if flask_mode:
            print("Starting Flask dashboard...")
            print("Visit http://localhost:8080 to view the dashboard")
            app.run(debug=True, host='0.0.0.0', port=8080)
        else:
            print("Testing both default URLs:")
            print("\n=== Testing URL1 ===")
            check_connection(URL1)
            print("\n=== Testing URL2 ===")
            check_connection(URL2)
            print("\nTo run Flask dashboard, set FLASK_MODE=true")