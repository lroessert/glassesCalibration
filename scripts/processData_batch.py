"""
Batch submit multiple subjects to the proccessData script
"""

import os
import subprocess
from os.path import join
import pandas as pd
from subprocess import Popen

metadataTable_path = '/Users/leonardrossert/Documents/User_Study/2023-01-31/002/Results'

conditions = ['002_PupilInvisible_1M_0deg', '002_PupilInvisible_1M_10Ldeg', '002_PupilInvisible_1M_10Rdeg',
			  '002_PupilInvisible_2M_0deg', '002_PupilInvisible_2M_10Ldeg', '002_PupilInvisible_2M_10Rdeg',
			  '002_PupilInvisible_3M_0deg', '002_PupilInvisible_3M_10Ldeg', '002_PupilInvisible_3M_10Rdeg',
			  '102_PupilInvisible_1M_0deg', '102_PupilInvisible_1M_10Ldeg', '102_PupilInvisible_1M_10Rdeg',
			  '102_PupilInvisible_2M_0deg', '102_PupilInvisible_2M_10Ldeg', '102_PupilInvisible_2M_10Rdeg',
			  '102_PupilInvisible_3M_0deg', '102_PupilInvisible_3M_10Ldeg', '102_PupilInvisible_3M_10Rdeg',
			  '002_PupilInvisible_1M_1', '002_PupilInvisible_1M_2', '002_PupilInvisible_1M_3',
			  '002_PupilInvisible_2M_1', '002_PupilInvisible_2M_2', '002_PupilInvisible_2M_3',
			  '002_PupilInvisible_3M_1', '002_PupilInvisible_3M_2', '002_PupilInvisible_3M_3']

parallel_processes = 10

# Load the metadata.csv table to get date and time in relation to condition
metadata_df = pd.read_csv(join(metadataTable_path, 'metadataTable.csv'), sep = ';')

# List for all the commands for processData
commands = []

# Fill commands with commands for each file
for cond in conditions:

	print('Submitting job for: {}'.format(cond))

	thisRow = metadata_df.loc[metadata_df.Condition == cond]
	preprocDir = join(metadataTable_path, thisRow.Date.iloc[0], thisRow.Time.iloc[0])

	commands.append('python3 processData.py ' + preprocDir + ' ' + cond)

for j in range(max(int(len(commands) / parallel_processes), 1)):
	try:
		procs = [subprocess.Popen(i, shell=True) for i in commands[j * parallel_processes: min((j + 1) * parallel_processes, len(commands))]]

		for p in procs:
			p.wait()
	except:
		print('FAILED TO RUN:  {}'.format(commands))
