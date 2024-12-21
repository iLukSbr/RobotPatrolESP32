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

# Flags to enable/disable components
ENABLE_I2C = True
ENABLE_BUZZER = True
ENABLE_BME280 = True
ENABLE_SCD4X = True
ENABLE_MQ135 = True
ENABLE_FLAME_SENSOR = True
ENABLE_DS1302 = True
ENABLE_INA219 = True
ENABLE_LSM303D = True
ENABLE_L3GD20 = True
ENABLE_UART_COMM = True

def main():
    try:
        if ENABLE_I2C:
            i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=115200)
        
        if ENABLE_BUZZER:
            buzzer = Buzzer()
        
        if ENABLE_BME280:
            bme = BME280(i2c=i2c)

        if ENABLE_SCD4X:
            scd4x = SCD41(i2c)
            scd4x.begin()
            scd4x.set_calibration_mode(False)
            scd4x.save_settings()
            scd4x.start_periodic_measurement()
        
        if ENABLE_MQ135:
            mq135 = MQ135()
        
        if ENABLE_FLAME_SENSOR:
            flame = FlameSensor()
        
        if ENABLE_DS1302:
            ds1302 = DS1302()
            ds1302.start()
        
        if ENABLE_INA219:
            ina = INA219(i2c)
            ina.configure()
        
        if ENABLE_LSM303D:
            lsm303d = LSM303(i2c)
        
        if ENABLE_L3GD20:
            l3gd20 = L3GD20(i2c)

        if ENABLE_UART_COMM:
            comm = UARTComm()

        while True:
            if ENABLE_DS1302:
                timestamp = ds1302.date_time()
                datetime_str_iso = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(timestamp[0], timestamp[1], timestamp[2], timestamp[4], timestamp[5], timestamp[6])
                comm.add_data("timestamp", datetime_str_iso)
                datetime_str = "{:s}, {:02d}/{:02d}/{:04d} {:02d}:{:02d}:{:02d} {:s}".format(ds1302.weekday_string(timestamp[3]), timestamp[2], timestamp[1], timestamp[0], timestamp[4], timestamp[5], timestamp[6], "BRT")

            if ENABLE_BME280:
                temp, pressure, humidity = bme.read_compensated_data()
                if pressure is not None:
                    pressure_hpa = pressure / 100
                if temp is not None and pressure is not None and humidity is not None:
                    print(f"[{datetime_str}] Temperature: {temp:.3f} Celsius; Pressure: {pressure_hpa:.3f} hPa; Humidity: {humidity:.3f}%")
                    comm.add_data("temperature", temp)
                    comm.add_data("pressure", pressure_hpa)
                    comm.add_data("humidity", humidity)
                utime.sleep_ms(200)
            
            if ENABLE_FLAME_SENSOR:
                if flame.is_flame_detected():
                    print(f"[{datetime_str}] Flame detected!")
                    if ENABLE_BUZZER:
                        buzzer.sound_alarm('flame')
                    comm.add_data("flame", True)
                else:
                    print(f"[{datetime_str}] No flame detected.")
                    comm.add_data("flame", False)
                utime.sleep_ms(200)
            
            if ENABLE_MQ135:
                co2, nh3 = get_gas_concentrations(temp, humidity)
                if nh3['nh3'] is not None:
                    print(f"[{datetime_str}] MQ131 - Ammonia (NH3) concentration: {nh3['nh3']:.3f} ppm")
                    comm.add_data("nh3", nh3['nh3'])
                    if nh3['nh3'] > 2.88:
                        if ENABLE_BUZZER:
                            buzzer.sound_alarm('nh3')
                        comm.add_data("nh3_alarm", True)
                    else:
                        comm.add_data("nh3_alarm", False)
                utime.sleep_ms(500)

            if ENABLE_SCD4X:
                try:
                    if scd4x.is_data_ready():
                        if pressure is not None:
                            scd4x.set_ambient_pressure(int(pressure_hpa))
                        co2_scd4x, t_scd4x, rh_scd4x = scd4x.read_measurement()
                        if co2_scd4x is not None:
                            print(f"[{datetime_str}] SCD41 - Carbon dioxide (CO2) concentration: {co2_scd4x:.0f} ppm")
                            comm.add_data("co2", co2_scd4x)
                            if co2_scd4x > 1000:
                                if ENABLE_BUZZER:
                                    buzzer.sound_alarm('co2')
                                comm.add_data("co2_alarm", True)
                            else:
                                comm.add_data("co2_alarm", False)
                        else:
                            print("Failed to read SCD41 measurement")
                    else:
                        print("SCD41 data not ready")
                except Exception as e:
                    print("Error reading SCD41 data:")
                    sys.print_exception(e)
                
            if ENABLE_INA219:
                try:
                    print("INA219 - Bus Voltage: %.3f V, Current: %.3f mA, Power: %.3f mW, Battery: %.3f%%" % (ina.voltage(), ina.current(), ina.power(), ina.battery_percentage()))
                except Exception as e:
                    print(f"Error reading INA219: {e}")
                
            if ENABLE_LSM303D:
                try:
                    accel_data = lsm303d.read_accel()
                    mag_data = lsm303d.read_mag()
                    print("LSM303D - Accelerometer: %.3f m/s^2, %.3f m/s^2, %.3f m/s^2, Magnetometer: %.3f uT, %.3f uT, %.3f uT" % (accel_data[0], accel_data[1], accel_data[2], mag_data[0], mag_data[1], mag_data[2]))
                except Exception as e:
                    print(f"Error reading LSM303D: {e}")
                
            if ENABLE_L3GD20:
                try:
                    gyro_data = l3gd20.gyro
                    print("L3GD20 - Gyroscope: %.3f rad/s, %.3f rad/s, %.3f rad/s" % (gyro_data[0], gyro_data[1], gyro_data[2]))
                except Exception as e:
                    print(f"Error reading L3GD20: {e}")

            if ENABLE_UART_COMM:
                comm.send_json()
                comm.read_serial()
            utime.sleep_ms(500)

    except Exception as e:
        print("An error occurred:")
        sys.print_exception(e)

if __name__ == "__main__":
    main()