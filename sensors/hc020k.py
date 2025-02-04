from machine import Pin, Timer
import time

class HC020K:
    PULSES_PER_REVOLUTION = 20  # Number of pulses per revolution
    WHEEL_DIAMETER_CM = 6.77 # Diameter of the wheel in cm
    
    def __init__(self, pin, pulses_per_revolution=PULSES_PER_REVOLUTION, wheel_diameter_cm=WHEEL_DIAMETER_CM):
        self.pin = Pin(pin, Pin.IN)
        self.slots = pulses_per_revolution
        self.wheel_diameter = wheel_diameter_cm
        self.pulse_count = 0
        self.last_time = time.ticks_ms()
        self.speed_rps = 0
        self.distance_traveled_cm = 0

        # Set up the interrupt on the pin
        self.pin.irq(trigger=Pin.IRQ_RISING, handler=self._pulse_handler)

        # Set up a timer to calculate speed periodically
        self.timer = Timer(-1)
        self.timer.init(period=1000, mode=Timer.PERIODIC, callback=self._calculate_speed)

    def _pulse_handler(self, pin):
        self.pulse_count += 1

    def _calculate_speed(self, timer):
        current_time = time.ticks_ms()
        elapsed_time = time.ticks_diff(current_time, self.last_time) / 1000  # Convert to seconds
        self.last_time = current_time

        # Calculate speed in revolutions per second (RPS)
        self.speed_rps = (self.pulse_count / self.slots) / elapsed_time
        self.pulse_count = 0

        # Calculate distance traveled in cm
        circumference_cm = self.wheel_diameter * 3.14159
        self.distance_traveled_cm += self.speed_rps * circumference_cm * elapsed_time

    def get_speed_cmps(self):
        # Convert speed from RPS to km/h
        circumference_cm = self.wheel_diameter * 3.14159
        speed_cm_per_sec = self.speed_rps * circumference_cm
        return speed_cm_per_sec
    
    def get_distance_traveled_m(self):
        return self.distance_traveled_cm / 100
