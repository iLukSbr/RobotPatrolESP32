# UART string sender/receiver

from machine import UART, Pin

class UARTComm:
    TX_PIN = 17
    RX_PIN = 16
    BAUD_RATE = 115200
    UART_NUM = 1
    TIMEOUT = 1000
        
    def __init__(self, tx_pin=TX_PIN, rx_pin=RX_PIN, baudrate=BAUD_RATE, uart_num=UART_NUM, timeout=1000):
        try:
            self.uart = UART(uart_num, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin), timeout=timeout)
            print(f"UART initialized on TX pin {tx_pin} and RX pin {rx_pin}")
        except Exception as e:
            print(f"Failed to initialize UART: {e}")

    def send_message(self, message):
        try:
            self.uart.write(message.encode('utf-8') + b'\n')
            print(f"Sent message: {message}")
        except Exception as e:
            print(f"Failed to send message: {e}")

    def read_serial(self):
        message = self.uart.readline()
        if message is not None:
            message = message.decode('utf-8').strip()
            print(f"Received serial message: {message}")
        return message
