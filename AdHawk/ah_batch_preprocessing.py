import os
from os.path import join
import pandas as pd


# conditions
sessions = [22]
raw_dir = '/Users/leonardrossert/Documents/User_Study/2023-02-08/015/Raw_Data'
output_dir = '/Users/leonardrossert/Documents/User_Study/2023-02-08/015/Results'

for s in sessions:
    cmd_str = ' '.join(['python3', 'ah_preprocessing.py', join(raw_dir, str(s).zfill(3)), output_dir])
    print(cmd_str)

    try:
        os.system(cmd_str)
    except:
        print('failed on: {}'.format(cmd_str))
