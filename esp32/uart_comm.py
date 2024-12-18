from machine import UART, Pin
import json

class UARTComm:
    TX_PIN = 17
    RX_PIN = 16
    BAUD_RATE = 115200
    UART_NUM = 1
    TIMEOUT = 1000
        
    def __init__(self, tx_pin=Pin(TX_PIN), rx_pin=Pin(RX_PIN), baudrate=BAUD_RATE, uart_num=UART_NUM, timeout=1000):
        try:
            self.uart = UART(uart_num, baudrate=baudrate, tx=tx_pin, rx=rx_pin, timeout=timeout)
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

    def read_serial(self):
        message = self.uart.readline()
        if message is not None:
            message = message.decode('utf-8').strip()
            print(f"Received serial message: {message}")
        return message