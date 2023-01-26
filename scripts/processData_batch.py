"""
Batch submit multiple subjects to the proccessData script
"""

import os
from os.path import join
import pandas as pd

metadataTable_path = '/Users/leonardrossert/Documents/Eye_tracking_test/Pilot-Study_23-01-25/Results/Preprocessing/AdHawk'

conditions = 	['001_AdHawk_1M_0deg', '001_AdHawk_1M_10Ldeg', '001_AdHawk_1M_10Rdeg',
				'001_AdHawk_2M_0deg', '001_AdHawk_2M_10Ldeg', '001_AdHawk_2M_10Ldeg', '001_AdHawk_2M_10Rdeg',
				'001_AdHawk_3M_0deg', '001_AdHawk_3M_10Ldeg', '001_AdHawk_3M_10Rdeg']

# load the metadata table
metadata_df = pd.read_table(join(metadataTable_path, 'metadataTable.txt'), sep='\t', header=0)

# create new column that concatenates subfields to match condition formatting
metadata_df['condition'] = '00' + metadata_df['Subj'].map(str) + '_' + metadata_df['Glasses'] + '_' + metadata_df['Distance'] + '_' + metadata_df['Offset']

for cond in conditions:

	print('Submitting job for: {}'.format(cond))

	thisRow = metadata_df.loc[metadata_df.condition == cond]
	preprocDir = join(metadataTable_path, thisRow.Date.iloc[0], thisRow.Time.iloc[0])

	try:
		cmd_str = 'python3 processData.py ' + preprocDir + ' ' + cond
		print(cmd_str)
		os.system(cmd_str)
	except:
		print('FAILED TO RUN:  {}'.format(cond))
