# https://github.com/chrisb2/pyb_ina219

from ina219 import INA219
from ina219 import DeviceRangeError
from machine import I2C

I2C_INTERFACE_NO = 2
SHUNT_OHMS = 0.1  # Check value of shunt used with your INA219
MAX_EXPECTED_AMPS = 0.2

ina = INA219(SHUNT_OHMS, I2C(I2C_INTERFACE_NO), MAX_EXPECTED_AMPS)
ina.configure(ina.RANGE_16V)

print("Bus Voltage: %.3f V" % ina.voltage())
try:
    print("Bus Current: %.3f mA" % ina.current())
    print("Power: %.3f mW" % ina.power())
    print("Shunt voltage: %.3f mV" % ina.shunt_voltage())
except DeviceRangeError as e:
    # Current out of device range with specified shunt resister
    print e