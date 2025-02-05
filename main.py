from machine import I2C, Pin
import time
import sys

from actuators import KY006
from communication import DS1302, UARTComm, JSONParser
from utils import *
from sensors import BME280, HC020K, HCSR04, INA219, KY026, L3GD20, LSM303, MQ135, SCD41

def main():
    try:
        if ENABLE_I2C:
            i2c = I2C(0, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=I2C_FREQ)
            print("I2C devices found: ", [hex(device) for device in i2c.scan()])
        
        if ENABLE_BME280:
            bme = BME280(i2c)

        if ENABLE_DS1302:
            ds1302 = DS1302(clk=23, dat=18, rst=19)
            
        if any(ENABLE_HC020K.values()):
            hc020k = {}
            if ENABLE_HC020K.get("front_left", False):
                hc020k["front_left"] = HC020K(pin=14)
            if ENABLE_HC020K.get("front_right", False):
                hc020k["front_right"] = HC020K(pin=15)
            if ENABLE_HC020K.get("rear_left", False):
                hc020k["rear_left"] = HC020K(pin=5)
            if ENABLE_HC020K.get("rear_right", False):
                hc020k["rear_right"] = HC020K(pin=2)
            
        if any(ENABLE_HCSR04.values()):
            hcsr04 = {}
            if ENABLE_HCSR04.get("front", False):
                hcsr04["front"] = HCSR04(trig_pin=32, echo_pin=36)
            if ENABLE_HCSR04.get("left", False):
                hcsr04["left"] = HCSR04(trig_pin=33, echo_pin=39)
            if ENABLE_HCSR04.get("right", False):
                hcsr04["right"] = HCSR04(trig_pin=25, echo_pin=34)
            if ENABLE_HCSR04.get("rear", False):
                hcsr04["rear"] = HCSR04(trig_pin=26, echo_pin=35)
                
        if ENABLE_KY006:
            ky006 = KY006(pwm_pin=13)
                
        if ENABLE_KY026:
            ky026 = KY026(pin=14)

        if ENABLE_INA219:
            ina = INA219(i2c)     

        if ENABLE_L3GD20:
            l3gd20 = L3GD20(i2c)

        if ENABLE_LSM303D:
            lsm303d = LSM303(i2c)
        
        if ENABLE_MQ135:
            mq135 = MQ135(adc_pin=27)
            
        if ENABLE_SCD41:
            scd41 = SCD41(i2c)

        if ENABLE_UART_COMM:
            comm = UARTComm(tx_pin=17, rx_pin=16)
            json_parser = JSONParser()
    except Exception as e:
        error_print(f"An error occurred during initialization: {e}")

    while True:
        try:
            if ENABLE_DS1302:
                try:
                    timestamp = ds1302.date_time()
                    datetime_str_iso = format_iso_datetime(timestamp)
                    json_parser.add_data("timestamp", datetime_str_iso)
                    datetime_str = format_brt_datetime(timestamp, ds1302.weekday_string(timestamp[3]))
                except Exception as e:
                    error_print(f"Error reading DS1302 data: {e}")
            else:
                datetime_str = ""

            if ENABLE_BME280:
                try:
                    temp, pressure, humidity = bme.read_compensated_data()
                    if pressure is not None:
                        pressure_hpa = pressure / 100
                    if temp is not None and pressure is not None and humidity is not None:
                        info_print(f"[{datetime_str}] Temperature: {temp:.3f} Celsius; Pressure: {pressure_hpa:.3f} hPa; Humidity: {humidity:.3f}%")
                        json_parser.add_data("temperature", temp)
                        json_parser.add_data("pressure", pressure_hpa)
                        json_parser.add_data("humidity", humidity)
                except Exception as e:
                    error_print(f"Error reading BME280 data: {e}")
                
            if any(ENABLE_HC020K.values()):
                try:
                    for key, sensor in hc020k.items():
                        speed = sensor.get_speed_cmps()
                        if speed is not None:
                            info_print(f"[{datetime_str}] HC020K {key} - Speed: {speed:.3f} cm/s")
                            json_parser.add_data(f"speed.{key}", speed)
                        distance = sensor.get_distance_traveled_m()
                        if distance is not None:
                            info_print(f"[{datetime_str}] HC020K {key} - Distance: {distance:.3f} m")
                            json_parser.add_data(f"traveled.{key}", distance)
                except Exception as e:
                    error_print(f"Error reading HC020K data: {e}")
            
            if any(ENABLE_HCSR04.values()):
                try:
                    for key, sensor in hcsr04.items():
                        distance = sensor.measure_median()
                        if distance is not None:
                            info_print(f"[{datetime_str}] HCSR04 {key} - Distance: {distance:.3f} cm")
                            json_parser.add_data(f"distance.{key}", distance)
                except Exception as e:
                    error_print(f"Error reading HCSR04 data: {e}")
            
            if ENABLE_INA219:
                try:
                    json_parser.add_data("bus_voltage", ina.voltage())
                    json_parser.add_data("current", ina.current())
                    json_parser.add_data("power", ina.power())
                    json_parser.add_data("battery_percentage", ina.battery_percentage())
                    info_print(f"[{datetime_str}] INA219 - Bus Voltage: %.3f V, Current: %.3f mA, Power: %.3f mW, Battery: %.3f%%" % (ina.voltage(), ina.current(), ina.power(), ina.battery_percentage()))
                except Exception as e:
                    error_print(f"Error reading INA219: {e}")
            
            if ENABLE_KY026:
                try:
                    if ky026.is_flame_detected():
                        info_print(f"[{datetime_str}] Flame detected!")
                        if ENABLE_KY006:
                            ky006.sound_alarm('flame')
                        json_parser.add_data("flame", True)
                    else:
                        info_print(f"[{datetime_str}] No flame detected.")
                        json_parser.add_data("flame", False)
                except Exception as e:
                    error_print(f"Error reading KY026: {e}")
            
            if ENABLE_MQ135:
                try:
                    co2, nh3 = mq135.get_gas_concentrations(temp, humidity)
                    if nh3['nh3'] is not None:
                        info_print(f"[{datetime_str}] MQ131 - Ammonia (NH3) concentration: {nh3['nh3']:.3f} ppm")
                        json_parser.add_data("nh3", nh3['nh3'])
                        if nh3['nh3'] > NH3_THRESHOLD:
                            if ENABLE_KY006:
                                ky006.sound_alarm('nh3')
                            json_parser.add_data("nh3_alarm", True)
                        else:
                            json_parser.add_data("nh3_alarm", False)
                except Exception as e:
                    error_print(f"Error reading MQ135 data: {e}")

            if ENABLE_L3GD20:
                try:
                    gyro_data = l3gd20.gyro
                    json_parser.add_data("gyroscope.x", gyro_data[0])
                    json_parser.add_data("gyroscope.y", gyro_data[1])
                    json_parser.add_data("gyroscope.z", gyro_data[2])
                    info_print(f"[{datetime_str}] L3GD20 - Gyroscope: %.3f rad/s, %.3f rad/s, %.3f rad/s" % (gyro_data[0], gyro_data[1], gyro_data[2]))
                except Exception as e:
                    error_print(f"Error reading L3GD20: {e}")
                
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
                    info_print(f"[{datetime_str}] LSM303D - Accelerometer: %.3f m/s^2, %.3f m/s^2, %.3f m/s^2, Magnetometer: %.3f uT, %.3f uT, %.3f uT" % (accel_data[0], accel_data[1], accel_data[2], mag_data[0], mag_data[1], mag_data[2]))
                except Exception as e:
                    error_print(f"Error reading LSM303D: {e}")
                    
            if ENABLE_SCD41:
                try:
                    if ENABLE_BME280 and pressure is not None:
                        co2_scd41, t_scd41, rh_scd41 = scd41.read_measurement(int(pressure_hpa))
                    else:
                        co2_scd41, t_scd41, rh_scd41 = scd41.read_measurement()
                    if co2_scd41 is not None and co2_scd41 > 0:
                        info_print(f"[{datetime_str}] SCD41 - Carbon dioxide (CO2) concentration: {co2_scd41:.0f} ppm")
                        json_parser.add_data("co2", co2_scd41)
                        if co2_scd41 > CO2_THRESHOLD:
                            if ENABLE_KY006:
                                ky006.sound_alarm('co2')
                            json_parser.add_data("co2_alarm", True)
                        else:
                            json_parser.add_data("co2_alarm", False)
                    else:
                        info_print("Failed to read SCD41 measurement")
                except Exception as e:
                    error_print(f"Error reading SCD41 data: {e}")
                    
            message = json_parser.get_json_message()
            info_print(f"JSON message: {message}")
            
            if ENABLE_UART_COMM:
                if message:
                    comm.send_message(message)
                comm.read_serial()
                
            json_parser.clear_json_message()
            
            time.sleep_us(1)
            
        except Exception as e:
            error_print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
