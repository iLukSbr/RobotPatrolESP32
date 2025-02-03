# Passive buzzer KY-006

from machine import Pin, PWM
import utime

class KY006:
    PIN = 13
    
    PATTERNS = {
        'flame': [(300, 500)],  # "flame"
        'co2': [(800, 200), (300, 200), (1000, 200), (1400, 200), (900, 200)],  # "car-bon di-ox-ide"
        'nh3': [(600, 300), (700, 300), (600, 300), (500, 300)]  # "am-mo-ni-a"
    }
    
    def __init__(self, pwm_pin=PIN):
        self.pwm_pin = pwm_pin
        self.pwm = PWM(Pin(self.pwm_pin, Pin.OUT), freq=1)
        
    def sound_alarm(self, alarm_type):
        try:
            print(f"Danger alarm activated: {alarm_type}")            
            if alarm_type in self.PATTERNS:
                pattern = self.PATTERNS[alarm_type]
                for freq, duration in pattern:
                    # print(f"Alarm {alarm_type} with frequency {freq} Hz for {duration} ms")
                    self.pwm.freq(freq)
                    self.pwm.duty_u16(32767)
                    utime.sleep_ms(duration)
                    self.pwm.duty_u16(0)
                    utime.sleep_ms(100)  # Short pause between syllables
                self.pwm.freq(1)  # Volta ao estado inicial
                # print(f"Completed alarm for {alarm_type}")
            else:
                raise ValueError("Invalid alarm type")

        except Exception as e:
            print(f"An error occurred in sound_alarm: {e}")
