Bitaxe-Temperature-Control

A small Python script for monitoring and adjusting the ASIC temperature of the Bitaxe using a Raspberry Pi and Systemd Service.
Overview

I wrote a small script in Python to monitor and adjust the ASIC temperature of the Bitaxe. The motivation behind this was to maintain optimal performance by controlling the temperature, especially as it fluctuates throughout the day due to environmental changes and nearby heat-emitting electronics. 

I'm not entirely sure at what temperature the Bitaxe would automatically shut down or throttle the frequency to protect the chip from overheating (and i was to lazy to look at every firmware change log tbh), so I decided to take matters into my own hands. This script checks the temperature via the Bitaxe API every 5 minutes and adjusts the frequency to two predefined levels if necessary, helping to prevent overheating.
Features
    -Temperature Monitoring: The script regularly checks the ASIC temperature every 5 minutes using the Bitaxe's API.
    -Frequency Adjustment: If the temperature exceeds a predefined threshold, the script adjusts the frequency to a lower level to reduce the heat.
    -Automatic Restart: The script can automatically restart the Bitaxe after adjusting the frequency to ensure the changes take effect.
    -Customizable Settings: You can customize the temperature threshold and frequency levels via environment variables, making the script adaptable to different setups.

How It Works

The script performs the following actions:
    Get System Information: Calls the Bitaxe API to retrieve the current temperature and frequency.
    Check Temperature: Compares the current temperature against a user-defined threshold.
    Adjust Frequency: If the temperature exceeds the threshold, the script attempts to lower the frequency to a predefined level (two levels are supported).
    Restart the System: After adjusting the frequency, the script restarts the Bitaxe to apply the changes.

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

Edit the Script:
    If needed, adjust the environment variables directly in the script or export them in your shell.

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
    Environment=BITAXE_IP=http://{your_ip_here}
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

Customization

You can customize the behavior of the script by setting the following environment variables:

BITAXE_IP: The IP address of the Bitaxe device.
TEMP_THRESHOLD: The temperature threshold (in Celsius) above which the script will attempt to lower the frequency.
FIRST_FREQUENCY: The first frequency level to set when the temperature exceeds the threshold.
SECOND_FREQUENCY: The second, lower frequency level to set if the temperature remains high after the first adjustment.
CHECK_INTERVAL: The interval (in seconds) between temperature checks.
