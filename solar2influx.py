#!/usr/bin/env python3
#
# Required environment variables (no defaults):
# - INFLUXDB_HOSTNAME: hostname or ip-address of influxdb server
# - INFLUXDB_TOKEN: token with write-access to influxdb bucket
# - INFLUXDB_ORG: influxdb organization
# - INVERTER_HOSTNAME: hostname or ip-address of GoodWe solar inverter
# Optional environment variables:
# - INFLUXDB_PORT: TCP-port of InfluxDB server, default: 8086
# - INFLUXDB_BUCKET: bucketname to store data in InfluxDB, default: solar
# - SCAN_INTERVAL: interval in seconds to access the inverter, default: 30
# Optional environment variables for debugging:
# - ENABLE_LOGGING: true (log data to stdout) or false (no data to stdout, default)
# - ENABLE_INFLUXDB: true (write data to InfluxDB, default) or false (do not write to InfluxDB)

import os
import sys
import time
import asyncio
import goodwe
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


async def get_runtime_data(inverterhost):
    # runtime_data example:
    # {
    #     'timestamp': datetime.datetime(2024, 8, 25, 20, 28, 24),
    #     'vpv1': 188.6,
    #     'ipv1': 0.1,
    #     'ppv1': 18,
    #     'vpv2': 188.0,
    #     'ipv2': 0.0,
    #     'ppv2': 0,
    #     'ppv': 18,
    #     'pv2_mode': 2,
    #     'pv2_mode_label': 'PV panels connected, producing power',
    #     'pv1_mode': 2,
    #     'pv1_mode_label': 'PV panels connected, producing power',
    #     'vgrid': 233.0,
    #     'igrid': 1.0,
    #     'fgrid': 49.99,
    #     'pgrid': 148,
    #     'vgrid2': 233.8,
    #     'igrid2': 0.9,
    #     'fgrid2': 50.0,
    #     'pgrid2': 139,
    #     'vgrid3': 232.8,
    #     'igrid3': 1.0,
    #     'fgrid3': 49.98,
    #     'pgrid3': 145,
    #     'grid_mode': 1,
    #     'grid_mode_label': 'Connected to grid',
    #     'total_inverter_power': 433,
    #     'active_power': -28,
    #     'grid_in_out': 0,
    #     'grid_in_out_label': 'Idle',
    #     'reactive_power': 0,
    #     'apparent_power': 0,
    #     'backup_v1': 20.3,
    #     'backup_i1': 0.0,
    #     'backup_f1': 49.99,
    #     'load_mode1': 0,
    #     'backup_p1': 0,
    #     'backup_v2': 20.2,
    #     'backup_i2': 0.0,
    #     'backup_f2': 50.0,
    #     'load_mode2': 0,
    #     'backup_p2': 0,
    #     'backup_v3': 20.0,
    #     'backup_i3': 0.1,
    #     'backup_f3': 49.98,
    #     'load_mode3': 0,
    #     'backup_p3': 0,
    #     'load_p1': 36,
    #     'load_p2': 311,
    #     'load_p3': 114,
    #     'backup_ptotal': 1,
    #     'load_ptotal': 461,
    #     'ups_load': 0,
    #     'temperature_air': 38.4,
    #     'temperature_module': 0.0,
    #     'temperature': 35.0,
    #     'function_bit': 16416,
    #     'bus_voltage': 654.1,
    #     'nbus_voltage': 325.8,
    #     'vbattery1': 211.4,
    #     'ibattery1': 1.9,
    #     'pbattery1': 418,
    #     'battery_mode': 2,
    #     'battery_mode_label': 'Discharge',
    #     'warning_code': 0,
    #     'safety_country': 2,
    #     'safety_country_label': 'DE LV with PV',
    #     'work_mode': 1,
    #     'work_mode_label': 'Normal (On-Grid)',
    #     'operation_mode': 0,
    #     'error_codes': 0,
    #     'errors': '',
    #     'e_total': 5141.6,
    #     'e_day': 14.5,
    #     'e_total_exp': 5472.5,
    #     'h_total': 10014,
    #     'e_day_exp': 14.9,
    #     'e_total_imp': 26.8,
    #     'e_day_imp': 0.0,
    #     'e_load_total': 3974.5,
    #     'e_load_day': 8.7,
    #     'e_bat_charge_total': 1505.7,
    #     'e_bat_charge_day': 3.5,
    #     'e_bat_discharge_total': 957.0,
    #     'e_bat_discharge_day': 2.1,
    #     'diagnose_result': 33554496,
    #     'diagnose_result_label': 'Discharge Driver On, PF value set',
    #     'house_consumption': 464,
    #     'battery_bms': 255,
    #     'battery_index': 304,
    #     'battery_status': 1,
    #     'battery_temperature': 23.0,
    #     'battery_charge_limit': 25,
    #     'battery_discharge_limit': 25,
    #     'battery_error_l': 0,
    #     'battery_soc': 73,
    #     'battery_soh': 98,
    #     'battery_modules': 4,
    #     'battery_warning_l': 0,
    #     'battery_protocol': 261,
    #     'battery_error_h': 0,
    #     'battery_error': '',
    #     'battery_warning_h': 0,
    #     'battery_warning': '',
    #     'battery_sw_version': 0,
    #     'battery_hw_version': 0,
    #     'battery_max_cell_temp_id': 0,
    #     'battery_min_cell_temp_id': 0,
    #     'battery_max_cell_voltage_id': 0,
    #     'battery_min_cell_voltage_id': 0,
    #     'battery_max_cell_temp': 0.0,
    #     'battery_min_cell_temp': 0.0,
    #     'battery_max_cell_voltage': 0.0,
    #     'battery_min_cell_voltage': 0.0,
    #     'commode': 5,
    #     'rssi': 101,
    #     'manufacture_code': 10,
    #     'meter_test_status': 0,
    #     'meter_comm_status': 1,
    #     'active_power1': 113,
    #     'active_power2': -169,
    #     'active_power3': 33,
    #     'active_power_total': -22,
    #     'reactive_power_total': 259,
    #     'meter_power_factor1': 0.457,
    #     'meter_power_factor2': -0.61,
    #     'meter_power_factor3': 0.213,
    #     'meter_power_factor': -0.044,
    #     'meter_freq': 49.99,
    #     'meter_e_total_exp': 2440.23,
    #     'meter_e_total_imp': 931.75,
    #     'meter_active_power1': 113,
    #     'meter_active_power2': -169,
    #     'meter_active_power3': 33,
    #     'meter_active_power_total': -22,
    #     'meter_reactive_power1': 175,
    #     'meter_reactive_power2': 125,
    #     'meter_reactive_power3': -41,
    #     'meter_reactive_power_total': 259,
    #     'meter_apparent_power1': 248,
    #     'meter_apparent_power2': -279,
    #     'meter_apparent_power3': 150,
    #     'meter_apparent_power_total': -678,
    #     'meter_type': 1,
    #     'meter_sw_version': 80
    # }

    try:
        inverter = await goodwe.connect(inverterhost)
        runtime_data = await inverter.read_runtime_data()
        return runtime_data
    except Exception as e:
        print(f"Warning: error reading from solar inverter {inverterhost}: {e}", file=sys.stderr)

