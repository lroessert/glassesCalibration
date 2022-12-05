"""
Format raw AdHawk data.
Tested with Python 3.6, open CV 3.2
The raw input data will be copied to a new directory stored in ./data.
The output directory will be  named according to [mo-day-yr]/[hr-min-sec] of the original creation time format.
The output directory will contain:
	- worldCamera.mp4: the video from the point-of-view scene camera on the glasses
	- frame_timestamps.tsv: table of timestamps for each frame in the world
	- gazeData_world.tsv: gaze data, where all gaze coordinates are represented w/r/t the world camera
"""

# python 2/3 compatibility
from __future__ import division
from __future__ import print_function

import sys, os, shutil
import argparse
from datetime import datetime
from datetime import date
from os.path import join
import numpy as np
import pandas as pd
import csv
import json
from itertools import chain

import gc
import msgpack

def preprocessData(inputDir, output_root):
	"""
	Run all preprocessing steps for pupil lab data
	"""
	### Prep output directory
	#TODO: Get date and time from gaze_data.csv file
	info_file = join(inputDir, 'meta_data.json')  	# get the timestamp from the meta_data.json file
	with open(info_file, 'r') as f:
		meta_data = json.load(f)

	# save current date and time
	current_date = date.today()
	date_dir = current_date.strftime('%Y_%m_%d')
	current_time = datetime.now()
	time_dir = current_time.strftime("%H-%M-%S")

	worldCamRes_y = 1280
	worldCamRes_x = 720

	# create the output directory (if necessary)
	outputDir = join(output_root, date_dir, time_dir)
	if not os.path.isdir(outputDir):
		os.makedirs(outputDir)

	### Format the gaze data
	print('formatting gaze data...')
	gazeData_world, frame_timestamps = formatGazeData(inputDir)

	# write the gazeData to to a csv file
	print('writing file to csv...')
	csv_file = join(outputDir, 'gazeData_world.tsv')
	export_range = slice(0, len(gazeData_world))
	with open(csv_file, 'w', encoding='utf-8', newline='') as csvfile:
		csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_NONE)
		csv_writer.writerow(['{}\t{}\t{}\t{}\t{}'.format("timestamp",
							"frame_idx",
							"confidence",
							"norm_pos_x",
							"norm_pos_y")])
		for g in list(chain(*gazeData_world[export_range])):
			data = ['{:.3f}\t{:d}\t{:.1f}\t{:.3f}\t{:.3f}'.format(g["timestamp"]*1000,
								g["frame_idx"],
								g["confidence"],
								g["norm_pos"][0],
								1-g["norm_pos"][1])]  # translate y coord to origin in top-left
			csv_writer.writerow(data)

	# write the frametimestamps to a csv file
	frameNum = np.arange(1, frame_timestamps.shape[0]+1)
	frame_ts_df = pd.DataFrame({'frameNum': frameNum, 'timestamp':frame_timestamps})
	frame_ts_df.to_csv(join(outputDir, 'frame_timestamps.tsv'), sep='\t', float_format='%.3f', index=False)

	### Compress and Move the world camera movie to the output
	print('copying world recording movie...')
	if not 'worldCamera.mp4' in os.listdir(outputDir):
		# compress
		print('compressing world camera video')
		cmd_str = ' '.join(['ffmpeg', '-i', join(inputDir, 'world.mp4'), '-pix_fmt', 'yuv420p', join(inputDir, 'worldCamera.mp4')])
		print(cmd_str)
		os.system(cmd_str)

		# move the file to the output directory
		shutil.move(join(inputDir, 'worldCamera.mp4'), join(outputDir, 'worldCamera.mp4'))


def formatGazeData(inputDir):
	"""
	- load the pupil_data and timestamps
	- get the "gaze" fields from pupil data (i.e. the gaze lcoation w/r/t world camera)
	- sync gaze data with the world_timestamps array
	"""

	# load gaze data
	info_file = join(inputDir, 'gaze_data.csv')
	# import gaze_data.csv file as pandas dataframe
	gaze_data_frame = remove_columns_from_data_frame(pd.read_csv(info_file), ['Gaze_X', 'Gaze_Y', 'Gaze_Z', 'Gaze_X_Right', 'Gaze_Y_Right', 'Gaze_Z_Right', 'Gaze_X_Left', 'Gaze_Y_Left', 'Gaze_Z_Left', 'Vergence', 'Screen_X', 'Screen_Y'])

	# align gaze with world camera timestamps
	gaze_by_frame = correlate_data(gaze_data_frame)

	print(gaze_by_frame[1][1])

	# make frame_timestamps relative to the first data timestamp
	start_timeStamp = gaze_by_frame[1][1]['timestamp']
	frame_timestamps = (frame_timestamps - start_timeStamp) * 1000 # convert to ms

	return gaze_by_frame, frame_timestamps


def remove_columns_from_data_frame(data_frame, remove_columns_list):
	try:
		for i in remove_columns_list:
			del data_frame[i]
	except KeyError as e:
		print('Error: No column with that name in dataframe:', e)

	return data_frame


def correlate_data(gaze_data_frame):
	'''
	data:  list of data :
		each datum is a dict with at least:
			timestamp: float
	timestamps: timestamps list to correlate  data to
	this takes a data list and a timestamps list and makes a new list
	with the length of the number of timestamps.
	Each slot contains a list that will have 0, 1 or more assosiated data points.
	Finally we add an index field to the datum with the associated index
	'''
	print(gaze_data_frame)
	rows = gaze_data_frame.shape[0]
	data_by_frame = [[] for i in range(rows)]

	gaze_data_frame.sort_values(by=['Timestamp'])

	timestamps_data_frame = generate_timestamp_dataframe(gaze_data_frame)
	print(gaze_data_frame)

	frame_idx = timestamps_data_frame._get_value(0, 'Frame_Index')
	data_index = 0


	while True:
		try:
			datum = gaze_data_frame.iloc[data_index].to_dict()
			#print('datum: ', datum)

			#print('frame_idx: ', frame_idx + 1)
			ts_row_number = timestamps_data_frame.loc[timestamps_data_frame['Frame_Index'] == (frame_idx + 1)].index[0]
			ts = timestamps_data_frame._get_value(ts_row_number, 'Timestamp')
			#print('ts: ', ts)

		except IndexError:
			# we might loose a data point at the end but we dont care
			break

		if datum['Timestamp'] <= ts:
			datum['Frame_Index'] = frame_idx
			data_by_frame[frame_idx].append(datum)
			data_index +=1
		else:
			frame_idx+=1

	return data_by_frame

def generate_timestamp_dataframe(data):
	# remove columns not needed for timestamp dataframef
	timestamps = remove_columns_from_data_frame(data, ['Image_X', 'Image_Y'])
	# remove duplicate timestamps for frames
	# only first timestamp of frame is saved
	timestamps = timestamps.drop_duplicates(subset=['Frame_Index'], keep='first')
	# reset indeces after deleting rows
	timestamps.reset_index(drop=True, inplace=True)

	return timestamps

if __name__ == '__main__':
	# parse arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('inputDir', help='path to the raw pupil labs recording dir')
	parser.add_argument('outputDir', help='output directory root. Raw data will be written to recording specific dirs within this directory')
	args = parser.parse_args()

	# check if input directory is valid
	if not os.path.isdir(args.inputDir):
		print('Invalid input dir: {}'.format(args.inputDir))
		sys.exit()
	else:

		# run preprocessing on this data
		preprocessData(args.inputDir, args.outputDir)