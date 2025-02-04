import time
from uart_comm import UARTComm
from ..sensors.mq135 import MQ135 #NH3
from ..sensors.scd41 import SCD41 #CO2 TEMP HUM
from ..sensors.ky026 import KY026

MQ135_instance = MQ135()
SCD41_instance = SCD41()
KY026_instance = KY026()

UARTComm_instance = UARTComm()

while True:
    try:
        co2, temperature, humidity = SCD41_instance.read_measurement()
        _, nh3 = MQ135_instance.get_gas_concentrations(temperature, humidity)
        flame = KY026_instance.is_flame_detected()

        message = str(co2) + "," + str(temperature) + "," + str(humidity) + "," + str(nh3) + "," + str(flame)

        UARTComm_instance.send_message(message)
        print("Sensor data sent.")
    
    except Exception as e:
            print(f"Failed to send sensor data: {e}")
    
    time.sleep(1)