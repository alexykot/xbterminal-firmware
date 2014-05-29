#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import json
import subprocess
import time
import sys
import os
import logging
import argparse


import requests

include_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, include_path)

logging.basicConfig(
    format="%(asctime)s %(name)s [%(levelname)s] :: %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler])
logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.WARNING)
logger = logging.getLogger("bootstrap.py")

import xbterminal
import xbterminal.defaults
import xbterminal.helpers.configs
from xbterminal.exceptions import ConfigLoadError

xbterminal.defaults.PROJECT_ABS_PATH = include_path
xbterminal.helpers.configs.load_local_state()

from xbterminal.defaults import (
    PROJECT_LOCAL_PATH,
    REMOTE_SERVERS,
    REMOTE_API_ENDPOINTS,
    EXTERNAL_CALLS_REQUEST_HEADERS,
    REMOTE_CONFIG_UPDATE_CYCLE
)


def check_firmware(server_url, device_key):
    firmware_check_url = server_url + REMOTE_API_ENDPOINTS['firmware_check'].format(
        device_key=device_key)
    headers = EXTERNAL_CALLS_REQUEST_HEADERS.copy()
    headers['Content-type'] = 'application/json'
    try:
        response = requests.get(url=firmware_check_url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as error:
        logger.exception(error)
    return None


def update_firmware(server_url, device_key, firmware_hash):
    firmware_download_url = server_url + REMOTE_API_ENDPOINTS['firmware_download'].format(device_key=device_key,
                                                                                          firmware_hash=firmware_hash)
    tmp_filename = os.path.join('/tmp', 'xbterminal_firmware_{firmware_hash}.tar.gz'.format(firmware_hash=firmware_hash))
    headers = EXTERNAL_CALLS_REQUEST_HEADERS.copy()
    headers['Content-type'] = 'application/json'
    try:
        response = requests.get(firmware_download_url, stream=True, headers=headers)
        with open(tmp_filename, 'wb') as tmp_file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    tmp_file.write(chunk)
                    tmp_file.flush()
        subprocess.check_call(["tar", "-xzf", tmp_filename])
        installer = os.path.join(os.path.splitext(tmp_filename)[0], "update_installer.py")
        subprocess.check_call([installer])
    except Exception as error:
        logger.exception(error)
        return False
    else:
        return True


def report_firmware_updated(server_url, device_key, firmware_hash):
    firmware_report_url = server_url + REMOTE_API_ENDPOINTS['firmware_updated'].format(
        device_key=device_key)
    headers = EXTERNAL_CALLS_REQUEST_HEADERS.copy()
    headers['Content-type'] = 'application/json'
    try:
        requests.post(firmware_report_url, headers=headers,
                      data=json.dumps({'firmware_version_hash': firmware_hash}))
    except requests.exceptions.RequestException as error:
        logger.exception(error)
        return False
    else:
        return True


def run_firmware(idle=False, updates_enabled=True):
    device_key = xbterminal.helpers.configs.get_device_key()
    server_url = None
    main_process = None
    new_version_hash = None
    last_check = 0
    while True:
        if updates_enabled and time.time() - last_check > REMOTE_CONFIG_UPDATE_CYCLE:
            # Check for updates
            logger.info("checking for updates...")
            last_check = time.time()
            if server_url is None:
                try:
                    server_url, _ = xbterminal.helpers.configs.choose_remote_server(device_key)
                except ConfigLoadError:
                    continue
            updates_data = check_firmware(server_url, device_key)
            new_version_hash = updates_data.get('next_firmware_version_hash')
            if new_version_hash is not None:
                logger.info("current version: {cur_ver}, next version: {next_ver}, installing ...".format(
                    cur_ver=updates_data['current_firmware_version'],
                    next_ver=updates_data['next_firmware_version'],))
                try:
                    main_process.kill()
                except AttributeError:
                    pass
                result = update_firmware(server_url, device_key, new_version_hash)
                if result:
                    logger.info("firmware updated to {version}".format(version=updates_data['next_firmware_version']))
                else:
                    logger.error("update failed")
        if not idle:
            # Check if process is running
            try:
                main_process_running = main_process.poll() is None
            except AttributeError:
                main_process_running = False
            if not main_process_running:
                # (Re)start process
                main_executable = os.path.join(include_path, PROJECT_LOCAL_PATH, "main.so")
                if not os.path.exists(main_executable):
                    main_executable = os.path.join(include_path, PROJECT_LOCAL_PATH, "main.py")
                logger.info("starting {0}...".format(main_executable))
                try:
                    main_process = subprocess.Popen([main_executable])
                except Exception as error:
                    logger.exception(error)
                else:
                    if new_version_hash is not None:
                        result = report_firmware_updated(server_url, device_key, new_version_hash)
                        if not result:
                            logger.warning("report failed")
                        else:
                            new_version_hash = None
                            logger.info("report sent")
        time.sleep(2)


if __name__ == "__main__":
    argp = argparse.ArgumentParser()
    argp.add_argument("--idle", action="store_true")
    argp.add_argument("--disable-updates", action="store_true")
    args = argp.parse_args()
    run_firmware(idle=args.idle, updates_enabled=not args.disable_updates)
