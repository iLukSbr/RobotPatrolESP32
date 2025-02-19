# UART string sender/receiver

from machine import UART, Pin
import time

class UARTComm:
    TX_PIN = 17
    RX_PIN = 16
    BAUD_RATE = 9600
    UART_NUM = 1
    TIMEOUT = 5000  # Timeout em milissegundos
        
    def __init__(self, tx_pin=TX_PIN, rx_pin=RX_PIN, baudrate=BAUD_RATE, uart_num=UART_NUM, timeout=TIMEOUT, parity=0, stop=2):
        try:
            self.uart = UART(uart_num, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin), timeout=timeout, parity=parity, stop=stop)
            parity_str = "even" if parity == 0 else "odd"
            print(f"UART initialized on TX pin {tx_pin} and RX pin {rx_pin} with {baudrate} baudrate, parity {parity_str}, and {stop} stop bits.")
        except Exception as e:
            print(f"Failed to initialize UART: {e}")

    def send_message(self, message, add_newline=True):
        try:
            if add_newline:
                self.uart.write(message.encode('utf-8') + b'\n')
            else:
                self.uart.write(message.encode('utf-8'))
            print(f"Sent message: {message}")
            time.sleep(0.1)
        except Exception as e:
            print(f"Failed to send message: {e}")

    def read_serial(self):
        buffer = ""
        start_time = time.ticks_ms()
        while True:
            try:
                if self.uart.any():
                    data = self.uart.read()
                    if data:
                        buffer += data.decode('utf-8')
                        if '\n' in buffer:
                            lines = buffer.split('\n')
                            for line in lines[:-1]:
                                line = line.strip()
                                print(f"Received serial message: {line}")
                                return line
                            buffer = lines[-1]
                    start_time = time.ticks_ms()  # Reset the timeout timer
                if time.ticks_ms() - start_time > self.TIMEOUT:
                    if buffer:
                        print(f"Received partial message: {buffer.strip()}")
                    return buffer.strip()
                time.sleep(0.1)
            except Exception as e:
                print(f"Failed to read serial: {e}")
                self.send_message("{\"error\": \"Failed to read serial\"}")
                return None
                