import requests
import time

URL = "https://193.167.189.95/api/groups/AMUMMM/certificates/"
HEADERS = {
    "Pwp-Api-Key": "iZe7EB9WTHrGpac0RfbRnrdXvHNRIPJ9shcJw3EMLv4"
}

def send_post_request():
    try:
        response = requests.post(URL, headers=HEADERS, verify=False)  # verify=False skips SSL cert check
        print(f"[{response.status_code}] {response.text}")
    except requests.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    print("⏱️ Starting to send POST requests every second...")
    while True:
        send_post_request()
        time.sleep(5)
