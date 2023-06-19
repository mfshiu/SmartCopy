import os

path = '/aaa/bbb/ccc'
head_folder = os.path.dirname(path)
print(head_folder)  # Output: 'aaa'