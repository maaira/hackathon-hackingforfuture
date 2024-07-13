import json
import time
import paho.mqtt.client as mqtt
from bluepy import btle  
import time
import struct
import datetime
import calendar

broker = '172.16.25.224'
port = 1883
topic = "rasp/sensors/"
 
mac_address = "6f:10:fb:58:28:90"#"11:9b:62:1e:37:f0" 
service_uuid = "12345678-1234-5678-1234-56789abcdef0"
uuid_dict = {
    "temperature": "7e45d293-9b2a-4812-899a-b3a111fa0f67",
    "humidity": "33e6cf6f-f1f3-44c5-8dd5-bb0cb2d9e2f8",
    "pressure": "f327aae5-349f-4c7f-a812-e60c7cfc5968",
    "accelerometer": "12345678-1234-5678-1234-56789abcdef1",
    "gyroscope": "d43306de-76e7-4b06-971c-9d8cc499290e",
    "magnetometer": "4bdf3152-ffe6-4d6f-8a28-c43a5e8c1bc2"
}

print("Connecting…")
nano_sense = btle.Peripheral(mac_address)
print("Discovering Services…")
_ = nano_sense.services
bleService = nano_sense.getServiceByUUID(service_uuid)
print("Discovering Characteristics…")
_ = bleService.getCharacteristics()

     
def byte_array_to_int(value):
    # Raw data is hexstring of int values, as a series of bytes, in little endian byte order
    # values are converted from bytes -> bytearray -> int
    # e.g., b'\xb8\x08\x00\x00' -> bytearray(b'\xb8\x08\x00\x00') -> 2232
    value = bytearray(value)
    value = int.from_bytes(value, byteorder="little", signed=True)
    return value

def read_temp_humi_press(service, uuid):
    data_char = service.getCharacteristics(uuid)[0]
    data = data_char.read()
    data = byte_array_to_int(data)
    return round(data/100, 2)

def read_imu(service, uuid):
    data_char = service.getCharacteristics(uuid)[0]
    data = data_char.read()
    x, y, z = struct.unpack('fff', data)
    return {
            "x": float(round(x*100)),
            "y": float(round(y*100)),
            "z": float(round(z*100))
            }

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}\n")
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.on_connect = on_connect
    client.username_pw_set("andorinha", "andorinha")
    client.connect(broker, port)
    return client

def acquire_data_from_arduino():
    temp = read_temp_humi_press(bleService, uuid_dict['temperature'])
    humi = read_temp_humi_press(bleService, uuid_dict['humidity'])
    pressure = read_temp_humi_press(bleService, uuid_dict['pressure'])
    acc = read_imu(bleService, uuid_dict['accelerometer'])
    gyro = read_imu(bleService, uuid_dict['gyroscope'])
    mag = read_imu(bleService, uuid_dict['magnetometer'])
    return temp, humi, pressure, acc, gyro, mag


def publish(client, temp, humi, pressure, acc, gyro, mag, kalman_estimation_temperature,bed_temperature, tool_temperature, printing):
    time.sleep(1)
    msg = {
        "printing": str(printing),
        "estimate_table_temperature": kalman_estimation_temperature,
        "octor_print_table_temperature":bed_temperature,
        "octor_print_tool_temperature": tool_temperature,
        "arduino_table_temperature": temp,
        "arduino_humidity": humi,
        "arduino_pressure": pressure,
        "arduino_accelerometer_x": acc['x'],
        "arduino_accelerometer_y": acc['y'],
        "arduino_accelerometer_z": acc['z'],
        "arduino_gyroscope_x": gyro['x'],
        "arduino_gyroscope_y": gyro['y'],
        "arduino_gyroscope_z": gyro['z'],
        "arduino_magnetometer_x": mag['x'],
        "arduino_magnetometer_y": mag['y'],
        "arduino_magnetometer_z": mag['z'],
        "timestamp": calendar.timegm(datetime.datetime.utcnow().utctimetuple())   #unix utc ts
    }
    print(msg)
    result = client.publish(topic, json.dumps(msg))
    status = result[0]
    if status == 0:
        print(f"Sent `{msg}` to topic `{topic}`")
    elif KeyboardInterrupt:
        print(f"interrupt")
    else:
        print(f"Failed to send message to topic {topic}")
    

