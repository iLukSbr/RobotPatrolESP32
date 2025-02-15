# Constants
I2C_SCL_PIN = 22
I2C_SDA_PIN = 21
I2C_FREQ = 115200

NH3_THRESHOLD = 80
CO2_THRESHOLD = 1000

# Flags to enable/disable components
ENABLE_I2C = False
ENABLE_BME280 = True
ENABLE_KY006 = True
ENABLE_DS1302 = False
ENABLE_KY026 = True
ENABLE_HCSR04 = {
    "front": True,
    "left": True,
    "right": True,
    "rear": True
}
ENABLE_HC020K = {
    "front_left": True,
    "front_right": True,
    "rear_left": True,
    "rear_right": True
}
ENABLE_INA219 = True
ENABLE_L3GD20 = True
ENABLE_LSM303D = True
ENABLE_MQ135 = True
ENABLE_SCD41 = True
ENABLE_UART_COMM = True

ENABLE_INFO_PRINT = True
ENABLE_ERROR_PRINT = True
