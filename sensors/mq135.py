# Ammonia NH3 sensor MQ135
# https://github.com/ncdcommunity/Raspberry_Pi_ADC121C_MQ135_Amonia_Gas_Detection_Sensor_Python_Library
# https://github.com/rubfi/MQ135

import time
from machine import ADC, Pin
import math

class MQ135:
    # MQ135 configuration
    MEASURE_RL = 20.0
    MQ_SAMPLE_TIME = 5
    MEASURED_RO_IN_CLEAN_AIR = 3.7
    NH3_OFFSET = -2.8 # NH3 offset in ppm

    # ESP32 ADC pin
    ADC_PIN = 27
    
    # Load resistance on the board
    RLOAD = 10.0
    # CO2 resistance in clean air
    RZERO = 76.63
    # CO2 parameters for calibration
    PARA = 116.6020682
    PARB = 2.769034857

    # Humidity and temperature correction factors
    CORA = 0.00035
    CORB = 0.02718
    CORC = 1.39538
    CORD = 0.0018
    CORE = -0.003333333
    CORF = -0.001923077
    CORG = 1.130128205

    # CO2 atmospheric concentration for calibration
    ATMOCO2 = 397.13

    def __init__(self, adc_pin=ADC_PIN):
        self.sensor = ADC(Pin(adc_pin, Pin.IN))
        self.sensor.atten(ADC.ATTN_11DB)  # Configures the ADC to read from 0 to 3.3V
        self.raw_adc = 0
        self.rs_air = 0
        self.ratio = 0

    def read_raw_data(self):
        """Reads the raw data from the sensor"""
        self.raw_adc = self.sensor.read()
        return self.raw_adc

    def get_correction_factor(self, temperature, humidity):
        """Calculates the correction factor for temperature and humidity"""
        if temperature < 20:
            return self.CORA * temperature * temperature - self.CORB * temperature + self.CORC - (humidity - 33.) * self.CORD
        return self.CORE * temperature + self.CORF * humidity + self.CORG

    def get_resistance(self):
        """Returns the resistance of the sensor"""
        self.read_raw_data()
        if self.raw_adc <= 1.0:
            return 0
        return (4096. / self.raw_adc - 1.) * self.RLOAD

    def get_corrected_resistance(self, temperature, humidity):
        """Obtains the corrected resistance of the sensor"""
        if self.get_correction_factor(temperature, humidity) <= 0.0:
            return self.get_resistance()
        return self.get_resistance() / self.get_correction_factor(temperature, humidity)

    def measure_Ro(self, temperature, humidity):
        """Calculates the resistance of the sensor in clean air"""
        Measure_Ro = 0.0
        for _ in range(self.MQ_SAMPLE_TIME):
            self.read_raw_data()
            self.rs_air = self.get_corrected_resistance(temperature, humidity)
            Measure_Ro += self.rs_air
            time.sleep_us(1)
        Measure_Ro = Measure_Ro / self.MQ_SAMPLE_TIME
        Measure_Ro = Measure_Ro / self.MEASURED_RO_IN_CLEAN_AIR
        return Measure_Ro

    def measure_Rs(self, temperature, humidity):
        Measure_Rs = 0.0
        for _ in range(self.MQ_SAMPLE_TIME):
            self.read_raw_data()
            self.rs_air = self.get_corrected_resistance(temperature, humidity)
            Measure_Rs += self.rs_air
            time.sleep_us(1)
        Measure_Rs = Measure_Rs / self.MQ_SAMPLE_TIME
        return Measure_Rs

    def measure_ratio(self, temperature, humidity):
        if self.measure_Ro(temperature, humidity) <= 0.0:
            self.ratio = self.measure_Rs(temperature, humidity)
        self.ratio = self.measure_Rs(temperature, humidity) / self.measure_Ro(temperature, humidity)
        # print("Ratio = {:.3f}".format(self.ratio))

    def calculate_ppm_CO2(self, temperature, humidity):
        """Calculates the final concentration of CO2 corrected for temperature/humidity"""
        self.measure_ratio(temperature, humidity)
        a = -0.32
        b = 1.0
        ppm = math.exp(((math.log(self.ratio, 10)) - b) / a)
        return ppm

    def calculate_ppb_NH3(self, temperature, humidity):
        """Calculates the final concentration of NH3 corrected for temperature/humidity"""
        self.measure_ratio(temperature, humidity)
        a = -0.41
        b = 1.0
        ppb = (math.exp(((math.log(self.ratio, 10)) - b) / a) + self.NH3_OFFSET) * 1000
        return ppb

    def get_gas_concentrations(self, temperature, humidity):
        """Obtains the final concentrations of CO2 and NH3 corrected for temperature/humidity"""
        co2_values = []
        nh3_values = []
        for _ in range(20):
            co2_values.append(self.calculate_ppm_CO2(temperature, humidity))
            nh3_values.append(self.calculate_ppb_NH3(temperature, humidity))
            time.sleep_ms(40)  # Small delay between measurements

        co2_values.sort()
        nh3_values.sort()

        median_co2 = co2_values[len(co2_values) // 2]
        median_nh3 = nh3_values[len(nh3_values) // 2]

        return median_co2, median_nh3