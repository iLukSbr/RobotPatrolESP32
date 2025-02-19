from machine import UART, Pin
import time

def uart_listener_writer(tx_pin, rx_pin, baudrate, timeout=5000):
    uart = UART(1, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin), timeout=timeout, parity=0, stop=2)
    print(f"Listening on TX pin {tx_pin} and RX pin {rx_pin} at {baudrate} baudrate.")
    
    buffer = ""
    start_time = time.ticks_ms()
    
    while True:
        try:
            if uart.any():
                data = uart.read()
                if data:
                    buffer += data.decode('utf-8')
                    if '\n' in buffer:
                        lines = buffer.split('\n')
                        for line in lines[:-1]:
                            line = line.strip()
                            print(f"Received: {line}")
                            # Echo the received data back
                            uart.write(line.encode('utf-8') + b'\n')
                            print(f"Sent: {line}")
                        buffer = lines[-1]
                start_time = time.ticks_ms()  # Reset the timeout timer
            if time.ticks_ms() - start_time > timeout:
                if buffer:
                    print(f"Received partial message: {buffer.strip()}")
                buffer = ""  # Clear the buffer after timeout
                start_time = time.ticks_ms()  # Reset the timeout timer
            time.sleep(0.1)
        except Exception as e:
            print(f"Failed to read serial: {e}")
            uart.write("{\"error\": \"Failed to read serial\"}")
            pass

if __name__ == "__main__":
    uart_listener_writer(tx_pin=0, rx_pin=1, baudrate=9600)
    