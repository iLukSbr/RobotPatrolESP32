# Infrared flame sensor KY-026

from machine import ADC, Pin

class KY026:
    ADC_PIN = 14
    FLAME_THRESHOLD = 1000

    def __init__(self, adc_pin=ADC_PIN, threshold=FLAME_THRESHOLD):
        self.sensor = ADC(Pin(adc_pin, Pin.IN))
        self.sensor.atten(ADC.ATTN_11DB)  # Configura a atenuação para ler o valor completo de 0-3.3V
        self.threshold = threshold

    def is_flame_detected(self):
        return self.sensor.read() < self.threshold  # Verifica se o valor lido é menor que o limiar
    