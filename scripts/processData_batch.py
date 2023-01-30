"""
Batch submit multiple subjects to the proccessData script
"""

import os
from os.path import join
import pandas as pd

metadataTable_path = '/Users/leonardrossert/Documents/Eye_tracking_test/Pilot-Study_23-01-30/Results/Preprocessing/PupilLabs_Invisible'

conditions = ['001_PupilInvisible_1M_0deg', '001_PupilInvisible_3M_0deg']

# Load the metadata.csv table to get date and time in relation to condition
metadata_df = pd.read_csv(join(metadataTable_path, 'metadataTable.csv'), sep = ';')

for cond in conditions:

	print('Submitting job for: {}'.format(cond))

	thisRow = metadata_df.loc[metadata_df.Condition == cond]
	preprocDir = join(metadataTable_path, thisRow.Date.iloc[0], thisRow.Time.iloc[0])

	try:
		cmd_str = 'python3 processData.py ' + preprocDir + ' ' + cond
		os.system(cmd_str)
	except:
		print('FAILED TO RUN:  {}'.format(cond))
