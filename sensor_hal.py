# Author: Chrysanthemum GG
# Github: seagilbert002

# Importing for hardware functionality
from time import sleep

# Check for running in production or test environment
try:
    import board
    import adafruit_ahtx0
    HARDWARE_AVAILABLE = True
except (ImportError, NotImplementedError):
    # Fall back when running on dev machine
    HARDWARE_AVAILABLE = False

# Mock Sensor for testing on dev hardware
class MockSensorHAL:
    def read_telemetry(self):
        import random
        return {
                "temperature_c": round(random.uniform(18.0, 30.0), 1),
                "humidity_percent": round(random.uniform(40.0, 85.0), 1)
                }

# Reads the sensor data from the I2C bus
class SensorHAL:
    def __init__(self):
        self.i2c = board.I2C()
        self.sensor = adafruit_dhtx0.AHTx0(self.i2c)

    # Fetches the raw temps in celcius and relative humidity in %
    def read_telemetry(self):
        temperature_c = self.sensor.temperature
        humidity = self.sensor.relative_humidity

        if temperature_c is None or humidity is None:
            raise RuntimeError("Received empty or corrupted reading from I2C bus")

        return {
            "temperature_c": round(float(temperature_c), 1),
            "humidity_percent": round(float(humidity), 1)
        }

    def cleanup(self):
        "Safely releases the I2C bus"
        if hasattr(self.i2c, 'deinit'):
            self.i2c.deinit()
