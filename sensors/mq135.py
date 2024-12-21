# https://github.com/ncdcommunity/Raspberry_Pi_ADC121C_MQ135_Amonia_Gas_Detection_Sensor_Python_Library
# https://github.com/rubfi/MQ135

import utime
from machine import ADC, Pin
import math

class MQ135:
    # Configurações do sensor MQ135
    MEASURE_RL = 20.0
    MQ_SAMPLE_TIME = 5
    MEASURED_RO_IN_CLEAN_AIR = 3.7

    # Pino ADC do ESP32
    ADC_PIN = 34
    
    # A resistência de carga na placa
    RLOAD = 10.0
    # Resistência de calibração no nível de CO2 atmosférico
    RZERO = 76.63
    # Parâmetros para calcular ppm de CO2 a partir da resistência do sensor
    PARA = 116.6020682
    PARB = 2.769034857

    # Parâmetros para modelar a dependência de temperatura e umidade
    CORA = 0.00035
    CORB = 0.02718
    CORC = 1.39538
    CORD = 0.0018
    CORE = -0.003333333
    CORF = -0.001923077
    CORG = 1.130128205

    # Nível de CO2 atmosférico para fins de calibração
    ATMOCO2 = 397.13

    def __init__(self, adc_pin=Pin(ADC_PIN)):
        self.sensor = ADC(adc_pin)
        self.sensor.atten(ADC.ATTN_11DB)  # Configura a atenuação para ler o valor completo de 0-3.3V
        self.raw_adc = 0
        self.rsAir = 0
        self.ratio = 0

    def read_raw_data(self):
        """Lê o valor bruto do ADC"""
        self.raw_adc = self.sensor.read()

    def get_correction_factor(self, temperature, humidity):
        """Calcula o fator de correção para temperatura do ar ambiente e umidade relativa"""
        if temperature < 20:
            return self.CORA * temperature * temperature - self.CORB * temperature + self.CORC - (humidity - 33.) * self.CORD
        return self.CORE * temperature + self.CORF * humidity + self.CORG

    def get_resistance(self):
        """Retorna a resistência do sensor em kOhms"""
        self.read_raw_data()
        if self.raw_adc == 0:
            return -1
        return (4095. / self.raw_adc - 1.) * self.RLOAD

    def get_corrected_resistance(self, temperature, humidity):
        """Obtém a resistência do sensor corrigida para temperatura/umidade"""
        return self.get_resistance() / self.get_correction_factor(temperature, humidity)

    def measure_Ro(self, temperature, humidity):
        """Calcula a razão Rs/Ro a partir da resistência Rs & Ro"""
        Measure_Ro = 0.0
        for _ in range(self.MQ_SAMPLE_TIME):
            self.read_raw_data()
            self.rsAir = self.get_corrected_resistance(temperature, humidity)
            Measure_Ro += self.rsAir
            utime.sleep(0.1)
        Measure_Ro = Measure_Ro / self.MQ_SAMPLE_TIME
        Measure_Ro = Measure_Ro / self.MEASURED_RO_IN_CLEAN_AIR
        return Measure_Ro

    def measure_Rs(self, temperature, humidity):
        Measure_Rs = 0.0
        for _ in range(self.MQ_SAMPLE_TIME):
            self.read_raw_data()
            self.rsAir = self.get_corrected_resistance(temperature, humidity)
            Measure_Rs += self.rsAir
            utime.sleep(0.1)
        Measure_Rs = Measure_Rs / self.MQ_SAMPLE_TIME
        return Measure_Rs

    def measure_ratio(self, temperature, humidity):
        self.ratio = self.measure_Rs(temperature, humidity) / self.measure_Ro(temperature, humidity)
        # print("Ratio = {:.3f}".format(self.ratio))

    def calculate_ppm_CO2(self, temperature, humidity):
        """Calcula a concentração final de CO2 corrigida para temperatura/umidade"""
        self.measure_ratio(temperature, humidity)
        a = -0.32
        b = 1.0
        ppm = math.exp(((math.log(self.ratio, 10)) - b) / a)
        return {'co2': ppm}

    def calculate_ppm_NH3(self, temperature, humidity):
        """Calcula a concentração final de NH3 corrigida para temperatura/umidade"""
        self.measure_ratio(temperature, humidity)
        a = -0.41
        b = 1.0
        ppm = math.exp(((math.log(self.ratio, 10)) - b) / a)
        return {'nh3': ppm}

    def get_gas_concentrations(self, temperature, humidity):
        """Obtém as concentrações de gases corrigidas para temperatura e umidade"""
        co2 = self.calculate_ppm_CO2(temperature, humidity)
        nh3 = self.calculate_ppm_NH3(temperature, humidity)
        return co2, nh3