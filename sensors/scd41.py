# Carbon dioxide CO2 sensor SCD41
# https://github.com/CDFER/scd4x-CO2

import time
from machine import I2C

class SCD41:
    SCD41_I2C_ADDRESS = 0x62
    I2C_RETRY_COUNT = 1000
    I2C_RETRY_DELAY_uS = 1
    CO2_OFFSET = -140
    co2 = 0
    temperature = 0
    humidity = 0
    
    def __init__(self, i2c: I2C, address: int = SCD41_I2C_ADDRESS):
        self.i2c = i2c
        self.address = address
        self._error = 0
        self._settingsChanged = False
        self._isValid = False
        self.begin()
        self.set_calibration_mode(False)
        self.save_settings()
        self.start_periodic_measurement()
        # print(f"SCD41 initialized with address {self.address}")

    def begin(self) -> int:
        try:
            # Iniciar transmissão I2C para o endereço do sensor
            self.i2c.writeto(self.address, b'')
            # print("SCD41 begin successful")
            return 0
        except OSError as e:
            self._error = e.args[0]
            print(f"SCD41 begin failed with error: {self.get_error_text(self._error)}")
            return self._error

    def is_connected(self) -> bool:
        # print("Checking if SCD41 is connected...")
        self.stop_periodic_measurement()
        time.sleep_us(1)

        if self._error != 0:
            print(f"SCD4x returned endTransmission error {self._error}")
            return False

        self._command_sequence(0x3639)
        time.sleep_us(1)

        data = self._read_bytes(3)
        if data != b'\x00\x00\x81':
            print(f"SCD4x returned selfTest Error: {data[0]:02X} {data[1]:02X} with CRC of {data[2]:02X}")
            return False

        print("SCD4x Connected Correctly")
        return True

    def start_periodic_measurement(self) -> int:
        # print("Starting periodic measurement...")
        self._command_sequence(0x21B1)
        if self._error != 0:
            print(f"Periodic measurement started with error: {self.get_error_text(self._error)}")
        return self._error

    def stop_periodic_measurement(self) -> int:
        # print("Stopping periodic measurement...")
        self._command_sequence(0x3F86)
        if self._error != 0:
            print(f"Periodic measurement stopped with error: {self.get_error_text(self._error)}")
        return self._error

    def read_measurement(self, pressure=None) -> tuple:
        if not self.is_data_ready():
            return self.co2, self.temperature, self.humidity
        # print("Reading measurement...")
        self._write_bytes(0xEC05, b'')
        data = self._read_bytes(9)

        if len(data) == 9:
            co2 = ((data[0] << 8) | data[1]) + self.CO2_OFFSET
            temperature = -45 + 175 * ((data[3] << 8) | data[4]) / 65536
            humidity = 100 * ((data[6] << 8) | data[7]) / 65536

            if not self._in_range(co2, 40000, 0) or not self._in_range(temperature, 60, -10) or not self._in_range(humidity, 100, 0):
                print(f"Measurement out of range: {co2},{temperature},{humidity}")
                self._error = 7
                return self.co2, self.temperature, self.humidity

            self.co2 = co2
            self.temperature = temperature
            self.humidity = humidity
            
            if pressure is not None:
                self.set_ambient_pressure(pressure)
                
            # print(f"Measurement read: CO2={co2}, Temperature={temperature}, Humidity={humidity}")
            return self.co2, self.temperature, self.humidity
        else:
            self._error = 6
            print(f"Failed to read measurement, error: {self.get_error_text(self._error)}")
            return self.co2, self.temperature, self.humidity

    def is_data_ready(self) -> bool:
        # print("Checking if data is ready...")
        ready = (self._read_sequence(0xE4B8) & 0x07FF) != 0x0000
        # print(f"Data ready: {ready}")
        return ready

    def set_calibration_mode(self, enable_auto_calibration: bool) -> int:
        # print(f"Setting calibration mode to {'auto' if enable_auto_calibration else 'manual'}...")
        self.stop_periodic_measurement()
        time.sleep_us(1)

        if enable_auto_calibration != self.get_calibration_mode():
            if enable_auto_calibration:
                self._write_sequence(0x2416, 0x0001, 0xB0)
            else:
                self._write_sequence(0x2416, 0x0000, 0x81)
            self._settingsChanged = True

        if self._error != 0:
            print(f"Calibration mode set with error: {self.get_error_text(self._error)}")
        return self._error

    def get_calibration_mode(self) -> bool:
        mode = bool(self._read_sequence(0x2313))
        # print(f"Calibration mode is {'auto' if mode else 'manual'}")
        return mode

    def reset_eeprom(self) -> int:
        # print("Resetting EEPROM...")
        self.stop_periodic_measurement()
        time.sleep_us(1)

        self._command_sequence(0x3632)
        time.sleep_us(1)

        if self._error != 0:
            print(f"EEPROM reset failed with error: {self.get_error_text(self._error)}")
        return self._error

    def save_settings(self) -> int:
        if self._settingsChanged:
            # print("Saving settings to EEPROM...")
            self._command_sequence(0x3615)
            # print("Settings Saved to EEPROM")
            time.sleep_us(1)
        else:
            print("Settings not changed, save command not sent")

        return self._error

    def get_error_text(self, error_code: int) -> str:
        error_texts = {
            0: "Success",
            1: "I2C data too long to fit in transmit buffer",
            2: "I2C received NACK on transmit of address",
            3: "I2C received NACK on transmit of data",
            4: "I2C other error",
            5: "I2C timeout",
            6: "bytesReceived != bytesRequested",
            7: "Measurement out of range",
            19: "No such device"
        }
        return error_texts.get(error_code, "Unknown error")

    def _in_range(self, value: float, max_value: float, min_value: float) -> bool:
        return min_value < value <= max_value

    def _command_sequence(self, register_address: int):
        # print(f"Sending command sequence to register {register_address:04X}")
        self._write_bytes(register_address, b'')

    def _read_sequence(self, register_address: int) -> int:
        # print(f"Reading sequence from register {register_address:04X}")
        data = self._read_bytes(3)
        if len(data) == 3:
            result = (data[0] << 8) | data[1]
            # print(f"Read sequence result: {result:04X}")
            return result
        else:
            print("Failed to read sequence")
            return 0

    def _write_sequence(self, register_address: int, value: int, checksum: int):
        # print(f"Writing sequence to register {register_address:04X} with value {value:04X} and checksum {checksum:02X}")
        self._write_bytes(register_address, bytes([value >> 8, value & 0xFF, checksum]))

    def _write_bytes(self, register_address: int, data: bytes):
        # print(f"Writing bytes to register {register_address:04X}: {data}")
        last_error = None
        for attempt in range(self.I2C_RETRY_COUNT):
            try:
                self.i2c.writeto(self.address, bytes([register_address >> 8, register_address & 0xFF]) + data)
                self._error = 0  # Success
                return
            except OSError as e:
                last_error = e
                last_error_code = e.args[0]
                time.sleep_us(self.I2C_RETRY_DELAY_uS)
        self._error = last_error_code
        print(f"Failed to write to register {register_address:04X} after {self.I2C_RETRY_COUNT} attempts with error: {self.get_error_text(self._error)}")

    def _read_bytes(self, num_bytes: int) -> bytes:
        # print(f"Reading {num_bytes} bytes from address {self.address:02X}")
        last_error = None
        for attempt in range(self.I2C_RETRY_COUNT):
            try:
                data = self.i2c.readfrom(self.address, num_bytes)
                # print(f"Read bytes: {data}")
                self._error = 0  # Success
                return data
            except OSError as e:
                last_error = e
                last_error_code = e.args[0]
                time.sleep_us(self.I2C_RETRY_DELAY_uS)
        self._error = last_error_code
        print(f"Failed to read {num_bytes} bytes from address {self.address:02X} after {self.I2C_RETRY_COUNT} attempts with error: {self.get_error_text(self._error)}")
        return b''
    
    def set_ambient_pressure(self, pressure: int):
        if pressure < 0 or pressure > 1200:
            raise ValueError("Pressure must be between 0 and 1200 hPa")
        self._write_bytes(0xE000, bytes([pressure >> 8, pressure & 0xFF]))
        if self._error != 0:
            print(f"Setting ambient pressure failed with error: {self.get_error_text(self._error)}")
        return self._error