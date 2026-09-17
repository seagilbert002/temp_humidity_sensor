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

class BookshelfTelemetryDaemon:
    def __init__(self):
        self.running = True
        self.sensor = sensor_hal.get_sensor()
        self.backoff_interval = INITIAL_BACKOFF_SEC

        # Register a SIGINT (Ctrl+C) and SIGTERM (systemd stop) handlers

    # Cleanly handles a halt to the event loop and releases hardware resources
    def _handle_shutdown(self, signum, frame):
        prinf(f"\n[Daemon] Shutdown signal ({signum}) received. Cleaning up...")
        self.running = False

    # Transmits the JSON over an HTTP post to the api
    def _transmit_payload(self, payload: dict) -> bool:
        json_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
                API_URL,
                data=json_bytes,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "BookshelfTelemetryDaemon"
                    },
                method="POST"
                )

        # Timeout after 5 seconds to avoid blocking the event loop
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status in (200, 201, 202)

    # Main asynchronous event loop with the exponential backoff
    def run(self):
        print(f"[Daemon] Starting BookshelfTelemetryDaemon for {SHELF_ID}")
        print(f"[Daemon] Target Endpoint: {API_URL}")

        while self.running:
            # Read from the HAL
            reading = self.sensor.read_telemetry()

            # Construct payload matching the database schema 
            payload = {
                    "shelfID": SHELF_ID,
                    "tempC": reading["temperature_c"],
                    "humidity": reading["humidity_percent"],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                    }

            # Transmit the payload if not successful wait the corresponding backoff
            try:
                success = self._transmit_payload(payload)
                if success:
                    print(
                            f"[Telemetry Sent] Shelf: {SHELF_ID} | "
                            f"Temp: {payload['temperature_c']}°C | "
                            f"Humidity: {payload['humidity']}%"
                            )

                    # Reset backoff interval if successful
                    self.backoff_interval = INITIAL_BACKOFF_SEC

            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
                print(
                        f"[Network Warning] Transmission failed ({e}). "
                        f"Retrying in {self.backoff_interval}s..."
                        )

                # Sleep for the backoff interval
                time.sleep(self.backoff_interval)

                # Double the backoff interval until it reachs a max of 60
                self.backoff_interval = min(self.backoff_interval * 2, MAX_BACKOFF_SEC)
                continue

        # Standard sample pause
        time.sleep(SAMPLING_INTERVAL_SEC)

        # Cleanup after the loop
        self.sensor.cleanup()
        print("[Daemon] Stopped cleanly.")

if __name__ == "__main__":
    daemon = BookshelfTelemetryDaemon()
    daemon.run()
