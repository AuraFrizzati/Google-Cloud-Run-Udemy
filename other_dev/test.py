import os
import datetime
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL1 = "https://www2.nphs.wales.nhs.uk/WHAIPDocs.nsf"
URL2 = "https://www.nhfd.co.uk/20/nhfdcharts.nsf/vwCharts/Mortality"

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
        'content': result_content
    }

if __name__ == "__main__":
    # Check if a specific URL is provided via environment variable
    target_url = os.environ.get('TARGET_URL')
    
    if target_url:
        print(f"Testing URL from environment variable: {target_url}")
        check_connection(target_url)
    else:
        print("Testing both default URLs:")
        print("\n=== Testing URL1 ===")
        check_connection(URL1)
        print("\n=== Testing URL2 ===")
        check_connection(URL2)