# Passive buzzer KY-006

from machine import Pin, PWM
import time

class KY006:
    PIN = 13
    
    PATTERNS = {
        'flame': [(300, 500)],  # "flame"
        'co2': [(800, 200), (300, 200), (1000, 200), (1400, 200), (900, 200)],  # "car-bon di-ox-ide"
        'nh3': [(600, 300), (700, 300), (600, 300), (500, 300)]  # "am-mo-ni-a"
    }
    
    def __init__(self, pin=PIN):
        self.pwm_pin = pin
        self.pwm = PWM(Pin(self.pwm_pin, Pin.OUT), freq=1)
        self.pwm.duty_u16(0)
        
    def sound_alarm(self, alarm_type):
        try:
            print(f"Danger alarm activated: {alarm_type}")
            if alarm_type in self.PATTERNS:
                pattern = self.PATTERNS[alarm_type]
                for freq, duration in pattern:
                    # print(f"Alarm {alarm_type} with frequency {freq} Hz for {duration} ms")
                    self.pwm.freq(freq)
                    self.pwm.duty_u16(32767)
                    time.sleep(duration / 1000)
                    self.pwm.duty_u16(0)
                    time.sleep(0.000001)  # Short pause between syllables
                self.pwm.freq(1)  # Back to idle frequency
                # print(f"Completed alarm for {alarm_type}")
            else:
                raise ValueError("Invalid alarm type")

        except Exception as e:
            print(f"An error occurred in sound_alarm: {e}")
