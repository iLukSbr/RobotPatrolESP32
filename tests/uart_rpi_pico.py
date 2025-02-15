from machine import UART, Pin
import time

def uart_listener_writer(tx_pin, rx_pin, baudrate):
    uart = UART(0, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin))
    print(f"Listening on TX pin {tx_pin} and RX pin {rx_pin} at {baudrate} baudrate.")
    
    while True:
        if uart.any():
            data = uart.read().decode('utf-8').rstrip()
            print(f"Received: {data}")
            # Echo the received data back
            uart.write(data.encode('utf-8'))
            print(f"Sent: {data}")
        time.sleep(1)

if __name__ == "__main__":
    uart_listener_writer(tx_pin=0, rx_pin=1, baudrate=115200)