import os
import shutil
import threading
import time

#TODO: Log to file
#TODO: 檔案會重覆被copy, 一直copy不乾淨
#TODO: 統計已拷貝的夾檔數
#TODO: 確認retry_copy能順利運作

source_root = "/Volumes/HM800/Work"
# source_root = "/Users/xumingfang/Work"
# source_root = "/Volumes/Home/WorkA"
# source_root = "/Volumes/Disk4T/Work"
# source_root = "/Users/xumingfang/Documents"
# source_root = "/Users/xumingfang/Pictures"

# target_root = "/Volumes/HM800/Work"
# target_root = "/Volumes/HM800/可愛小妍/Eric"
# target_root = "/Volumes/HM800/可愛小妍/Eric/圖片"
# target_root = "/Volumes/Disk4T/Work"
target_root = "/Volumes/Home/WorkA"

# source_root = "/Users/xumingfang/Documents"
# target_root = "/Volumes/Home/可愛小妍/Eric"

curr_copy_file_threads = 0
max_copy_file_threads = 10000
curr_copy_dir_threads = 0
max_copy_dir_threads = 1000

running = True
retry_files = []
retry_files_lock = threading.Lock()

def get_dir_folders_files(dir):
    folders = []
    files = []
    for item in os.scandir(dir):
        if item.is_dir():
            folders.append(item.name)
        else:
            files.append(item.name)
    return folders, files

def check_dir_need_copy(dir, dir1):
    if ("/temp" in dir.lower()):
        return False
    if not os.path.exists(dir1):
        os.makedirs(dir1)
        return True
    if not next(os.scandir(dir), None):
        return False
    if os.path.getmtime(dir) > os.path.getmtime(dir1):
        return True
    return False

def check_file_need_copy(path0, path1):
    if not os.path.exists(path1):
        return True
    if os.path.getmtime(path0) > os.path.getmtime(path1):
        return True
    if os.path.getsize(path0) != os.path.getsize(path1):
        return True
    return False

def shorten_path(path, max_width):
    if (len(path) <= max_width):
        return path
    n = max_width // 2
    return f"{path[:n]}...{path[-n:]}"

# def shorten_path(path, width=30, filename_width=17):
#     if (len(path) <= width):
#         return path
#     name = os.path.basename(path)
#     if len(name) >= filename_width:
#         return f"{path[:width-3-filename_width]}...{name[:filename_width]}"
#     else:
#         return f"{path[:width-3-len(name)]}...{name}"

def copy_file(path0, path1):
    global curr_copy_file_threads
    global retry_files
    global retry_files_lock
    try:
        shutil.copyfile(path0, path1)
    except Exception as ex:
        retry_files_lock.acquire()
        retry_files.append((path0, path1))
        size = len(retry_files)
        retry_files_lock.release()
        print(f"ERROR: (copy_file) curr_copy_file_threads:{curr_copy_file_threads} retry_files:{size} {ex}")
    # time.sleep(1)
    curr_copy_file_threads -= 1

def copy_dir(dir, files, i):
    global curr_copy_dir_threads
    global curr_copy_file_threads
    try:
        print(f"[{i}]\r", end='')
        dir1 = dir.replace(source_root, target_root)
        if (check_dir_need_copy(dir, dir1)):
            print(f"[{i:03}] Dir: {dir}")
            for file in files:
                path0 = os.path.join(dir, file)
                path1 = os.path.join(dir1, file)
                if (check_file_need_copy(path0, path1)):
                    print(f"[{i:03}] C: {shorten_path(path0, 50)} -> {shorten_path(path1, 50)}")
                    while curr_copy_file_threads >= max_copy_file_threads:
                        time.sleep(0.1)
                    try:
                        curr_copy_file_threads += 1
                        threading.Thread(target=copy_file, args=(path0, path1)).start()
                    except Exception as ex:
                        curr_copy_file_threads -= 1
                        print(f"ERROR: (copy_dir1) {ex}")
    except Exception as ex:
        print(f"ERROR: (copy_dir) {ex}")
    curr_copy_dir_threads -= 1

def retry_copy():
    global running
    global retry_files
    global retry_files_lock
    files = ()

    while running or len(retry_files) > 0:
        retry_files_lock.acquire()
        if len(retry_files):
            files = retry_files.pop()
        retry_files_lock.release()

        if files:
            print(f"(retry_copy) from:{files[0]} to:{files[1]}")
            copy_file(files[0], files[1])

        if len(retry_files) == 0:
            time.sleep(0.1)

threading.Thread(target=retry_copy).start()

i = 0
for dir, folders, files in os.walk(source_root):
    dir0 = dir
    while curr_copy_dir_threads >= max_copy_dir_threads:
        time.sleep(0.1)
    curr_copy_dir_threads += 1
    try:
        threading.Thread(target=copy_dir, args=(dir0, files.copy(), i)).start()
    except Exception as ex:
        curr_copy_dir_threads -= 1
        print(f"ERROR: (main) {ex}")
    i += 1

running = False
print("Wait all copy done.")
while curr_copy_dir_threads > 0 or curr_copy_file_threads > 0:
    print(f"dir: {curr_copy_dir_threads} file: {curr_copy_file_threads}\r", end='')
    time.sleep(3)

print("\nCopy complete.")

