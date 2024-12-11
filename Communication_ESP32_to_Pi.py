import serial
import time

esp32_serial = serial.Serial(port='/dev/serial0', baudrate=115200, timeout=1)

print("ESP32 iniciado")

while True:
    try:
        # Enviar mensagens para o PI
        esp32_serial.write(b"Ola, Raspberry Pi!\n")
        time.sleep(1)
        esp32_serial.write(b"Aqui eh a ESP32!\n")
        time.sleep(1)
        print("Mensagens enviadas para Pi.")

        # Ler mensagem do PI
        if esp32_serial.in_waiting > 0:
            mensagem = esp32_serial.readline().decode('utf-8').strip()
            print(f"Recebido da Raspberry Pi: {mensagem}")

    except KeyboardInterrupt:
        print("Encerrando comunicação.")
        break

# Fechar a conexão serial ao encerrar
esp32_serial.close()
