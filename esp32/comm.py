from machine import UART, Pin
import json

class UARTComm:
    def __init__(self, tx_pin=17, rx_pin=16, baudrate=115200, uart_num=1, timeout=1000):
        try:
            self.uart = UART(uart_num, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin), timeout=timeout)
            self.json_message = {}
            # print(f"UART initialized on TX pin {tx_pin} and RX pin {rx_pin}")
        except Exception as e:
            print(f"Failed to initialize UART: {e}")

    def print_json(self):
        print(self.json_message)

    def send_json(self):
        try:
            message = json.dumps(self.json_message)
            self.uart.write(message.encode('utf-8') + b'\n')
            print(f"Sent message: {message}")
            self.json_message = {}
        except Exception as e:
            print(f"Failed to send JSON message: {e}")

    def add_data(self, key, value):
        self.json_message[key] = value

# Exemplo de uso
if __name__ == "__main__":
    comm = UARTComm()
    comm.add_data("temperature", 25.5)
    comm.add_data("humidity", 60)
    comm.print_json()
    comm.send_json()