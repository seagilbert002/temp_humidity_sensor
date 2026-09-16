"""
Bookshelf Telemetry Daemon
"""

import json
import os
import signal
import sys
import time
from datetime import datetime, timezone
import urllib.request
import urllib.error

# Import the sensorHAL
import sensor_hal

# Environment Variable Configuration
API_URL = os.getenv("TELEMETRY_API_URL", "http://localhost:3000/api/telemetry")

