import os
from os.path import join
import pandas as pd


# load the file mapping table
#df = pd.read_table('./data/Tobii_fileName_mapping.txt', sep='\t', header=0)

TobiiNames = ['jirucdk', 'poe7kfs']
Segments = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
raw_dir = '/Users/leonardrossert/Documents/User_Study/2023-02-07/014/Raw_Data'
output_dir = '/Users/leonardrossert/Documents/User_Study/2023-02-07/014/Results'

for d in TobiiNames:
	for s in Segments:
		cmd_str = ' '.join(['python3', 'tobii_preprocessing.py', join(raw_dir, d, 'segments/', s), output_dir])
		print(cmd_str)
		try:
			os.system(cmd_str)
		except:
			print('failed on: {}'.format(cmd_str))
