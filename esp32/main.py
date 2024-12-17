from machine import I2C, Pin
import utime
import sys

from flame import is_flame_detected
from bme280 import BME280
from mq135 import get_gas_concentrations
from buzzer import sound_alarm
from scd41 import SCD4X
from ds1302 import DS1302

def main():
    try:
        # print("Initializing I2C...")
        i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=115200)
        # print("I2C initialized.")
        
        # print("Initializing BME280 sensor...")
        bme = BME280(i2c=i2c)
        # print("BME280 sensor initialized.")

        # print("Initializing SCD4x sensor...")
        scd4x = SCD4X(i2c)
        scd4x.begin()
        scd4x.set_calibration_mode(False)
        scd4x.save_settings()
        scd4x.start_periodic_measurement()
        # print("SCD4x sensor initialized.")
        
        # print("Initializing DS1302 RTC...")
        ds1302 = DS1302(clk=Pin(17), dio=Pin(18), cs=Pin(19))
        ds1302.start()
        ds1302.year(2024)
        ds1302.month(12)
        ds1302.day(18)
        ds1302.hour(11)
        ds1302.minute(30)
        ds1302.second(0)
        # print("DS1302 RTC initialized.")

        while True:
            timestamp = ds1302.date_time()
            datetime_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(timestamp[0], timestamp[1], timestamp[2], timestamp[3], timestamp[4], timestamp[5])

            # found_addresses = i2c.scan()
            # print("Found I2C addresses:", found_addresses)
            # utime.sleep(1)
            
            temp, pressure, humidity = bme.read_compensated_data()
            if pressure is not None:
                pressure_hpa = pressure / 100
            if temp is not None and pressure is not None and humidity is not None:
                print(f"[{datetime_str}] Temperature: {temp:.3f} Celsius; Pressure: {pressure_hpa:.3f} hPa; Humidity: {humidity:.3f}%")
            utime.sleep_ms(200)
            
            if is_flame_detected():
                print(f"[{datetime_str}] Flame detected!")
                sound_alarm('flame')
            else:
                print(f"[{datetime_str}] No flame detected.")
            utime.sleep_ms(200)
            
            co2, nh3 = get_gas_concentrations(temp, humidity)
            # if co2['co2'] is not None:
            #     print(f"[{datetime_str}] MQ135 - Carbon dioxide (CO2) concentration: {co2['co2']:.3f} ppm")
            #     if co2['co2'] > 1000:
            #         sound_alarm('co2')
            if nh3['nh3'] is not None:
                print(f"[{datetime_str}] MQ131 - Ammonia (NH3) concentration: {nh3['nh3']:.3f} ppm")
                if nh3['nh3'] > 2.88:
                    sound_alarm('nh3')

            utime.sleep_ms(500)

            try:
                if scd4x.is_data_ready():
                    # print("Data is ready, reading measurement...")
                    if pressure is not None:
                        scd4x.set_ambient_pressure(int(pressure_hpa))
                    co2_scd4x, t_scd4x, rh_scd4x = scd4x.read_measurement()
                    if co2_scd4x is not None:
                        print(f"[{datetime_str}] SCD41 - Carbon dioxide (CO2) concentration: {co2_scd4x:.0f} ppm")
                        if co2_scd4x > 1000:
                            sound_alarm('co2')
                    else:
                        print("Failed to read SCD41 measurement")
                    # if t_scd4x is not None:
                        # print(f"SCD41 - Temperature: {t_scd4x:.3f} oC")
                    # if rh_scd4x is not None:
                        # print(f"SCD41 - Relative humidity [%]: {rh_scd4x:.3f}%")
                else:
                    print("SCD41 data not ready")
            except Exception as e:
                print("Error reading SCD41 data:")
                sys.print_exception(e)

            utime.sleep_ms(500)

    except Exception as e:
        print("An error occurred:")
        sys.print_exception(e)

if __name__ == "__main__":
    main()