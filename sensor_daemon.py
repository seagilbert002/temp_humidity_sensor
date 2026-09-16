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
SHELF_ID = os.getenv("SHELF_ID", "LOFT_SHELF_2")
SAMPLING_INTERVAL_SEC = int(os.getenv(" SAMPLING_INTERVAL", "30"))
INITIAL_BACKOFF_SEC = 1
MAX_BACKOFF_SEC = 60