def write_influx(influxserver, influxport, influxorg, influxtoken,influxbucket, enable_logging, enable_influxdb, inverterdata):

    if enable_influxdb == "TRUE":
        try:
            influxdbclient = InfluxDBClient(url=f"http://{influxserver}:{influxport}", token=influxtoken, org=influxorg)
            write_api = influxdbclient.write_api(write_options=SYNCHRONOUS)
            record = [
                Point("vpv1").field("volt", inverterdata.get('vpv1')),
                Point("ipv1").field("ampere", inverterdata.get('vpv1')),
                Point("ppv1").field("watt", inverterdata.get('ppv1')),
                Point("vpv2").field("volt", inverterdata.get('vpv2')),
                Point("ipv2").field("ampere", inverterdata.get('vpv2')),
                Point("ppv2").field("watt", inverterdata.get('ppv2')),
                Point("vline1").field("volt", inverterdata.get('vline1')),
                Point("vgrid1").field("volt", inverterdata.get('vgrid1')),
                Point("igrid1").field("ampere", inverterdata.get('igrid1')),
                Point("fgrid1").field("hz", inverterdata.get('fgrid1')),
                Point("pgrid1").field("watt", inverterdata.get('pgrid1')),
                Point("ppv").field("watt", inverterdata.get('ppv')),
                Point("h_total").field("hours", inverterdata.get('h_total')),
                Point("e_total").field("kwh", inverterdata.get('e_total')),
                Point("e_day").field("kwh", inverterdata.get('e_day')),
                Point("temperature").field("degrees", inverterdata.get('temperature')),
                Point("battery_soc").field("percent", inverterdata.get('battery_soc')),
                Point("battery_soh").field("percent", inverterdata.get('battery_soh')),
                Point("battery_index").field("watt", inverterdata.get('battery_index')),
                Point("battery_temperature").field("degrees", inverterdata.get('battery_temperature')),
                Point("battery_charge_limit").field("ampere", inverterdata.get('battery_charge_limit')),
                Point("battery_discharge_limit").field("ampere", inverterdata.get('battery_discharge_limit')),
                Point("battery_error_l").field("error", inverterdata.get('battery_error_l')),
                Point("battery_error_h").field("error", inverterdata.get('battery_error_h')),
                Point("battery_warning_l").field("warning", inverterdata.get('battery_warning_l')),
                Point("battery_warning_h").field("warning", inverterdata.get('battery_warning_h')),
                Point("load_ptotal").field("watt", inverterdata.get('load_ptotal')),
                Point("house_consumption").field("watt", inverterdata.get('house_consumption')),
                Point("e_bat_charge_day").field("kwh", inverterdata.get('e_bat_charge_day')),
                Point("e_bat_discharge_day").field("kwh", inverterdata.get('e_bat_discharge_day')),
                Point("e_load_day").field("kwh", inverterdata.get('e_load_day')),
                Point("e_load_total").field("kwh", inverterdata.get('e_load_total')),
                Point("e_bat_charge_total").field("kwh", inverterdata.get('e_bat_charge_total')),
                Point("e_bat_discharge_total").field("kwh", inverterdata.get('e_bat_discharge_total')),
                Point("battery_status").field("status", inverterdata.get('battery_status')),
            ]
            write_api.write(bucket=influxbucket, org=influxorg, record=record)
            influxdbclient.__del__()
        except Exception as e:
            print(f"Fatal error accessing InfluDB: {e}", file=sys.stderr)

    if enable_logging == "TRUE":
        print(f"Date + time: {inverterdata.get('timestamp')}")
        print(f"PV1 Voltage (V) (vpv1): {inverterdata.get('vpv1')}")
        print(f"PV1 Current (A) (ipv1): {inverterdata.get('ipv1')}")
        print(f"PV1 Power (W) (ppv1): {inverterdata.get('ppv1')}")
        print(f"PV2 Voltage (V) (vpv2): {inverterdata.get('vpv2')}")
        print(f"PV2 Current (A) (ipv2): {inverterdata.get('ipv2')}")
        print(f"PV2 Power (W) (ppv2): {inverterdata.get('ppv2')}")
        print(f"On-grid L1-L2 Voltage (V) (vline1): {inverterdata.get('vline1')}")
        print(f"Grid Voltage (V) (vgrid1): {inverterdata.get('vgrid1')}")
        print(f"Grid Current (A) (igrid1): {inverterdata.get('igrid1')}")
        print(f"Grid Frequency (Hz) (fgrid1): {inverterdata.get('fgrid1')}")
        print(f"Grid Power (W) (pgrid1): {inverterdata.get('pgrid1')}")
        print(f"PV Power (W) (ppv): {inverterdata.get('ppv')}")
        print(f"Temperature (degrees celcius) (temperature): {inverterdata.get('temperature')}")
        print(f"Total hours (hours) (h_total): {inverterdata.get('h_total')}")
        print(f"Total load (kWH) (e_total): {inverterdata.get('e_total')}")
        print(f"Today's load (kWH) (e_day): {inverterdata.get('e_day')}")
        if enable_influxdb == "TRUE":
            print(f"==> Data written to InfluxDB host {influxserver}")


