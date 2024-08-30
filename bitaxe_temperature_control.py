import requests
import time
import os
from requests.exceptions import HTTPError, RequestException
from collections import deque
from datetime import datetime, timedelta
import signal

# Configuration variables
BITAXE_IP = os.getenv("BITAXE_IP", "http://192.168.2.117")
API_INFO_ENDPOINT = f"{BITAXE_IP}/api/system/info"
API_PATCH_ENDPOINT = f"{BITAXE_IP}/api/system"
API_RESTART_ENDPOINT = f"{BITAXE_IP}/api/system/restart"
TEMP_THRESHOLD = int(os.getenv("TEMP_THRESHOLD", 65))
FIRST_FREQUENCY = int(os.getenv("FIRST_FREQUENCY", 500))
SECOND_FREQUENCY = int(os.getenv("SECOND_FREQUENCY", 410))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))  # 5 minutes by default
MAX_FREQUENCY = 575
STABLE_TIMEFRAME = timedelta(hours=1)

TEMP_INCREASE_THRESHOLD = 64

# Initialize temperature history deque with an appropriate maxlen
temperature_history = deque(maxlen=int(STABLE_TIMEFRAME.total_seconds() // CHECK_INTERVAL))

def get_system_info():
    retry_attempts = 3
    for attempt in range(retry_attempts):
        try:
            response = requests.get(API_INFO_ENDPOINT)
            response.raise_for_status()
            data = response.json()
            if 'temp' not in data or 'frequency' not in data:
                print_log("Unexpected API response format:", data)
                return None
            return data
        except (HTTPError, RequestException) as e:
            print_log(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            print_log(f"An unexpected error occurred: {e}")
            break
    return None

def patch_frequency(frequency):
    payload = {"frequency": frequency}
    retry_attempts = 3
    for attempt in range(retry_attempts):
        try:
            response = requests.patch(API_PATCH_ENDPOINT, json=payload)
            response.raise_for_status()
            print_log(f"Frequency set to {frequency} MHz.")
            return True
        except (HTTPError, RequestException) as e:
            print_log(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            print_log(f"An unexpected error occurred while setting frequency: {e}")
            break
    return False

def restart_system():
    try:
        response = requests.post(API_RESTART_ENDPOINT)
        response.raise_for_status()
        print_log("System restart initiated.")
    except HTTPError as http_err:
        print_log(f"HTTP error occurred while restarting system: {http_err}")
    except RequestException as req_err:
        print_log(f"Request error occurred while restarting system: {req_err}")
    except Exception as e:
        print_log(f"An unexpected error occurred while restarting system: {e}")

def check_temperature_stability():
    if len(temperature_history) < STABLE_TIMEFRAME.total_seconds() // CHECK_INTERVAL:
        return False  # Not enough data yet
    avg_temp = sum(temp for temp, _ in temperature_history) / len(temperature_history)
    if avg_temp <= TEMP_THRESHOLD:
        return True  # Temperature has been stable or below threshold
    return False

def print_log(message):
    """Utility function to print a message with the current time and date."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def graceful_shutdown(signum, frame):
    print_log(f"Received signal {signum}. Shutting down gracefully...")
    exit(0)

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, graceful_shutdown)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, graceful_shutdown)  # Handle termination signal

def monitor_and_adjust():
    current_frequency = MAX_FREQUENCY
    last_adjustment_time = datetime.now()

    while True:
        try:
            system_info = get_system_info()
            if system_info:
                temperature = system_info["temp"]
                frequency = system_info["frequency"]

                print_log(f"Current Temperature: {temperature}°C at frequency {frequency} MHz")

                # Ensure frequency does not exceed MAX_FREQUENCY
                if frequency > MAX_FREQUENCY:
                    print_log(f"Frequency {frequency} MHz exceeds maximum allowed {MAX_FREQUENCY} MHz. Adjusting down.")
                    if patch_frequency(MAX_FREQUENCY):
                        restart_system()
                        current_frequency = MAX_FREQUENCY
                        last_adjustment_time = datetime.now()
                        continue  # Skip to the next loop iteration after adjustment

                temperature_history.append((temperature, datetime.now()))

                if temperature > TEMP_THRESHOLD:
                    print_log("Temperature exceeded threshold!")
                    if current_frequency > SECOND_FREQUENCY:
                        new_frequency = max(SECOND_FREQUENCY, FIRST_FREQUENCY - 50)
                        print_log(f"Attempting to set frequency to {new_frequency} MHz...")
                        if patch_frequency(new_frequency):
                            restart_system()
                            current_frequency = new_frequency
                            last_adjustment_time = datetime.now()
                elif (temperature < TEMP_INCREASE_THRESHOLD and
                      datetime.now() - last_adjustment_time > STABLE_TIMEFRAME and
                      check_temperature_stability()):
                    if current_frequency < MAX_FREQUENCY:
                        new_frequency = min(current_frequency + 25, MAX_FREQUENCY)
                        print_log(f"Temperature stable, increasing frequency to {new_frequency} MHz...")
                        if patch_frequency(new_frequency):
                            restart_system()
                            current_frequency = new_frequency
                            last_adjustment_time = datetime.now()
                else:
                    print_log("Temperature is within safe limits.")
            else:
                print_log("Failed to retrieve system information.")
        except Exception as e:
            print_log(f"An error occurred in the monitoring loop: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        monitor_and_adjust()
    except KeyboardInterrupt:
        print_log("Monitoring stopped by user.")
