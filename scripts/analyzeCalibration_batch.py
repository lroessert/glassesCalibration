"""
Batch submit multiple subjects to the analyzeCalibration script
"""

import os
from os.path import join
import pandas as pd
import subprocess
import math

parallel_processes = 9

conditions = []
for subj in ['014']:
    for glasses in ['Tobii']:
        for dist in ['1M', '2M', '3M']:
            for offset in ['0deg', '10Ldeg', '10Rdeg']:
                thisCond = '_'.join([subj, glasses, dist, offset])
                conditions.append(thisCond)

# Fill commands with commands for each file
commands = []
for cond in conditions:
    print('Submitting job for: {}'.format(cond))
    # Append python3 command to list
    commands.append('python3 analyzeCalibration.py ' + cond)

# Start parallel_processes amount of processes
for j in range(max(math.ceil(len(commands) / parallel_processes), 1)):
    try:
        procs = [subprocess.Popen(i, shell=True) for i in
                 commands[j * parallel_processes: min((j + 1) * parallel_processes, len(commands))]]
        for p in procs:
            p.wait()
    except:
        print('FAILED TO RUN:  {}'.format(commands))
