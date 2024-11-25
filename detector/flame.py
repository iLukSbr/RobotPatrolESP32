# https://newbiely.com/tutorials/esp32-micropython/esp32-micropython-flame-sensor

from machine import Pin
import utime  # For timing functions

DO_PIN = Pin(13, Pin.IN)  # The ESP32 pin GPIO13 connected to the DO pin of the flame sensor module

while True:
    flame_state = DO_PIN.value()  # Read the digital value from the pin

    if flame_state == 1:
        print("The flame is NOT present => The fire is NOT detected")
    else:
        print("The flame is present => The fire is detected")

    utime.sleep(1)  # Add a small delay to avoid spamming the output
