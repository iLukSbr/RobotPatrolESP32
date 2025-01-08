from machine import I2C, Pin
import utime
import sys

from actuators import Buzzer
from communication import DS1302, UARTComm, JSONParser
from utils import *
from sensors import BME280, FlameSensor, HCSR04, INA219, L3GD20, LSM303, MQ135, SCD41

def main():
    try:
        if ENABLE_I2C:
            i2c = I2C(0, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=I2C_FREQ)
            print("I2C devices found: ", [hex(device) for device in i2c.scan()])
        
        if ENABLE_BME280:
            bme = BME280(i2c)
            
        if ENABLE_BUZZER:
            buzzer = Buzzer()

        if ENABLE_DS1302:
            ds1302 = DS1302()
            ds1302.start()

        if ENABLE_FLAME_SENSOR:
            flame = FlameSensor()
            
        if ENABLE_HCSR04:
            hcsr04 = {
                "front": HCSR04(trig_pin=32, echo_pin=36),
                "left": HCSR04(trig_pin=33, echo_pin=39),
                "right": HCSR04(trig_pin=25, echo_pin=34),
                "rear": HCSR04(trig_pin=26, echo_pin=35)
            }

        if ENABLE_INA219:
            ina = INA219(i2c)
            ina.configure()      

        if ENABLE_L3GD20:
            l3gd20 = L3GD20(i2c)

        if ENABLE_LSM303D:
            lsm303d = LSM303(i2c)
        
        if ENABLE_MQ135:
            mq135 = MQ135()
            
        if ENABLE_SCD41:
            scd41 = SCD41(i2c)
            scd41.begin()
            scd41.set_calibration_mode(False)
            scd41.save_settings()
            scd41.start_periodic_measurement()

        if ENABLE_UART_COMM:
            comm = UARTComm()
            json_parser = JSONParser()

        while True:
            if ENABLE_DS1302:
                timestamp = ds1302.date_time()
                datetime_str_iso = format_iso_datetime(timestamp)
                json_parser.add_data("timestamp", datetime_str_iso)
                datetime_str = format_brt_datetime(timestamp, ds1302.weekday_string(timestamp[3]))
            else:
                datetime_str = ""

            if ENABLE_BME280:
                temp, pressure, humidity = bme.read_compensated_data()
                if pressure is not None:
                    pressure_hpa = pressure / 100
                if temp is not None and pressure is not None and humidity is not None:
                    info_print(f"[{datetime_str}] Temperature: {temp:.3f} Celsius; Pressure: {pressure_hpa:.3f} hPa; Humidity: {humidity:.3f}%")
                    json_parser.add_data("temperature", temp)
                    json_parser.add_data("pressure", pressure_hpa)
                    json_parser.add_data("humidity", humidity)
                utime.sleep_ms(200)
            
            if ENABLE_FLAME_SENSOR:
                if flame.is_flame_detected():
                    info_print(f"[{datetime_str}] Flame detected!")
                    if ENABLE_BUZZER:
                        buzzer.sound_alarm('flame')
                    json_parser.add_data("flame", True)
                else:
                    info_print(f"[{datetime_str}] No flame detected.")
                    json_parser.add_data("flame", False)
                utime.sleep_ms(200)
                
            if ENABLE_HCSR04:
                for key, sensor in hcsr04.items():
                    distance = sensor.medir_mediana()
                    if distance is not None:
                        info_print(f"[{datetime_str}] HCSR04 {key} - Distance: {distance:.3f} cm")
                        json_parser.add_data(f"distance.{key}", distance)
                    utime.sleep_ms(200)
            
            if ENABLE_MQ135:
                co2, nh3 = mq135.get_gas_concentrations(temp, humidity)
                if nh3['nh3'] is not None:
                    info_print(f"[{datetime_str}] MQ131 - Ammonia (NH3) concentration: {nh3['nh3']:.3f} ppm")
                    json_parser.add_data("nh3", nh3['nh3'])
                    if nh3['nh3'] > NH3_THRESHOLD:
                        if ENABLE_BUZZER:
                            buzzer.sound_alarm('nh3')
                        json_parser.add_data("nh3_alarm", True)
                    else:
                        json_parser.add_data("nh3_alarm", False)
                utime.sleep_ms(500)

            if ENABLE_SCD41:
                try:
                    if scd41.is_data_ready():
                        if pressure is not None:
                            scd41.set_ambient_pressure(int(pressure_hpa))
                        co2_scd41, t_scd41, rh_scd41 = scd41.read_measurement()
                        if co2_scd41 is not None:
                            info_print(f"[{datetime_str}] SCD41 - Carbon dioxide (CO2) concentration: {co2_scd41:.0f} ppm")
                            json_parser.add_data("co2", co2_scd41)
                            if co2_scd41 > CO2_THRESHOLD:
                                if ENABLE_BUZZER:
                                    buzzer.sound_alarm('co2')
                                json_parser.add_data("co2_alarm", True)
                            else:
                                json_parser.add_data("co2_alarm", False)
                        else:
                            info_print("Failed to read SCD41 measurement")
                    else:
                        info_print("SCD41 data not ready")
                except Exception as e:
                    error_print(f"Error reading SCD41 data: {e}")
                
            if ENABLE_INA219:
                try:
                    json_parser.add_data("bus_voltage", ina.voltage())
                    json_parser.add_data("current", ina.current())
                    json_parser.add_data("power", ina.power())
                    json_parser.add_data("battery_percentage", ina.battery_percentage())
                    info_print("INA219 - Bus Voltage: %.3f V, Current: %.3f mA, Power: %.3f mW, Battery: %.3f%%" % (ina.voltage(), ina.current(), ina.power(), ina.battery_percentage()))
                except Exception as e:
                    error_print(f"Error reading INA219: {e}")
                
            if ENABLE_LSM303D:
                try:
                    accel_data = lsm303d.read_accel()
                    mag_data = lsm303d.read_mag()
                    json_parser.add_data("accelerometer.x", accel_data[0])
                    json_parser.add_data("accelerometer.y", accel_data[1])
                    json_parser.add_data("accelerometer.z", accel_data[2])
                    json_parser.add_data("magnetometer.x", mag_data[0])
                    json_parser.add_data("magnetometer.y", mag_data[1])
                    json_parser.add_data("magnetometer.z", mag_data[2])
                    info_print("LSM303D - Accelerometer: %.3f m/s^2, %.3f m/s^2, %.3f m/s^2, Magnetometer: %.3f uT, %.3f uT, %.3f uT" % (accel_data[0], accel_data[1], accel_data[2], mag_data[0], mag_data[1], mag_data[2]))
                except Exception as e:
                    error_print(f"Error reading LSM303D: {e}")
                
            if ENABLE_L3GD20:
                try:
                    gyro_data = l3gd20.gyro
                    json_parser.add_data("gyroscope.x", gyro_data[0])
                    json_parser.add_data("gyroscope.y", gyro_data[1])
                    json_parser.add_data("gyroscope.z", gyro_data[2])
                    info_print("L3GD20 - Gyroscope: %.3f rad/s, %.3f rad/s, %.3f rad/s" % (gyro_data[0], gyro_data[1], gyro_data[2]))
                except Exception as e:
                    error_print(f"Error reading L3GD20: {e}")

            message = json_parser.get_json_message()
            info_print(f"JSON message: {message}")
            
            if ENABLE_UART_COMM:
                if message:
                    comm.send_message(message)
                comm.read_serial()
                
            json_parser.clear_json_message()
            utime.sleep_ms(500)

    except Exception as e:
        error_print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
