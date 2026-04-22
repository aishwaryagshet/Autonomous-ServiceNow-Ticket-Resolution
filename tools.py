from langchain.tools import tool
import subprocess

import paramiko
import re

@tool
def ping_device(ip: str) -> str:
    """Ping a device and return reachable/unreachable"""
    try:
        result = subprocess.run(["ping", "-n", "2", ip], capture_output=True, text=True)
        print(result.stdout)
        if "TTL=" in result.stdout:
            return "reachable"
        return "unreachable"
    except Exception as e:
        return f"error: {str(e)}"


def parse_uptime(output):
    """
    Extract uptime in minutes from device output.
    Supports formats like:
    - 'up 45 minutes'
    - 'up 1 hour, 10 minutes'
    - 'up 2 days, 3 hours'
    """
    minutes = 0

    # Days
    days = re.search(r'(\d+)\s+day', output)
    if days:
        minutes += int(days.group(1)) * 24 * 60

    # Hours
    hours = re.search(r'(\d+)\s+hour', output)
    if hours:
        minutes += int(hours.group(1)) * 60

    # Minutes
    mins = re.search(r'(\d+)\s+minute', output)
    if mins:
        minutes += int(mins.group(1))

    return minutes

@tool
def check_device_status(ip, username, password, command="show version"):
    """ Execute show version on the device to fetch uptime of the device and check is device is up or down"""
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(hostname=ip, username=username, password=password, timeout=10)

        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.read().decode().lower()
        error = stderr.read().decode()

        client.close()

        if error:
            print("Error from device:", error)
            return "Device DOWN"

        # Check if device responded properly
        if "up" not in output:
            return "Device DOWN (no valid uptime info)"

        #  Parse uptime
        uptime_minutes = parse_uptime(output)

        print(f"Uptime (minutes): {uptime_minutes}")

        # Condition
        if uptime_minutes > 30:
            return "Device is UP"
        else:
            return "Device is DOWN (uptime < 30 min)"

    except Exception as e:
        return f"Device DOWN (connection failed): {str(e)}"



