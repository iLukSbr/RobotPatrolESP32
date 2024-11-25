import machine
import time

# Initialize the LED pin (assuming the LED is connected to pin 2)
led = machine.Pin(2, machine.Pin.OUT)

# Print "Hello, World!" to the serial monitor
print("Hello, World!")

# Blink the LED
while True:
    led.on()
    time.sleep(1)  # LED on for 1 second
    led.off()
    time.sleep(1)  # LED off for 1 second