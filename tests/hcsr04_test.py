from machine import Pin, time_pulse_us
import time

class HCSR04:
    def __init__(self, trig_pin, echo_pin):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.trig.off()

    def calcular_mediana(self, valores):
        valores_ordenados = sorted(valores)
        n = len(valores_ordenados)
        meio = n // 2

        if n % 2 == 0:
            return (valores_ordenados[meio - 1] + valores_ordenados[meio]) / 2
        else:
            return valores_ordenados[meio]

    def medir_mediana(self, leituras=5, timeout=38000):
        distancias = []

        for _ in range(leituras):
            self.trig.off()
            time.sleep(0.000002)
            self.trig.on()
            time.sleep(0.00001)
            self.trig.off()

            try:
                duracao = time_pulse_us(self.echo, 1, timeout)
                distancia = duracao * 0.0343 / 2
                distancias.append(distancia)
            except OSError:
                pass

            time.sleep(0.05)

        if len(distancias) < 3:
            return None

        return self.calcular_mediana(distancias)
