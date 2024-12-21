# https://github.com/jackw01/lsm303-python

import struct
import time
from machine import I2C

class LSM303:
    'LSM303 3-axis accelerometer/magnetometer'

    LSM303_ADDRESS_ACCEL = 0x19  # 0011001x
    LSM303_REGISTER_ACCEL_CTRL_REG1_A = 0x20
    LSM303_REGISTER_ACCEL_CTRL_REG4_A = 0x23
    LSM303_REGISTER_ACCEL_OUT_X_L_A = 0x28
    LSM303_REGISTER_ACCEL_OUT_X_H_A = 0x29
    LSM303_REGISTER_ACCEL_OUT_Y_L_A = 0x2A
    LSM303_REGISTER_ACCEL_OUT_Y_H_A = 0x2B
    LSM303_REGISTER_ACCEL_OUT_Z_L_A = 0x2C
    LSM303_REGISTER_ACCEL_OUT_Z_H_A = 0x2D

    LSM303_ADDRESS_MAG = 0x1E  # 0011110x
    LSM303_REGISTER_MAG_CRA_REG_M = 0x00
    LSM303_REGISTER_MAG_CRB_REG_M = 0x01
    LSM303_REGISTER_MAG_MR_REG_M = 0x02
    LSM303_REGISTER_MAG_OUT_X_H_M = 0x03
    LSM303_REGISTER_MAG_OUT_X_L_M = 0x04
    LSM303_REGISTER_MAG_OUT_Z_H_M = 0x05
    LSM303_REGISTER_MAG_OUT_Z_L_M = 0x06
    LSM303_REGISTER_MAG_OUT_Y_H_M = 0x07
    LSM303_REGISTER_MAG_OUT_Y_L_M = 0x08

    MAG_GAIN_1_3 = 0x20  # +/- 1.3
    MAG_GAIN_1_9 = 0x40  # +/- 1.9
    MAG_GAIN_2_5 = 0x60  # +/- 2.5
    MAG_GAIN_4_0 = 0x80  # +/- 4.0
    MAG_GAIN_4_7 = 0xA0  # +/- 4.7
    MAG_GAIN_5_6 = 0xC0  # +/- 5.6
    MAG_GAIN_8_1 = 0xE0  # +/- 8.1

    ACCEL_MS2_PER_LSB = 0.00980665  # meters/second^2 per least significant bit
    GAUSS_TO_MICROTESLA = 100.0

    def __init__(self, i2c: I2C, hires=True):
        'Initialize the sensor'
        self._bus = i2c

        # Enable the accelerometer - all 3 channels
        self._bus.writeto_mem(self.LSM303_ADDRESS_ACCEL,
                              self.LSM303_REGISTER_ACCEL_CTRL_REG1_A,
                              bytearray([0b01000111]))

        # Select hi-res (12-bit) or low-res (10-bit) output mode.
        # Low-res mode uses less power and sustains a higher update rate,
        # output is padded to compatible 12-bit units.
        if hires:
            self._bus.writeto_mem(self.LSM303_ADDRESS_ACCEL,
                                  self.LSM303_REGISTER_ACCEL_CTRL_REG4_A,
                                  bytearray([0b00001000]))
        else:
            self._bus.writeto_mem(self.LSM303_ADDRESS_ACCEL,
                                  self.LSM303_REGISTER_ACCEL_CTRL_REG4_A,
                                  bytearray([0b00000000]))

        # Enable the magnetometer
        self._bus.writeto_mem(self.LSM303_ADDRESS_MAG,
                              self.LSM303_REGISTER_MAG_MR_REG_M,
                              bytearray([0b00000000]))

        self.set_mag_gain(self.MAG_GAIN_1_3)

    def read_accel(self):
        'Read raw acceleration in meters/second squared'
        # Read as signed 12-bit little endian values
        accel_bytes = self._bus.readfrom_mem(self.LSM303_ADDRESS_ACCEL,
                                             self.LSM303_REGISTER_ACCEL_OUT_X_L_A | 0x80,
                                             6)
        accel_raw = struct.unpack('<hhh', accel_bytes)

        return (
            (accel_raw[0] >> 4) * self.ACCEL_MS2_PER_LSB,
            (accel_raw[1] >> 4) * self.ACCEL_MS2_PER_LSB,
            (accel_raw[2] >> 4) * self.ACCEL_MS2_PER_LSB
        )

    def set_mag_gain(self, gain):
        'Set magnetometer gain'
        self._gain = gain
        if gain == self.MAG_GAIN_1_3:
            self._lsb_per_gauss_xy = 1100
            self._lsb_per_gauss_z = 980
        elif gain == self.MAG_GAIN_1_9:
            self._lsb_per_gauss_xy = 855
            self._lsb_per_gauss_z = 760
        elif gain == self.MAG_GAIN_2_5:
            self._lsb_per_gauss_xy = 670
            self._lsb_per_gauss_z = 600
        elif gain == self.MAG_GAIN_4_0:
            self._lsb_per_gauss_xy = 450
            self._lsb_per_gauss_z = 400
        elif gain == self.MAG_GAIN_4_7:
            self._lsb_per_gauss_xy = 400
            self._lsb_per_gauss_z = 355
        elif gain == self.MAG_GAIN_5_6:
            self._lsb_per_gauss_xy = 330
            self._lsb_per_gauss_z = 295
        elif gain == self.MAG_GAIN_8_1:
            self._lsb_per_gauss_xy = 230
            self._lsb_per_gauss_z = 205

        self._bus.writeto_mem(self.LSM303_ADDRESS_MAG,
                              self.LSM303_REGISTER_MAG_CRB_REG_M,
                              bytearray([self._gain]))

    def set_mag_rate(self, rate):
        'Set magnetometer rate'
        self._bus.writeto_mem(self.LSM303_ADDRESS_MAG,
                              self.LSM303_REGISTER_MAG_CRA_REG_M,
                              bytearray([(rate & 0x07) << 2]))

    def read_mag(self):
        'Read raw magnetic field in microtesla'
        # Read as signed 16-bit big endian values
        mag_bytes = self._bus.readfrom_mem(self.LSM303_ADDRESS_MAG,
                                           self.LSM303_REGISTER_MAG_OUT_X_H_M,
                                           6)
        mag_raw = struct.unpack('>hhh', mag_bytes)

        return (
            mag_raw[0] / self._lsb_per_gauss_xy * self.GAUSS_TO_MICROTESLA,
            mag_raw[2] / self._lsb_per_gauss_xy * self.GAUSS_TO_MICROTESLA,
            mag_raw[1] / self._lsb_per_gauss_z * self.GAUSS_TO_MICROTESLA
        )
        