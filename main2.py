# encoding:utf-8 

import asyncio
from datetime import datetime as dt
from datetime import timedelta
import logging
import os
import shutil
import sys
import time

from config import LOG_DIR, SOURCE_ROOT, TARGET_ROOT
import helper 


def _check_dir_need_copy(dir, dir1):
    # print(f'dir.lower():{dir.lower()}')
    # dd = dir.lower()
    # if any(dd.endswith(x) for x in IGNORE_DIR_NAMES):
    #     return False
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
        # print(f'\nWhy copy: Target file not exist')
        return '+'
    
    size0 = os.path.getsize(path0)
    if size0 == 0:
        return None
    
    delta = dt.fromtimestamp(os.path.getmtime(path0)) - dt.fromtimestamp(os.path.getmtime(path1))
    if (delta.total_seconds() > 1):
        # print(f'Why copy: source time > target time: {delta.total_seconds()}')
        return '*'
    
    if size0 != os.path.getsize(path1):
        # print(f'Why copy: source size: {size0} > target size: {size1}')
        return '#'
    
    return None


def _shorten_path(path, max_width):
    if (len(path) <= max_width):
        return path
    n = max_width // 2
    return f"{path[:n]}...{path[-n:]}"


async def copy_dir(dir0, files):
    # print(f"{dir0}, {files}")

    dir1 = dir0.replace(SOURCE_ROOT, TARGET_ROOT)
    # dir_base = os.path.basename(os.path.normpath(dir0))
    if _check_dir_need_copy(dir0, dir1):
        # i = 0
        for file in files:
            path0 = os.path.join(dir0, file)
            path1 = os.path.join(dir1, file)
            if symbol := _check_file_need_copy(path0, path1):
                # i += 1
                logger.debug(f"{symbol} {_shorten_path(path1, 120)}")
                # print(f"[{dir_base}]-{i} {_shorten_path(path1, 100)}")
                # print(f"[{dir_base}]-{i} C: {_shorten_path(path0, 50)} -> {_shorten_path(path1, 50)}")
                try:
                    shutil.copy(path0, dir1)
                except Exception as ex:
                    logger.error(f"ERROR: {ex.args[1]}")
                    # logger.exception(f"ERROR: {ex.args[1].splitlines()[-1]}")
                    # logging.exception(f"ERROR: {path0}\n{str(ex)}")


# def copy_dir1(dir0, files):
#     print(f"{dir0}, {files}")

#     dir1 = dir0.replace(SOURCE_ROOT, TARGET_ROOT)
#     if not os.path.exists(dir1):
#         os.mkdir(dir1)
#     for file in files:
#         path0 = os.path.join(dir0, file)
#         # path1 = os.path.join(dir1, file)
#         shutil.copy(path0, dir1)


async def main_async():
    copy_tasks = []

    for dir, _, files in os.walk(SOURCE_ROOT):
        copy_tasks.append(copy_dir(dir, files))

    await asyncio.gather(*copy_tasks)


# def main_sync():
#     for dir, _, files in os.walk(SOURCE_ROOT):
#         copy_dir1(dir, files)


# SOURCE_ROOT = /Users/xumingfang/Work
# TARGET_ROOT = /Volumes/Home/WorkA/
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

    logger.info(f"\n********************")
    logger.info(f'SmartCopy starts at {dt.now()}')
    logger.info(f"********************")
    logger.info(f'SOURCE_ROOT: {SOURCE_ROOT}')
    logger.info(f'TARGET_ROOT: {TARGET_ROOT}')

    asyncio.run(main=main_async())
    # main_sync()

    stop_time = time.perf_counter()
    elapsed_time = stop_time - start_time
    logger.info(f'SmartCopy ends at {dt.now()}')
    logger.info(f"Elapsed time: {elapsed_time} seconds")
