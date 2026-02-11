import threading
from collections import deque
import time
import board
import busio
import adafruit_ahtx0

class AHT20sensor:
    """
        interval: seconds between sensor reads
    """
    def __init__(self, interval=2.0):
        self.interval = interval
        self._lock = threading.Lock()
        self._running = False 
        self._latest = None

        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_ahtx0.AHTx0(i2c)

    def _read_sensor(self):
        """Background thread that continuously polls the sensor."""
        while self._running:
            reading = {
                'temperature': self.sensor.temperature,
                'humidity': self.sensor.relative_humidity
            }

            with self._lock:
                self._latest = reading

            time.sleep(self.interval)

    def start(self):
        if self._running:
            return
        
        self._running = True
        thread = threading.Thread(
            target=self._read_sensor,
            daemon=True
        )
        thread.start()

    def stop(self):
        """Stop background sensor polling."""
        self._running = False

    def get_latest(self):
        """Return the most recent sensor reading."""
        with self._lock:
            return self._latest