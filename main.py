from mqtt_handle import mqtt
from filter import kalman
from octorprint import OctorPrintAcquisition

def run():
    client = mqtt.connect_mqtt()
    client.loop_start()
    while True:
        try:
            temp, humi, pressure, acc, gyro, mag = mqtt.acquire_data_from_arduino()
            printing, bed_temperature, tool_temperature = OctorPrintAcquisition.get_printer_info()
            kalman_estimation_temperature = kalman.kalman_filter(temp, bed_temperature)
            mqtt.publish(client, temp, humi, pressure, acc, gyro, mag, kalman_estimation_temperature,bed_temperature, tool_temperature, printing)
        except Exception as e:
            print(e)
            client.loop_stop()


if __name__ == '__main__':
    run()
