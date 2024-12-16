from machine import ADC, Pin

FLAME_SENSOR_PIN = 35
FLAME_THRESHOLD = 1000

class FlameSensor:
    def __init__(self, pin_number=FLAME_SENSOR_PIN, threshold=FLAME_THRESHOLD):
        self.sensor = ADC(Pin(pin_number))
        self.sensor.atten(ADC.ATTN_11DB)  # Configura a atenuação para ler o valor completo de 0-3.3V
        self.threshold = threshold

    def is_flame_detected(self):
        return self.sensor.read() < self.threshold  # Verifica se o valor lido é menor que o limiar

# Instância global do sensor de chama
flame_sensor = FlameSensor()

def is_flame_detected():
    return flame_sensor.is_flame_detected()