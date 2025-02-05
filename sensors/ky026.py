# Infrared flame sensor KY-026

from machine import ADC, Pin

class KY026:
    ADC_PIN = 14
    FLAME_THRESHOLD = 1000

    def __init__(self, pin=ADC_PIN, threshold=FLAME_THRESHOLD):
        # self.sensor = ADC(Pin(adc_pin, Pin.IN))
        self.sensor =  Pin(pin, Pin.IN)
        # self.threshold = threshold

    def is_flame_detected(self):
        sensor_value = self.sensor.value()
        print(f"Reading flame sensor: {sensor_value}")
        return sensor_value
        # return self.sensor.read() < self.threshold  # Verifica se o valor lido é menor que o limiar
    