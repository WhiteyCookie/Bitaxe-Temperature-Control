import requests
import time
import os
from requests.exceptions import HTTPError, RequestException

# Configuration variables
BITAXE_IP = os.getenv("BITAXE_IP", "http://192.168.2.117")
API_INFO_ENDPOINT = f"{BITAXE_IP}/api/system/info"
API_PATCH_ENDPOINT = f"{BITAXE_IP}/api/system"
API_RESTART_ENDPOINT = f"{BITAXE_IP}/api/system/restart"
TEMP_THRESHOLD = int(os.getenv("TEMP_THRESHOLD", 63))
FIRST_FREQUENCY = int(os.getenv("FIRST_FREQUENCY", 490))
SECOND_FREQUENCY = int(os.getenv("SECOND_FREQUENCY", 400))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))  # 5 minutes by default
MAX_RETRIES = 3  # Max number of retries for API calls
RETRY_DELAY = 5  # Delay between retries in seconds

def get_system_info():
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(API_INFO_ENDPOINT)
            response.raise_for_status()
            data = response.json()
            if 'temp' not in data or 'frequency' not in data:
                print("Unexpected API response format:", data)
                return None
            return data
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except RequestException as req_err:
            print(f"Request error occurred: {req_err}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
        print(f"Retrying... ({attempt + 1}/{MAX_RETRIES})")
        time.sleep(RETRY_DELAY)

    print("Failed to retrieve system information after multiple attempts.")
    return None

def patch_frequency(frequency):
    payload = {"frequency": frequency}  # Adjust key based on the API's requirement
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.patch(API_PATCH_ENDPOINT, json=payload)
            response.raise_for_status()
            print(f"Frequency set to {frequency} MHz.")
            return True
        except HTTPError as http_err:
            print(f"HTTP error occurred while setting frequency: {http_err}")
        except RequestException as req_err:
            print(f"Request error occurred while setting frequency: {req_err}")
        except Exception as e:
            print(f"An unexpected error occurred while setting frequency: {e}")

        print(f"Retrying... ({attempt + 1}/{MAX_RETRIES})")
        time.sleep(RETRY_DELAY)

    print(f"Failed to set frequency to {frequency} MHz after multiple attempts.")
    return False

def restart_system():
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(API_RESTART_ENDPOINT)
            response.raise_for_status()
            print("System restart initiated.")
            return True
        except HTTPError as http_err:
            print(f"HTTP error occurred while restarting system: {http_err}")
        except RequestException as req_err:
            print(f"Request error occurred while restarting system: {req_err}")
        except Exception as e:
            print(f"An unexpected error occurred while restarting system: {e}")
        
        print(f"Retrying... ({attempt + 1}/{MAX_RETRIES})")
        time.sleep(RETRY_DELAY)

    print("Failed to initiate system restart after multiple attempts.")
    return False

def monitor_and_adjust():
    while True:
        try:
            system_info = get_system_info()
            if system_info:
                temperature = system_info["temp"]
                frequency = system_info["frequency"]

                print(f"Current Temperature: {temperature}°C")
                if temperature > TEMP_THRESHOLD:
                    print("Temperature exceeded threshold!")
                    if frequency != FIRST_FREQUENCY:
                        print(f"Attempting to set frequency to {FIRST_FREQUENCY} MHz...")
                        if patch_frequency(FIRST_FREQUENCY):
                            restart_system()
                    else:
                        print(f"Attempting to set frequency to {SECOND_FREQUENCY} MHz...")
                        if patch_frequency(SECOND_FREQUENCY):
                            restart_system()
                else:
                    print("Temperature is within safe limits.")
            else:
                print("Failed to retrieve system information.")
        except Exception as e:
            print(f"An error occurred in the monitoring loop: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        monitor_and_adjust()
    except KeyboardInterrupt:
        print("Monitoring stopped by user.")
