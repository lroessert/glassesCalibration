import os
from os.path import join
import pandas as pd


# conditions
sessions = [1,2,3,4,5,6,7,8,9]
raw_dir = '/Users/leonardrossert/Documents/Eye_tracking_test/Pilot-Study_23-01-25/Raw_Data/AdHawk'
output_dir = '/Users/leonardrossert/Documents/Eye_tracking_test/Pilot-Study_23-01-25/Results/Preprocessing/AdHawk'

for s in sessions:
    cmd_str = ' '.join(['python3', 'ah_preprocessing.py', join(raw_dir, str(s).zfill(3)), output_dir])
    print(cmd_str)

    try:
        os.system(cmd_str)
    except:
        print('failed on: {}'.format(cmd_str))
