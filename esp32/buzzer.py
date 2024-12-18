from machine import Pin, PWM
import utime

def sound_alarm(alarm_type):
    try:
        buzzer = PWM(Pin(13), freq=1)
        print(f"Danger alarm activated: {alarm_type}")
        patterns = {
            'flame': [(300, 500)],  # "flame"
            'co2': [(800, 200), (300, 200), (1000, 200), (1400, 200), (900, 200)],  # "car-bon di-ox-ide"
            'nh3': [(600, 300), (700, 300), (600, 300), (500, 300)]  # "am-mo-ni-a"
        }
        
        if alarm_type in patterns:
            pattern = patterns[alarm_type]
            for freq, duration in pattern:
                # print(f"Alarm {alarm_type} with frequency {freq} Hz for {duration} ms")
                buzzer.freq(freq)
                buzzer.duty_u16(32767)
                utime.sleep_ms(duration)
                buzzer.duty_u16(0)
                utime.sleep_ms(100)  # Short pause between syllables
            buzzer.deinit()  # Desativa o PWM após o alarme
            # print(f"Completed alarm for {alarm_type}")
        else:
            raise ValueError("Invalid alarm type")
        
        # Reconfigura o pino 13 como saída digital com valor baixo
        pin13 = Pin(13, Pin.OUT)
        pin13.value(0)
    except Exception as e:
        print(f"An error occurred in sound_alarm: {e}")
