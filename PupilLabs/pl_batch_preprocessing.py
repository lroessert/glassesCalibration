import os
from os.path import join
import pandas as pd


# conditions
sessions = [0,1]
raw_dir = '/Users/leonardrossert/Documents/Eye_tracking_test/Pilot-Study_23-01-25/PupilLabs_Invisible'
output_dir = '/Users/leonardrossert/Documents/Eye_tracking_test/Results/Preprocessed_Results'

for s in sessions:
    cmd_str = ' '.join(['python3', 'pl_preprocessing.py', join(raw_dir, str(s).zfill(3)), output_dir])
    print(cmd_str)

    try:
        os.system(cmd_str)
    except:
        print('failed on: {}'.format(cmd_str))
