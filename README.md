Bitaxe-Temperature-Control

A Python script for monitoring and adjusting the ASIC temperature of the Bitaxe.
Overview

This script is designed to monitor and adjust the ASIC temperature of the Bitaxe, ensuring optimal performance by dynamically controlling the frequency based on temperature readings. 
It was developed to handle temperature fluctuations due to environmental changes or nearby heat-emitting electronics.

The motivation behind this project is to preemptively manage the temperature of the Bitaxe, as it's unclear if the device has built-in mechanisms to throttle or shut down to prevent overheating. 
This script regularly checks the temperature via the Bitaxe API and adjusts the operating frequency if necessary, helping to prevent overheating and maintain stable performance.

Features
    Temperature Monitoring: The script regularly checks the ASIC temperature every 5 minutes using the Bitaxe's API.
    Frequency Adjustment: The script adjusts the frequency in smaller, more precise steps if the temperature exceeds a predefined threshold. It supports multiple levels of frequency adjustments to fine-tune the response to temperature changes.
    Automatic Restart: After adjusting the frequency, the script restarts the Bitaxe to ensure that the changes take effect.
    Customizable Settings: The script allows customization of temperature thresholds, frequency levels, and check intervals via environment variables.
    Resilient API Communication: Implemented retry logic with exponential backoff for API requests to handle transient network issues more effectively.
    Graceful Shutdown: The script handles system signals for graceful shutdown, ensuring that it stops cleanly when necessary.
    Stability Checks: It uses a rolling average to determine temperature stability, providing more accurate and reliable adjustments.

How It Works

The script performs the following actions:
    -Get System Information: Calls the Bitaxe API to retrieve the current temperature and frequency.
    -Check Temperature: Compares the current temperature against a user-defined threshold.
    -Adjust Frequency: If the temperature exceeds the threshold, the script attempts to lower the frequency incrementally to predefined levels.
    -Restart the System: After adjusting the frequency, the script restarts the Bitaxe to apply the changes.
    -Monitor Stability: The script checks for temperature stability below a certain threshold before considering increasing the frequency back up, ensuring that the ASIC do not get too hot.

Setup Instructions
Prerequisites
    A Raspberry Pi running a recent version of Raspbian or similar.
    Python 3.9 or later installed on the Raspberry Pi.
    The Bitaxe device connected to the same network as the Raspberry Pi.

Installation
    Clone the Repository:

    git clone https://github.com/yourusername/bitaxe-temperature-control.git
    cd bitaxe-temperature-control

Create a Virtual Environment (Optional but Recommended):

    python3.9 -m venv venv
    source venv/bin/activate

Install Dependencies:

If your script has dependencies, install them via pip. For example:

    pip install requests

Running as a Systemd Service

To run the script automatically on startup and ensure it runs continuously in the background, set it up as a systemd service.

Create the Service File:

Create a new systemd service file:

    sudo nano /etc/systemd/system/bitaxe_temperature_control.service

Add the following content:

    [Unit]
    Description=Bitaxe Temperature Control
    After=network.target

    [Service]
    ExecStart=/usr/bin/python3.9 -u /home/pi/bitaxe-temperature-control/monitor.py
    WorkingDirectory=/home/pi/bitaxe-temperature-control/
    StandardOutput=journal
    StandardError=journal
    Restart=always
    User=pi
    Environment=BITAXE_IP=http://192.168.2.117
    Environment=TEMP_THRESHOLD=63
    Environment=FIRST_FREQUENCY=490
    Environment=SECOND_FREQUENCY=400
    Environment=CHECK_INTERVAL=300

    [Install]
    WantedBy=multi-user.target

Reload Systemd:

After creating the service file, reload systemd to recognize the new service:

    sudo systemctl daemon-reload

Enable and Start the Service:

Enable the service to start automatically on boot and start it immediately:

    sudo systemctl enable bitaxe_temperature_control.service &&
    sudo systemctl start bitaxe_temperature_control.service

Check the Status:

To check if the service is running correctly, use:

    sudo systemctl status bitaxe_temperature_control.service

You can also monitor the output in real-time:

    journalctl -u bitaxe_temperature_control.service -f

You can customize the behavior of the script by setting the following environment variables:

BITAXE_IP: The IP address of the Bitaxe device.
TEMP_THRESHOLD: The temperature threshold (in Celsius) above which the script will attempt to lower the frequency.
FIRST_FREQUENCY: The initial frequency level to set when the temperature exceeds the threshold.
SECOND_FREQUENCY: The lower frequency level to set if the temperature remains high after the first adjustment.
MAX_FREQUENCY: The maximum frequency level that the script will attempt to restore if the temperature is stable.
CHECK_INTERVAL: The interval (in seconds) between temperature checks.
STABLE_TIMEFRAME: The timeframe (in hours) used to assess temperature stability before considering increasing the frequency again.
