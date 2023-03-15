"""
Batch submit multiple subjects to the proccessData script
"""

import os
import subprocess
from os.path import join
import pandas as pd
import math

metadataTable_path = '../Results'

conditions = ['007_Tobii_1M_10Ldeg']

parallel_processes = 9

# Load the metadata.csv table to get date and time folder in relation to condition
metadata_df = pd.read_csv(join(metadataTable_path, 'metadataTable.csv'), sep=';')

# List for all the commands for processData
commands = []

# Fill commands with commands for each file
for cond in conditions:
    # print('Submitting job for: {}'.format(cond))
    try:
        # Search folder for condition with metadata_df
        thisRow = metadata_df.loc[metadata_df.Condition == cond]
        preprocDir = join(metadataTable_path, thisRow.Date.iloc[0], thisRow.Time.iloc[0])

        # Append python3 command to list
        commands.append('python3 processData.py ' + preprocDir + ' ' + cond)
    except IndexError as e:
        print(e)

# Start parallel_processes amount of processes
for j in range(max(math.ceil(len(commands) / parallel_processes), 1)):
    try:
        procs = [subprocess.Popen(i, shell=True) for i in
                 commands[j * parallel_processes: min((j + 1) * parallel_processes, len(commands))]]
        for p in procs:
            p.wait()
    except:
        print('FAILED TO RUN:  {}'.format(commands))
