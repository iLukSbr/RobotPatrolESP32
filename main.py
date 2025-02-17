from machine import I2C, Pin
import time

from actuators import KY006
from communication import DS1302, UARTComm, JSONParser
from utils import *
from sensors import BME280, HC020K, HCSR04, INA219, KY026, L3GD20, LSM303, MQ135, SCD41

def main():
    json_parser = None
    comm = None
    ds1302 = None
    hc020k = None
    hcsr04 = None
    ky006 = None
    ky026 = None
    mq135 = None
    i2c = None
    bme = None
    ina = None
    l3gd20 = None
    lsm303d = None
    scd41 = None
    devices = None
    datetime_str = None
    pressure_hpa = None
    
    try:
        json_parser = JSONParser()
    except Exception as e:
        error_print(f"Error initializing JSON parser: {e}")
    
    if ENABLE_UART_COMM:
        try:
            comm = UARTComm(tx_pin=17, rx_pin=16, baudrate=UART_BAUD_RATE, timeout=UART_TIMEOUT)
        except Exception as e:
            json_parser.add_data("error", f"Error initializing UART communication: {e}")
            message = json_parser.get_json_message()
            info_print(f"JSON message: {message}")
            if ENABLE_UART_COMM and message:
                comm.send_message(message)
            json_parser.clear_json_message()
            error_print(f"Error initializing UART communication: {e}")
        
    if ENABLE_DS1302:
        try:
            ds1302 = DS1302(clk=23, dat=18, rst=19)
        except Exception as e:
            json_parser.add_data("error", f"Error initializing DS1302: {e}")
            message = json_parser.get_json_message()
            info_print(f"JSON message: {message}")
            if ENABLE_UART_COMM and message:
                comm.send_message(message)
            json_parser.clear_json_message()
            error_print(f"Error initializing DS1302: {e}")
        
    if any(ENABLE_HC020K.values()):
        try:
            hc020k = {}
            if ENABLE_HC020K.get("front_left", False):
                hc020k["front_left"] = HC020K(pin=14, interrupt_type=Pin.IRQ_RISING)
            if ENABLE_HC020K.get("front_right", False):
                hc020k["front_right"] = HC020K(pin=15, interrupt_type=Pin.IRQ_RISING)
            if ENABLE_HC020K.get("rear_left", False):
                hc020k["rear_left"] = HC020K(pin=5, interrupt_type=Pin.IRQ_RISING)
            if ENABLE_HC020K.get("rear_right", False):
                hc020k["rear_right"] = HC020K(pin=2, interrupt_type=Pin.IRQ_FALLING)
        except Exception as e:
            json_parser.add_data("error", f"Error initializing HC020K: {e}")
            message = json_parser.get_json_message()
            info_print(f"JSON message: {message}")
            if ENABLE_UART_COMM and message:
                comm.send_message(message)
            json_parser.clear_json_message()
            error_print(f"Error initializing HC020K: {e}")
        
    if any(ENABLE_HCSR04.values()):
        try:
            hcsr04 = {}
            if ENABLE_HCSR04.get("front", False):
                hcsr04["front"] = HCSR04(trig_pin=26, echo_pin=35)
            if ENABLE_HCSR04.get("left", False):
                hcsr04["left"] = HCSR04(trig_pin=25, echo_pin=34)
            if ENABLE_HCSR04.get("right", False):
                hcsr04["right"] = HCSR04(trig_pin=33, echo_pin=39)
            if ENABLE_HCSR04.get("rear", False):
                hcsr04["rear"] = HCSR04(trig_pin=32, echo_pin=36)
        except Exception as e:
            json_parser.add_data("error", f"Error initializing HCSR04: {e}")
            message = json_parser.get_json_message()
            info_print(f"JSON message: {message}") 
            if ENABLE_UART_COMM and message:
                comm.send_message(message)
            json_parser.clear_json_message()
            error_print(f"Error initializing HCSR04: {e}")
            
    if ENABLE_KY006:
        try:
            ky006 = KY006(pin=13)
        except Exception as e:
            json_parser.add_data("error", f"Error initializing KY006: {e}")
            message = json_parser.get_json_message()
            info_print(f"JSON message: {message}") 
            if ENABLE_UART_COMM and message:
                comm.send_message(message)
            json_parser.clear_json_message()
            error_print(f"Error initializing KY006: {e}")
            
    if ENABLE_KY026:
        try:
            ky026 = KY026(pin=4)
        except Exception as e:
            json_parser.add_data("error", f"Error initializing KY026: {e}")
            message = json_parser.get_json_message()
            info_print(f"JSON message: {message}") 
            if ENABLE_UART_COMM and message:
                comm.send_message(message)
            json_parser.clear_json_message()
            error_print(f"Error initializing KY026: {e}")
        
    if ENABLE_MQ135:
        try:
            mq135 = MQ135(adc_pin=27)
        except Exception as e:
            json_parser.add_data("error", f"Error initializing MQ135: {e}")
            message = json_parser.get_json_message()
            info_print(f"JSON message: {message}") 
            if ENABLE_UART_COMM and message:
                comm.send_message(message)
            json_parser.clear_json_message()
            error_print(f"Error initializing MQ135: {e}")
    
    if ENABLE_I2C:
        try:
            i2c = I2C(0, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=I2C_FREQ)
            devices = i2c.scan()
            while True:
                if devices:
                    print("I2C devices found: ", [hex(device) for device in devices])
                    break
                else:
                    json_parser.add_data("error", "No I2C devices found")
                    message = json_parser.get_json_message()
                    info_print(f"JSON message: {message}") 
                    if ENABLE_UART_COMM and message:
                        comm.send_message(message)
                    json_parser.clear_json_message()
                    time.sleep(1)
                    devices = i2c.scan()
        except Exception as e:
            json_parser.add_data("error", f"Error initializing I2C: {e}")
            message = json_parser.get_json_message()
            info_print(f"JSON message: {message}") 
            if ENABLE_UART_COMM and message:
                comm.send_message(message)
            json_parser.clear_json_message()
            error_print(f"Error initializing I2C: {e}")
    
        if ENABLE_BME280:
            try:
                # while True:
                #     if BME280.get_i2c_address() in devices:
                #         break
                #     else:
                #         json_parser.add_data("error", "BME280 barometer/thermometer/hygrometer not found")
                #         message = json_parser.get_json_message()
                #         info_print(f"JSON message: {message}") 
                #         if ENABLE_UART_COMM and message:
                #             comm.send_message(message)
                #         json_parser.clear_json_message()
                #         time.sleep(1)
                #         devices = i2c.scan()
                bme = BME280(i2c)
            except Exception as e:
                json_parser.add_data("error", f"Error initializing BME280: {e}")
                message = json_parser.get_json_message()
                info_print(f"JSON message: {message}") 
                if ENABLE_UART_COMM and message:
                    comm.send_message(message)
                json_parser.clear_json_message()
                error_print(f"Error initializing BME280: {e}")
                
        if ENABLE_INA219:
            try:
                # while True:
                #     if INA219.get_i2c_address() in devices:
                #         break
                #     else:
                #         json_parser.add_data("error", "INA219 multimeter not found")
                #         message = json_parser.get_json_message()
                #         info_print(f"JSON message: {message}") 
                #         if ENABLE_UART_COMM and message:
                #             comm.send_message(message)
                #         json_parser.clear_json_message()
                #         time.sleep(1)
                #         devices = i2c.scan()
                ina = INA219(i2c)     
            except Exception as e:
                json_parser.add_data("error", f"Error initializing INA219: {e}")
                message = json_parser.get_json_message()
                info_print(f"JSON message: {message}") 
                if ENABLE_UART_COMM and message:
                    comm.send_message(message)
                json_parser.clear_json_message()
                error_print(f"Error initializing INA219: {e}")
                
        if ENABLE_L3GD20:
            try:
                # while True:
                #     if L3GD20.get_i2c_address() in devices:
                #         break
                #     else:
                #         json_parser.add_data("error", "L3GD20 magnetometer not found")
                #         message = json_parser.get_json_message()
                #         info_print(f"JSON message: {message}") 
                #         if ENABLE_UART_COMM and message:
                #             comm.send_message(message)
                #         json_parser.clear_json_message()
                #         time.sleep(1)
                #         devices = i2c.scan()
                l3gd20 = L3GD20(i2c)
            except Exception as e:
                json_parser.add_data("error", f"Error initializing L3GD20: {e}")
                message = json_parser.get_json_message()
                info_print(f"JSON message: {message}") 
                if ENABLE_UART_COMM and message:
                    comm.send_message(message)
                json_parser.clear_json_message()
                error_print(f"Error initializing L3GD20: {e}")

        if ENABLE_LSM303D:
            # try:
                # while True:
                #     if LSM303.get_accel_i2c_address() in devices:
                #         break
                #     else:
                #         json_parser.add_data("error", "LSM303D accelerometer not found")
                #         message = json_parser.get_json_message()
                #         info_print(f"JSON message: {message}") 
                #         if ENABLE_UART_COMM and message:
                #             comm.send_message(message)
                #         json_parser.clear_json_message()
                #         time.sleep(1)
                #         devices = i2c.scan()
            # except Exception as e:
            #     json_parser.add_data("error", f"Error initializing LSM303D: {e}")
            #     message = json_parser.get_json_message()
            #     info_print(f"JSON message: {message}") 
            #     if ENABLE_UART_COMM and message:
            #         comm.send_message(message)
            #     json_parser.clear_json_message()
            #     error_print(f"Error initializing LSM303D: {e}")
            try:
                # while True:
                #     if LSM303.get_mag_i2c_address() in devices:
                #         break
                #     else:
                #         json_parser.add_data("error", "LSM303D magnetometer not found")
                #         message = json_parser.get_json_message()
                #         info_print(f"JSON message: {message}") 
                #         if ENABLE_UART_COMM and message:
                #             comm.send_message(message)
                #         json_parser.clear_json_message()
                #         time.sleep(1)
                #         devices = i2c.scan()
                lsm303d = LSM303(i2c)
            except Exception as e:
                json_parser.add_data("error", f"Error initializing LSM303D: {e}")
                message = json_parser.get_json_message()
                info_print(f"JSON message: {message}") 
                if ENABLE_UART_COMM and message:
                    comm.send_message(message)
                json_parser.clear_json_message()
                error_print(f"Error initializing LSM303D: {e}")
        
        if ENABLE_SCD41:
            try:
                # while True:
                #     if SCD41.get_i2c_address() in devices:
                #         break
                #     else:
                #         json_parser.add_data("error", "SCD41 CO2 sensor not found")
                #         message = json_parser.get_json_message()
                #         info_print(f"JSON message: {message}") 
                #         if ENABLE_UART_COMM and message:
                #             comm.send_message(message)
                #         json_parser.clear_json_message()
                #         time.sleep(1)
                #         devices = i2c.scan()
                scd41 = SCD41(i2c)
            except Exception as e:
                json_parser.add_data("error", f"Error initializing SCD41: {e}")
                message = json_parser.get_json_message()
                info_print(f"JSON message: {message}") 
                if ENABLE_UART_COMM:
                    if message:
                        comm.send_message(message)
                json_parser.clear_json_message()
                error_print(f"Error initializing SCD41: {e}")

    while True:
        try:
            if ENABLE_DS1302:
                try:
                    timestamp = ds1302.date_time()
                    datetime_str_iso = format_iso_datetime(timestamp)
                    json_parser.add_data("timestamp", datetime_str_iso)
                    datetime_str = format_brt_datetime(timestamp, ds1302.weekday_string(timestamp[3]))
                except Exception as e:
                    json_parser.add_data("error_ds1302", f"Error reading DS1302 data: {e}")
                    error_print(f"Error reading DS1302 data: {e}")
            else:
                datetime_str = time.ticks_ms() / 60000

            if ENABLE_BME280 and ENABLE_I2C:
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
                    json_parser.add_data("error_bme280", f"Error reading BME280 data: {e}")
                    error_print(f"Error reading BME280 data: {e}")
                    temp = None
                    pressure_hpa = None
                    humidity = None
            else:
                temp = None
                pressure_hpa = None
                humidity = None
            
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
                    json_parser.add_data("error_hc020k", f"Error reading HC020K data: {e}")
                    error_print(f"Error reading HC020K data: {e}")
            
            if any(ENABLE_HCSR04.values()):
                try:
                    for key, sensor in hcsr04.items():
                        distance = sensor.measure_median()
                        if distance is not None:
                            info_print(f"[{datetime_str}] HCSR04 {key} - Distance: {distance:.3f} cm")
                            json_parser.add_data(f"distance.{key}", distance)
                except Exception as e:
                    json_parser.add_data("error_hcsr04", f"Error reading HCSR04 data: {e}")
                    error_print(f"Error reading HCSR04 data: {e}")
            
            if ENABLE_INA219 and ENABLE_I2C:
                try:
                    json_parser.add_data("bus_voltage", ina.voltage())
                    json_parser.add_data("current", ina.current())
                    json_parser.add_data("power", ina.power())
                    json_parser.add_data("battery_percentage", ina.battery_percentage())
                    info_print(f"[{datetime_str}] INA219 - Bus Voltage: %.3f V, Current: %.3f mA, Power: %.3f mW, Battery: %.3f%%" % (ina.voltage(), ina.current(), ina.power(), ina.battery_percentage()))
                except Exception as e:
                    json_parser.add_data("error_ina219", f"Error reading INA219: {e}")
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
                    json_parser.add_data("error_ky026", f"Error reading KY026: {e}")
                    error_print(f"Error reading KY026: {e}")
            
            if ENABLE_MQ135:
                raw_nh3 = mq135.read_raw_data()
                info_print(f"[{datetime_str}] Raw MQ135 ADC: {raw_nh3}")
                json_parser.add_data("raw_nh3", raw_nh3)
                try:
                    if temp is not None and humidity is not None:
                        co2, nh3 = mq135.get_gas_concentrations(temp, humidity)
                    else:
                        co2, nh3 = mq135.get_gas_concentrations()
                    if nh3 is not None:
                        info_print(f"[{datetime_str}] MQ135 - Ammonia (NH3) concentration: {nh3:.3f} ppb")
                        json_parser.add_data("nh3", nh3)
                        if nh3 > NH3_THRESHOLD:
                            if ENABLE_KY006:
                                ky006.sound_alarm('nh3')
                            json_parser.add_data("nh3_alarm", True)
                        else:
                            json_parser.add_data("nh3_alarm", False)
                except Exception as e:
                    json_parser.add_data("error_mq135", f"Error reading MQ135 data: {e}")
                    error_print(f"Error reading MQ135 data: {e}")
            
            if ENABLE_L3GD20 and ENABLE_I2C:
                try:
                    gyro_data = l3gd20.gyro
                    json_parser.add_data("gyroscope.x", gyro_data[0])
                    json_parser.add_data("gyroscope.y", gyro_data[1])
                    json_parser.add_data("gyroscope.z", gyro_data[2])
                    info_print(f"[{datetime_str}] L3GD20 - Gyroscope: %.3f rad/s, %.3f rad/s, %.3f rad/s" % (gyro_data[0], gyro_data[1], gyro_data[2]))
                except Exception as e:
                    json_parser.add_data("error_l3gd20", f"Error reading L3GD20: {e}")
                    error_print(f"Error reading L3GD20: {e}")
                
            if ENABLE_LSM303D and ENABLE_I2C:
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
                    json_parser.add_data("error_lsm303d", f"Error reading LSM303D: {e}")
                    error_print(f"Error reading LSM303D: {e}")
                    
            if ENABLE_SCD41 and ENABLE_I2C:
                try:
                    if ENABLE_BME280 and pressure_hpa is not None:
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
                    json_parser.add_data("error_scd41", f"Error reading SCD41 data: {e}")
                    error_print(f"Error reading SCD41 data: {e}")
                    
            message = json_parser.get_json_message()
            info_print(f"JSON message: {message}")
            
            if ENABLE_UART_COMM:
                if message:
                    comm.send_message(message)
            
            time.sleep_ms(100)
            
            json_parser.clear_json_message()
            
        except Exception as e:
            error_print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
