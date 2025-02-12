from machine import Pin, time_pulse_us  # type: ignore
import time

TRIG_PIN = Pin(5, Pin.OUT)   # Pino TRIG conectado ao GPIO 5
ECHO_PIN = Pin(18, Pin.IN)   # Pino ECHO conectado ao GPIO 18

def calcular_mediana(valores):
    
    #Calcula a mediana de uma lista de valores.
    
    valores_ordenados = sorted(valores)
    n = len(valores_ordenados)
    meio = n // 2

    if n % 2 == 0:
        return (valores_ordenados[meio - 1] + valores_ordenados[meio]) / 2
    else:
        return valores_ordenados[meio]

def medir_mediana(leituras=5, timeout=38000):
    
    #Mede a distancia e retorna a mediana de um conjunto de leituras.

    distancias = []

    for _ in range(leituras):
        # Gera o pulso TRIG
        TRIG_PIN.off()
        time.sleep_us(2)  # 2 microsegundos
        TRIG_PIN.on()
        time.sleep_us(10)  # 10 microsegundos
        TRIG_PIN.off()

        # Mede o tempo do pulso ECHO
        try:
            duracao = time_pulse_us(ECHO_PIN, 1, timeout)  # Tempo em microsegundos
            distancia = duracao * 0.0343 / 2  # Velocidade do som (em cm/us)
            distancias.append(distancia)
        except OSError:
            # Timeout: Pulso perdido
            pass

        time.sleep_ms(50)  # Intervalo entre leituras

'''
    #Verifica se ha leituras suficientes para calcular a mediana
    if len(distancias) < 3:
        return None  # Poucas leituras validas

    return calcular_mediana(distancias)
'''
try:
    while True:
        distancia = medir_mediana(5)
        if distancia is not None:
            print(f"Distância (mediana): {distancia:.2f} cm")
        else:
            print("Erro: Nenhuma leitura válida. Objeto fora de alcance ou sinal perdido.")
        time.sleep(0.5)  # Pequeno intervalo entre medições

except KeyboardInterrupt:
    print("Encerrando o programa.")
