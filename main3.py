# encoding:utf-8 
# -*- coding: utf-8 -*-

import asyncio
from datetime import datetime as dt
import logging
import os
import requests
import shutil
import sys
import threading
import time
import schedule

import urllib

from config import LOG_DIR, SOURCE_ROOT, TARGET_ROOT
import helper 


_total_tasks = 0
_task_number = 0


def _check_dir_need_copy(dir, dir1):
    if not os.path.exists(dir1):
        os.makedirs(dir1)
        return True
    if not next(os.scandir(dir), None):
        return False
    if os.path.getmtime(dir) > os.path.getmtime(dir1):
        return True
    return False


def _check_file_need_copy(path0, path1):
    if not os.path.exists(path1):
        return '+'
    
    size0 = os.path.getsize(path0)
    if size0 == 0:
        return None
    
    delta = dt.fromtimestamp(os.path.getmtime(path0)) - dt.fromtimestamp(os.path.getmtime(path1))
    if (delta.total_seconds() > 1):
        return '*'
    
    if size0 != os.path.getsize(path1):
        return '#'
    
    return None


def _shorten_path(path, max_width):
    if (len(path) <= max_width):
        return path
    n = max_width // 2
    return f"{path[:n]}...{path[-n:]}"


async def copy_dir(dir0, files):
    # print(f"{dir0}, {files}")
    global _total_tasks, _task_number
    _task_number += 1
    dir_number = _task_number
    file_number = 0

    dir1 = dir0.replace(SOURCE_ROOT, TARGET_ROOT)
    if _check_dir_need_copy(dir0, dir1):
        # i = 0
        for file in files:
            path0 = os.path.join(dir0, file)
            path1 = os.path.join(dir1, file)
            if symbol := _check_file_need_copy(path0, path1):
                file_number += 1
                logger.debug(f"{symbol} {dir_number}-{file_number}/{_total_tasks} {_shorten_path(path1, 120)}")
                try:
                    shutil.copy(path0, dir1)
                except Exception as ex:
                    logger.error(f"{ex.args[1]}, {path1}")


async def main_async():
    copy_tasks = []

    try:
        for dir, _, files in os.walk(SOURCE_ROOT):
            copy_tasks.append(copy_dir(dir, files))

        global _total_tasks, _task_number
        _total_tasks = len(copy_tasks)
        _task_number = 0
        logger.info(f"Total Tasks: {_total_tasks}")

        await asyncio.gather(*copy_tasks)
    except Exception as ex:
        print(ex)


def _send_out_message(msg):
    def send_to_mqtt(msg):
        topic = "smartcopy"
        msg = urllib.parse.quote(msg)
        msg = msg.replace('/', '\\')
        url = f"https://gigoo.co/mqtt/{topic}/{msg}"
        # print(f"url: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(f"Request failed with status code {response.status_code}")
    
    thread1 = threading.Thread(target=send_to_mqtt, args=(msg,))
    thread1.start()


def run_smartcopy():
    msg = f"""\n********************
SmartCopy starts at {dt.now()}
SOURCE_ROOT: {SOURCE_ROOT}
TARGET_ROOT: {TARGET_ROOT}
********************
"""
    logger.info(f"\n{msg}")
    _send_out_message(msg)

    asyncio.run(main=main_async())

    stop_time = time.perf_counter()
    elapsed_time = stop_time - start_time
    msg = f"""SmartCopy ends at {dt.now()}
Elapsed time: {elapsed_time} seconds
"""
    logger.info(msg)
    _send_out_message(msg)


if __name__ == '__main__':
    global logger

    arguments = sys.argv[1:]
    start_time = time.perf_counter()

    if len(arguments) >= 2:
        SOURCE_ROOT = arguments[0]
        TARGET_ROOT = arguments[1]
    if len(arguments) >= 3:
        LOG_DIR = arguments[2]

    logger = helper.init_logging(log_dir=LOG_DIR, log_level=logging.DEBUG)

    schedule.every().day.at("12:17").do(run_smartcopy)
    while True:
        print(".", end="", flush=True)
        schedule.run_pending()
        time.sleep(5)
