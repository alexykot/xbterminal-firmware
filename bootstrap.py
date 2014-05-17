#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import subprocess
import time
import sys
import os
import logging
import argparse

import requests

include_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, include_path)

# import xbterminal
# import xbterminal.defaults


XBTERMINAL_MAIN_PATH = os.path.join(include_path, 'xbterminal', 'main.so')
if os.path.exists(XBTERMINAL_MAIN_PATH):
    firmware_executable_path = XBTERMINAL_MAIN_PATH
else:
    firmware_executable_path = os.path.join(include_path, 'xbterminal', 'main.py')

# device_key = None
# try:
#     device_key_file_abs_path = os.path.abspath(os.path.join(xbterminal.defaults.PROJECT_ABS_PATH,
#                                                             xbterminal.defaults.DEVICE_KEY_FILE_PATH))
#     with open(device_key_file_abs_path, 'r') as device_key_file:
#         device_key = device_key_file.read().strip()
# except IOError:
#     print 'device key missing at path "{device_key_path}", exiting'.format(device_key_path=device_key_file_abs_path)
#     exit()
#
# server_url = None
# for server_url in xbterminal.defaults.REMOTE_SERVERS:
#     config_url = server_url + xbterminal.defaults.REMOTE_API_ENDPOINTS['config'].format(device_key=device_key)
#     try:
#         headers = xbterminal.defaults.EXTERNAL_CALLS_REQUEST_HEADERS
#         headers['Content-type'] = 'application/json'
#
#         result = requests.get(url=config_url, headers=headers)
#         if result.status_code == 200:
#             server_url = server_url
#             break

#     except requests.HTTPError:
#         print 'remote config {config_url} unreachable, trying next server'.format(config_url=config_url)
#
# if server_url is None:
#     print 'device key "{device_key}" is invalid, exiting'.format(device_key=device_key)
#     exit()
#
# def check_firmware(server_url, device_key):
#     firmware_check_url = '{server_url}{endpoint_path}'.format(
#         server_url=server_url,
#         endpoint_path=xbterminal.defaults.REMOTE_API_ENDPOINTS['firmware_check'].format(device_key=device_key))
#     headers = xbterminal.defaults.EXTERNAL_CALLS_REQUEST_HEADERS
#     headers['Content-type'] = 'application/json'
#
#     response = requests.get(url=firmware_check_url, headers=headers)
#     if response.status_code == 200:
#         response = response.json()
#         if response['next_firmware_version'] is not None:
#             return response['next_firmware_version']
#
#     return None
#
# def update_firmware(server_url, device_key, firmware_hash):
#     firmware_donwload_url = '{server_url}{endpoint_path}'.format(
#             server_url=server_url,
#             endpoint_path=xbterminal.defaults.REMOTE_API_ENDPOINTS['firmware_check'].format(device_key=device_key,
#                                                                                                 firmware_hash=firmware_hash))
#     tmp_filename = os.path.join('tmp', 'xbterminal_firmware_{hash}'.format(hash=firmware_hash))
#     headers = xbterminal.defaults.EXTERNAL_CALLS_REQUEST_HEADERS
#     headers['Content-type'] = 'application/json'
#
#     r = requests.get(firmware_donwload_url, stream=True, headers=headers)
#     with open(tmp_filename, 'wb') as f:
#         for chunk in r.iter_content(chunk_size=1024):
#             if chunk:
#                 f.write(chunk)
#                 f.flush()
#
#     os.rename(tmp_filename, XBTERMINAL_MAIN_PATH)
#
# def report_firmware_updated(device_key, firmware_hash):
#     firmware_report_url = '{server_url}{endpoint_path}'.format(
#             server_url=server_url,
#             endpoint_path=xbterminal.defaults.REMOTE_API_ENDPOINTS['firmware_updated'].format(device_key=device_key))
#     headers = xbterminal.defaults.EXTERNAL_CALLS_REQUEST_HEADERS
#     headers['Content-type'] = 'application/json'
#     data = {'firmware_version_hash': firmware_hash}
#     try:
#         requests.post(firmware_report_url, headers=headers, data=data)
#     except requests.HTTPError as error:
#         logging.exception(error)
#         pass

def run_firmware(idle=False):
    main_process = None
    while True:
        if not idle:
            try:
                main_process_running = main_process.poll() is None
            except AttributeError:
                main_process_running = False
            if not main_process_running:
                # (Re)start process
                try:
                    main_process = subprocess.Popen([firmware_executable_path])
                except Exception as error:
                    logging.exception(error)
        time.sleep(1)

        # if int(time.time()) % xbterminal.defaults.REMOTE_CONFIG_UPDATE_CYCLE == 0:
        #     new_version_hash = check_firmware(server_url, device_key)
        #     if new_version_hash is not None:
        #         update_firmware(server_url, device_key, new_version_hash)
        #         main_proc.kill()
        #         try:
        #             main_proc = subprocess.Popen([firmware_executable_path, ])
        #             main_proc_pid = main_proc.pid
        #             report_firmware_updated(device_key, new_version_hash)
        #         except Exception, error:
        #             logging.exception(error)

if __name__ == "__main__":
    argp = argparse.ArgumentParser()
    argp.add_argument("--idle", action="store_true")
    args = argp.parse_args()
    run_firmware(idle=args.idle)