def main():

    # Required environment variables
    try:
        influxserver = os.environ['INFLUXDB_HOSTNAME']
        influxorg = os.environ['INFLUXDB_ORG']
        influxtoken = os.environ['INFLUXDB_TOKEN']
        inverterhost = os.environ['INVERTER_HOSTNAME']
    except KeyError as e:
        print(f"Fatal error: variable not set: {e}", file=sys.stderr)
        sys.exit(1)

    # Variables with a default value
    influxport = os.environ.get('INFLUXDB_PORT', 8086)
    influxbucket = os.environ.get('INFLUXDB_BUCKET', 'solar')
    enable_logging = str(os.environ.get('ENABLE_LOGGING', 'false')).upper()
    enable_influxdb = str(os.environ.get('ENABLE_INFLUXDB', 'true')).upper()
    scan_interval = os.environ.get('SCAN_INTERVAL', 30)

    while True:
        
        ret = os.system(f"ping -c 3 -W 3000 {inverterhost} >/dev/null 2>&1")
        if ret == 0:
            try:
                inverterdata = asyncio.run(get_runtime_data(inverterhost))
            except Exception as e:
                print(f"Error reading from solar inverter {inverterhost}: {e}", file=sys.stderr)
            try:
                write_influx(influxserver, influxport, influxorg, influxtoken, influxbucket, enable_logging, enable_influxdb, inverterdata)
            except Exception as e:
                print(f"Error writing to influxdb server {influxserver}: {e}", file=sys.stderr)
        else:
            ts = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
            print(f"{ts} - Error connecting to solar inverter {inverterhost}", file=sys.stderr)
        
        time.sleep(scan_interval)


if __name__ == "__main__":
    main()

