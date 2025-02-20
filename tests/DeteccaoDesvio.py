from machine import Pin, time_pulse_us, UART
import time

# Definir os pinos dos sensores
TRIG1 = Pin(4, Pin.OUT)
ECHO1 = Pin(5, Pin.IN)

TRIG2 = Pin(18, Pin.OUT)
ECHO2 = Pin(19, Pin.IN)

TRIG3 = Pin(21, Pin.OUT)
ECHO3 = Pin(22, Pin.IN)

# Configuração do UART para comunicação com a Raspberry Pi
uart = UART(1, baudrate=115200, tx=16, rx=17)  # Ajuste os pinos tx e rx conforme a sua conexão

time.sleep(45)
print("Start")

# Função para medir a distância com o sensor HCSR04
def medir_distancia(trig, echo):
    # Enviar pulso de 10us no TRIG
    trig.off()
    time.sleep_us(2)
    trig.on()
    time.sleep_us(10)
    trig.off()
    
    # Medir duração do pulso no ECHO
    duracao = time_pulse_us(echo, 1, 30000)  # Timeout de 30ms
    
    # Se der timeout, retorna -1
    if duracao < 0:
        return -1
    
    # Calcular a distância (em cm)
    distancia = (duracao / 2) / 29.1
    return distancia

# Loop principal para testar os sensores
while True:
    # Medir distâncias
    
#     uart.write("Teste desvio!\n")
    
    distancia1 = medir_distancia(TRIG1, ECHO1)
    distancia2 = medir_distancia(TRIG2, ECHO2)
    distancia3 = medir_distancia(TRIG3, ECHO3)
    
    # Exibir resultados no terminal
    print("Sensor 1: {:.2f} cm".format(distancia1) if distancia1 >= 0 else "Sensor 1: Fora de alcance")
    print("Sensor 2: {:.2f} cm".format(distancia2) if distancia2 >= 0 else "Sensor 2: Fora de alcance")
    print("Sensor 3: {:.2f} cm".format(distancia3) if distancia3 >= 0 else "Sensor 3: Fora de alcance")
    print("-----------------------------")
    
    if distancia2 < 30:
        print("Desviando.")
        uart.write("1\n")
    else:
        uart.write("0\n")
    
    # Aguardar 1 segundo antes da próxima leitura
    time.sleep(0.05)

    


