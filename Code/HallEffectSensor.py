"""
Simple hall effect sensor device.
Tracks if magnet & sensor are aligned
"""
import digitalio

class HallEffectSensor:
    def __init__(self, pin):
        self.sensor = digitalio.DigitalInOut(pin)
        self.sensor.direction = digitalio.Direction.INPUT
        self.sensor.pull = digitalio.Pull.UP

    def deinit(self):
        self.sensor.deinit()

    @property
    def isAligned(self) -> bool:
        return not self.sensor.value
