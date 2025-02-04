# Infrared flame sensor KY-026

from machine import ADC, Pin

class KY026:
    ADC_PIN = 14
    FLAME_THRESHOLD = 1000

    def __init__(self, adc_pin=ADC_PIN, threshold=FLAME_THRESHOLD):
        self.sensor = ADC(Pin(adc_pin, Pin.IN))
        self.threshold = threshold

    def is_flame_detected(self):
        print(f"Reading flame sensor: {self.sensor.read()}")
        return self.sensor.read() < self.threshold  # Verifica se o valor lido é menor que o limiar
    