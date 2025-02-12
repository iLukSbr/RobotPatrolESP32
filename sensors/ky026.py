# Infrared flame sensor KY-026

from machine import ADC, Pin

class KY026:
    ADC_PIN = 4
    FLAME_THRESHOLD = 1000

    def __init__(self, pin=ADC_PIN, threshold=FLAME_THRESHOLD):
        self.sensor = ADC(Pin(pin, Pin.IN))
        self.threshold = threshold

    def is_flame_detected(self):
        sensor_value = self.sensor.read()
        # print(f"Reading flame sensor: {sensor_value}")
        return self.sensor.read() > self.threshold  # Verifies if value read is greater than threshold
    