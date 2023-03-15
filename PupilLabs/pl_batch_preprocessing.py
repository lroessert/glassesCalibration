import os
from os.path import join
import pandas as pd


# conditions
sessions = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
raw_dir = '/Users/leonardrossert/Documents/User_Study/2023-02-17/019/Raw_Data'
output_dir = '/Users/leonardrossert/Documents/User_Study/2023-02-17/019/Results'

for s in sessions:
    cmd_str = ' '.join(['python3', 'pl_preprocessing.py', join(raw_dir, str(s).zfill(3)), output_dir])
    print(cmd_str)

    try:
        os.system(cmd_str)
    except:
        print('failed on: {}'.format(cmd_str))
