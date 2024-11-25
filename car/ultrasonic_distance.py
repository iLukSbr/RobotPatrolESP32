# https://github.com/rsc1975/micropython-hcsr04

from hcsr04 import HCSR04

sensor = HCSR04(trigger_pin=16, echo_pin=0, echo_timeout_us=10000)

try:
    distance = sensor.distance_cm()
    print('Distance:', distance, 'cm')
except OSError as ex:
    print('ERROR getting distance:', ex)
