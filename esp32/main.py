from machine import I2C, Pin
import utime
import sys

from flame_sensor import FlameSensor
from bme280 import BME280
from mq135 import MQ135
from buzzer import Buzzer
from scd41 import SCD41
from ds1302 import DS1302
from ina219 import INA219
from lsm303d import LSM303
from l3gd20 import L3GD20
from uart_comm import UARTComm

def main():
    try:
        # print("Initializing I2C...")
        i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=115200)
        # print("I2C initialized.")
        
        # print("Initializing Buzzer...")
        buzzer = Buzzer()
        # print("Buzzer initialized.")
        
        # print("Initializing BME280 sensor...")
        bme = BME280(i2c=i2c)
        # print("BME280 sensor initialized.")

        # print("Initializing SCD4x sensor...")
        scd4x = SCD41(i2c)
        scd4x.begin()
        scd4x.set_calibration_mode(False)
        scd4x.save_settings()
        scd4x.start_periodic_measurement()
        # print("SCD4x sensor initialized.")
        
        # print("Initializing MQ135 sensor...")
        mq135 = MQ135()
        # print("MQ135 sensor initialized.")
        
        # print("Initializing Flame sensor...")
        flame = FlameSensor()
        # print("Flame sensor initialized.")
        
        # print("Initializing DS1302 RTC...")
        ds1302 = DS1302()
        ds1302.start()
        # ds1302.date_time([2024, 12, 18, 4, 9, 40, 30])
        # print("DS1302 RTC initialized.")
        
        # print("Initializing INA219 sensor...")
        ina = INA219(i2c)
        ina.configure()
        # print("INA219 sensor initialized.")
        
        # print("Initializing LSM303D sensor...")
        lsm303d = LSM303(i2c)
        # print("LSM303D sensor initialized.")
        
        # print("Initializing L3GD20 sensor...")
        l3gd20 = L3GD20(i2c)
        # print("L3GD20 sensor initialized.")

        # print("Initializing UART communication...")
        comm = UARTComm()
        # print("UART communication initialized.")

        while True:
            timestamp = ds1302.date_time()
            datetime_str_iso = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(timestamp[0], timestamp[1], timestamp[2], timestamp[4], timestamp[5], timestamp[6])
            comm.add_data("timestamp", datetime_str_iso)
            datetime_str = "{:s}, {:02d}/{:02d}/{:04d} {:02d}:{:02d}:{:02d} {:s}".format(ds1302.weekday_string(timestamp[3]), timestamp[2], timestamp[1], timestamp[0], timestamp[4], timestamp[5], timestamp[6], "BRT")

            # found_addresses = i2c.scan()
            # print("Found I2C addresses:", found_addresses)
            # utime.sleep(1)
            
            temp, pressure, humidity = bme.read_compensated_data()
            if pressure is not None:
                pressure_hpa = pressure / 100
            if temp is not None and pressure is not None and humidity is not None:
                print(f"[{datetime_str}] Temperature: {temp:.3f} Celsius; Pressure: {pressure_hpa:.3f} hPa; Humidity: {humidity:.3f}%")
                comm.add_data("temperature", temp)
                comm.add_data("pressure", pressure_hpa)
                comm.add_data("humidity", humidity)
            utime.sleep_ms(200)
            
            if flame.is_flame_detected():
                print(f"[{datetime_str}] Flame detected!")
                buzzer.sound_alarm('flame')
                comm.add_data("flame", True)
            else:
                print(f"[{datetime_str}] No flame detected.")
                comm.add_data("flame", False)
            utime.sleep_ms(200)
            
            co2, nh3 = get_gas_concentrations(temp, humidity)
            # if co2['co2'] is not None:
            #     print(f"[{datetime_str}] MQ135 - Carbon dioxide (CO2) concentration: {co2['co2']:.3f} ppm")
            #     if co2['co2'] > 1000:
            #         buzzer.sound_alarm('co2')
            if nh3['nh3'] is not None:
                print(f"[{datetime_str}] MQ131 - Ammonia (NH3) concentration: {nh3['nh3']:.3f} ppm")
                comm.add_data("nh3", nh3['nh3'])
                if nh3['nh3'] > 2.88:
                    buzzer.sound_alarm('nh3')
                    comm.add_data("nh3_alarm", True)
                else:
                    comm.add_data("nh3_alarm", False)

            utime.sleep_ms(500)

            try:
                if scd4x.is_data_ready():
                    # print("Data is ready, reading measurement...")
                    if pressure is not None:
                        scd4x.set_ambient_pressure(int(pressure_hpa))
                    co2_scd4x, t_scd4x, rh_scd4x = scd4x.read_measurement()
                    if co2_scd4x is not None:
                        print(f"[{datetime_str}] SCD41 - Carbon dioxide (CO2) concentration: {co2_scd4x:.0f} ppm")
                        comm.add_data("co2", co2_scd4x)
                        if co2_scd4x > 1000:
                            buzzer.sound_alarm('co2')
                            comm.add_data("co2_alarm", True)
                        else:
                            comm.add_data("co2_alarm", False)
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
                
            try:
                print("INA219 - Bus Voltage: %.3f V, Current: %.3f mA, Power: %.3f mW, Battery: %.3f%" % (ina.voltage(), ina.current(), ina.power(), ina.battery_percentage()))
            except Exception as e:
                print(f"Error reading INA219: {e}")
                
            try:
                accel_data = device.read_accel()
                mag_data = device.read_mag()
                print("LSM303D - Accelerometer: %.3f m/s^2, %.3f m/s^2, %.3f m/s^2, Magnetometer: %.3f uT, %.3f uT, %.3f uT" % (accel_data[0], accel_data[1], accel_data[2], mag_data[0], mag_data[1], mag_data[2]))
            except Exception as e:
                print(f"Error reading LSM303D: {e}")
                
            try:
                gyro_data = device.read_gyro()
                print("L3GD20 - Gyroscope: %.3f rad/s, %.3f rad/s, %.3f rad/s" % (gyro_data[0], gyro_data[1], gyro_data[2]))
            except Exception as e:
                print(f"Error reading L3GD20: {e}")

            comm.send_json()
            comm.read_serial()
            utime.sleep_ms(500)

    except Exception as e:
        print("An error occurred:")
        sys.print_exception(e)

if __name__ == "__main__":
    main()