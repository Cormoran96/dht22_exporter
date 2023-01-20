#!/usr/bin/env python3
import sys
import time
import argparse
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import Adafruit_DHT

SENSOR = Adafruit_DHT.DHT22


def read_sensor(pin, name):
    humidity, temperature = Adafruit_DHT.read_retry(SENSOR, pin)
    print(humidity, temperature)
    if humidity is None or temperature is None:
        print("Error reading sensor data, skipping", file=sys.stderr)
        return

    if humidity > 200 or temperature > 200:
        print("Sensor data out of range, skipping", file=sys.stderr)
        return

    point = Point("dht22").tag("name", name).field("humidity", humidity).field("temperature_c", temperature).field("temperature_f", 9.0/5.0 * temperature + 32)
    return point

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g1", "--gpio1", dest="gpio1", type=int, required=True, help="GPIO pin number on which the first sensor is plugged in")
    parser.add_argument("-g2", "--gpio2", dest="gpio2", type=int, required=True, help="GPIO pin number on which the second sensor is plugged in")
    parser.add_argument("-i", "--interval", dest="interval", type=float, required=True, help="Interval sampling time, in minutes")
    parser.add_argument("-u", "--url", dest="url", type=str, required=True, help="URL of the InfluxDB instance")
    parser.add_argument("-t", "--token", dest="token", type=str, required=True, help="Token for authentication")
    parser.add_argument("-o", "--org", dest="org", type=str, required=True, help="Organization for InfluxDB")
    parser.add_argument("-b", "--bucket", dest="bucket", type=str, default="my-bucket", required=False, help="Bucket for data")

    args = parser.parse_args()

    interval = args.interval * 60  # convert minutes to seconds

    client = InfluxDBClient(url=args.url, token=args.token, org=args.org)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    while True:
        write_api.write(bucket=args.bucket, record=read_sensor(pin=args.gpio1, name="Bureau"))
        write_api.write(args.bucket, read_sensor(pin=args.gpio2, name="outside"))
        time.sleep(interval)

main()
