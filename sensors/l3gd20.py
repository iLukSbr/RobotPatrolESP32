# Gyroscope L3GD20
# https://github.com/adafruit/Adafruit_CircuitPython_L3GD20
# https://github.com/jackw01/l3gd20-python

from math import radians
from struct import unpack
from micropython import const
from machine import I2C
import time

class L3GD20:
    """
    Driver for the L3GD20 3-axis Gyroscope sensor.

    :param int rng: a range value one of:

                    * :const:`RANGE_250DPS`
                    * :const:`RANGE_500DPS`
                    * :const:`RANGE_2000DPS`

                    Defaults to :const:`RANGE_250DPS`

    :param int rate: a rate value one of

                    * :const:`L3DS20_RATE_100HZ`
                    * :const:`L3DS20_RATE_200HZ`
                    * :const:`L3DS20_RATE_400HZ`
                    * :const:`L3DS20_RATE_800HZ`

                    Defaults to :const:`L3DS20_RATE_100HZ`
    """

    L3GD20_ADDRESS = const(0x69)
    L3GD20_REGISTER_WHO_AM_I = const(0x0F)
    L3GD20_REGISTER_CTRL_REG1 = const(0x20)
    L3GD20_REGISTER_CTRL_REG2 = const(0x21)
    L3GD20_REGISTER_CTRL_REG3 = const(0x22)
    L3GD20_REGISTER_CTRL_REG4 = const(0x23)
    L3GD20_REGISTER_CTRL_REG5 = const(0x24)
    L3GD20_REGISTER_REFERENCE = const(0x25)
    L3GD20_REGISTER_OUT_TEMP = const(0x26)
    L3GD20_REGISTER_STATUS_REG = const(0x27)
    L3GD20_REGISTER_OUT_X_L = const(0x28)
    L3GD20_REGISTER_OUT_X_H = const(0x29)
    L3GD20_REGISTER_OUT_Y_L = const(0x2A)
    L3GD20_REGISTER_OUT_Y_H = const(0x2B)
    L3GD20_REGISTER_OUT_Z_L = const(0x2C)
    L3GD20_REGISTER_OUT_Z_H = const(0x2D)
    L3GD20_REGISTER_FIFO_CTRL_REG = const(0x2E)
    L3GD20_REGISTER_FIFO_SRC_REG = const(0x2F)
    L3GD20_REGISTER_INT1_CFG = const(0x30)
    L3GD20_REGISTER_INT1_SRC = const(0x31)
    L3GD20_REGISTER_TSH_XH = const(0x32)
    L3GD20_REGISTER_TSH_XL = const(0x33)
    L3GD20_REGISTER_TSH_YH = const(0x34)
    L3GD20_REGISTER_TSH_YL = const(0x35)
    L3GD20_REGISTER_TSH_ZH = const(0x36)
    L3GD20_REGISTER_TSH_ZL = const(0x37)
    L3GD20_REGISTER_INT1_DURATION = const(0x38)

    RANGE_250DPS = const(0x00)
    RANGE_500DPS = const(0x10)
    RANGE_2000DPS = const(0x20)

    L3GD20_DPS_PER_LSB = {
        RANGE_250DPS: 0.00875,
        RANGE_500DPS: 0.0175,
        RANGE_2000DPS: 0.07,
    }

    L3DS20_RATE_100HZ = const(0x00)
    L3DS20_RATE_200HZ = const(0x40)
    L3DS20_RATE_400HZ = const(0x80)
    L3DS20_RATE_800HZ = const(0xC0)

    def __init__(self, i2c: I2C, address: int = L3GD20_ADDRESS, rng: int = RANGE_250DPS, rate: int = L3DS20_RATE_100HZ) -> None:
        self.i2c = i2c
        self.address = address

        if rng not in (self.RANGE_250DPS, self.RANGE_500DPS, self.RANGE_2000DPS):
            raise ValueError("Range value must be one of RANGE_250DPS, RANGE_500DPS, or RANGE_2000DPS")

        self.set_range(rng)
        self.write_register(self.L3GD20_REGISTER_CTRL_REG1, rate | 0x0F)

    def set_range(self, new_range: int) -> None:
        'Set range'
        self._range = new_range
        self._dps_per_lsb = self.L3GD20_DPS_PER_LSB[self._range]
        self.write_register(self.L3GD20_REGISTER_CTRL_REG4, self._range)

    def write_register(self, register: int, value: int) -> None:
        """
        Update a register with a byte value

        :param int register: which device register to write
        :param value: a byte to write
        """
        self.i2c.writeto_mem(self.address, register, bytes([value]))

    def read_register(self, register: int) -> int:
        """
        Returns a byte value from a register

        :param register: the register to read a byte
        """
        return self.i2c.readfrom_mem(self.address, register, 1)[0]

    def read(self) -> Tuple[float, float, float]:
        'Read raw angular velocity values in degrees/second'
        buffer = self.i2c.readfrom_mem(self.address, self.L3GD20_REGISTER_OUT_X_L | 0x80, 6)
        gyro_raw = unpack('<hhh', buffer)
        return (
            gyro_raw[0] * self._dps_per_lsb,
            gyro_raw[1] * self._dps_per_lsb,
            gyro_raw[2] * self._dps_per_lsb,
        )

    @property
    def gyro(self) -> Tuple[float, float, float]:
        """
        x, y, z angular momentum tuple floats, rescaled appropriately for
        range selected in rad/s
        """
        raw = self.read()
        return tuple(radians(v) for v in raw)

    def read_temperature(self) -> int:
        'Read temperature'
        return self.read_register(self.L3GD20_REGISTER_OUT_TEMP)

    def read_status(self) -> int:
        'Read status register'
        return self.read_register(self.L3GD20_REGISTER_STATUS_REG)

    def read_fifo_src(self) -> int:
        'Read FIFO source register'
        return self.read_register(self.L3GD20_REGISTER_FIFO_SRC_REG)

    def read_int1_src(self) -> int:
        'Read INT1 source register'
        return self.read_register(self.L3GD20_REGISTER_INT1_SRC)

    def set_fifo_ctrl(self, value: int) -> None:
        'Set FIFO control register'
        self.write_register(self.L3GD20_REGISTER_FIFO_CTRL_REG, value)

    def set_int1_cfg(self, value: int) -> None:
        'Set INT1 configuration register'
        self.write_register(self.L3GD20_REGISTER_INT1_CFG, value)

    def set_reference(self, value: int) -> None:
        'Set reference register'
        self.write_register(self.L3GD20_REGISTER_REFERENCE, value)

    def set_threshold_x(self, high: int, low: int) -> None:
        'Set threshold for X axis'
        self.write_register(self.L3GD20_REGISTER_TSH_XH, high)
        self.write_register(self.L3GD20_REGISTER_TSH_XL, low)

    def set_threshold_y(self, high: int, low: int) -> None:
        'Set threshold for Y axis'
        self.write_register(self.L3GD20_REGISTER_TSH_YH, high)
        self.write_register(self.L3GD20_REGISTER_TSH_YL, low)

    def set_threshold_z(self, high: int, low: int) -> None:
        'Set threshold for Z axis'
        self.write_register(self.L3GD20_REGISTER_TSH_ZH, high)
        self.write_register(self.L3GD20_REGISTER_TSH_ZL, low)

    def set_int1_duration(self, value: int) -> None:
        'Set INT1 duration register'
        self.write_register(self.L3GD20_REGISTER_INT1_DURATION, value)
