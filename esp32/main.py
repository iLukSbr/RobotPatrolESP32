from machine import I2C, Pin
import utime
import sys

from flame import is_flame_detected
from bme280 import BME280
from mq135 import get_gas_concentrations
from sound import sound_alarm
from scd41 import SCD4X

def main():
    try:
        print("Initializing I2C...")
        i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=115200)
        print("I2C initialized.")
        
        print("Initializing BME280 sensor...")
        bme = BME280(i2c=i2c)
        print("BME280 sensor initialized.")

        print("Initializing SCD4x sensor...")
        scd4x = SCD4X(i2c)
        scd4x.begin()
        scd4x.set_calibration_mode(False)
        scd4x.save_settings()
        scd4x.start_periodic_measurement()
        print("SCD4x sensor initialized.")
        
        while True:
            # Example usage
            sound_alarm('flame')
            utime.sleep(1)
            sound_alarm('co2')
            utime.sleep(1)
            sound_alarm('nh3')
            utime.sleep(1)
            
            found_addresses = i2c.scan()
            print("Found I2C addresses:", found_addresses)
            utime.sleep(1)
            
            temp, pressure, humidity = bme.read_compensated_data()
            print("Temperature: {:.2f} Celsius; Pressure: {:.2f} hPa; Humidity: {:.2f}%".format(temp, pressure, humidity))
            utime.sleep(1)
            
            if is_flame_detected():
                print("Flame detected!")
            else:
                print("No flame detected.")
            utime.sleep(1)
            
            co2, nh3 = get_gas_concentrations(temp, humidity)
            print("Carbon Dioxide Concentration: {:.3f} ppm".format(co2['co2']))
            print("Ammonia Concentration: {:.3f} ppm".format(nh3['nh3']))
            utime.sleep(1)

            try:
                if scd4x.is_data_ready():
                    print("Data is ready, reading measurement...")
                    co2_scd4x, t_scd4x, rh_scd4x = scd4x.read_measurement()
                    if co2_scd4x is not None:
                        print(f"SCD41 - CO2 [ppm]: {co2_scd4x:.0f}; Temperature: {t_scd4x:.4f} Celsius; Humidity: {rh_scd4x:.4f}%")
                    else:
                        print("Failed to read SCD41 measurement")
                else:
                    print("SCD41 data not ready")
            except Exception as e:
                print("Error reading SCD41 data:")
                sys.print_exception(e)
            utime.sleep(1)

    except Exception as e:
        print("An error occurred:")
        sys.print_exception(e)

if __name__ == "__main__":
    main()