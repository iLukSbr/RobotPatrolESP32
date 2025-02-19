from machine import Pin, time_pulse_us
import time

class HCSR04:
    def __init__(self, trig_pin, echo_pin):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.trig.off()
        
    def calculate_median(self, values):
        sorted_values = sorted(values)
        n = len(sorted_values)
        middle = n // 2

        if n % 2 == 0:
            return (sorted_values[middle - 1] + sorted_values[middle]) / 2
        else:
            return sorted_values[middle]

    def measure_median(self, readings=5, timeout=30000):
        distances = []

        for _ in range(readings):
            self.trig.off()
            time.sleep(0.000002)
            self.trig.on()
            time.sleep(0.00001)
            self.trig.off()

            try:
                duration = time_pulse_us(self.echo, 1, timeout)
                if duration < 0:
                    continue
                distance = duration * 0.0343 / 2
                if distance < 0:
                    continue
                distances.append(distance)
            except OSError as e:
                print(f"Error: {e}")

            time.sleep(0.05)

        if len(distances) < 3:
            return -1

        median_distance = self.calculate_median(distances)
        # print(f"Median distance: {median_distance} cm")
        return median_distance
