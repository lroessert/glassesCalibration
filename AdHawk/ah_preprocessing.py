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
		csv_writer.writerow(['{}\t{}\t{}\t{}'.format("timestamp",
							"frame_idx",
							"norm_pos_x",
							"norm_pos_y")])
		for g in list(chain(*gazeData_world[export_range])):
			data = ['{:.3f}\t{:d}\t{:.3f}\t{:.3f}'.format(g["Timestamp"]*1000,
								g["Frame_Index"],
								g["Image_X"],
								1-g["Image_Y"])]  # translate y coord to origin in top-left
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
		cmd_str = ' '.join(['ffmpeg', '-i', join(inputDir, 'session.mp4'), '-pix_fmt', 'yuv420p', join(inputDir, 'worldCamera.mp4')])
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

	# load timestamps: generate list with only timestamps for frames from gaze data
	frame_timestamps = generate_timestamp_list(gaze_data_frame.copy(), 0)

	# align gaze with world camera timestamps
	gaze_by_frame = correlate_data(gaze_data_frame, frame_timestamps)
	print(gaze_by_frame)
	# make frame_timestamps relative to the first data timestamp
	i = 0
	while i < len(gaze_by_frame):
		if len(gaze_by_frame[i]) != 0:
			start_timeStamp = gaze_by_frame[i][0]['Timestamp']
			break
		i += 1
	frame_timestamps = (frame_timestamps - start_timeStamp) * 1000

	return gaze_by_frame, frame_timestamps


def remove_columns_from_data_frame(data_frame, remove_columns_list):
	try:
		for i in remove_columns_list:
			del data_frame[i]
	except KeyError as e:
		print('Error: No column with that name in dataframe:', e)

	return data_frame


def correlate_data(gaze_data_frame, timestamps):
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

	data_by_frame = [[] for i in timestamps]
	gaze_data_frame.sort_values(by=['Timestamp'])

	frame_idx = 0
	data_index = 0

	while True:
		try:
			# get each row of data and convert from DataFrame to Dict
			datum = gaze_data_frame.iloc[data_index].to_dict()

			# we can take the midpoint between two frames in time: More appropriate for SW timestamps
			ts = (timestamps[frame_idx] + timestamps[frame_idx + 1]) / 2.

		except IndexError:
			# we might lose a data point at the end but we dont care
			break

		if datum['Timestamp'] <= ts:
			datum['Frame_Index'] = frame_idx
			data_by_frame[frame_idx].append(datum)

			data_index +=1
		else:
			frame_idx+=1
	return data_by_frame

def generate_timestamp_list(data, empty_value):
	"""
	Generates timestamp list from AdHawk gaze data. Fills frames with no timestamps with calculated average frame time.
	Returns frames as Numpy array.
	"""

	# get number of frames from DataFrame and create empty list with number of frames as length
	number_of_frames = data['Frame_Index'].max(axis=0)
	frame_timestamps = [[] for i in range(number_of_frames)]

	# fill list with timestamps from each frame
	for i in range(number_of_frames + 1):
		try:
			frame_timestamps[i-1] = data.loc[data.Frame_Index == i, 'Timestamp'].values[0]
		except IndexError:
			# no timestamp exists for that frame
			frame_timestamps[i-1] = empty_value

	#convert list to numpy array and fill empty_values
	frame_timestamps = fill_incomplete_timestamps(np.array(frame_timestamps), empty_value)

	return frame_timestamps

def fill_incomplete_timestamps(timestamps, empty_value):
	"""
	Fills empty frames with calculated average frame time.
	"""

	if list_contains_value(timestamps, empty_value):
		#create copy of list without zeroes
		timestamps_copy = np.delete(timestamps, np.where(timestamps == 0))

		#calculate average frame time
		average_frametime = np.average(np.diff(timestamps_copy))

		fill_list_values(timestamps, average_frametime, empty_value)

	# return list as numpy array
	return timestamps

def fill_list_values(list, difference, empty_value):
	"""
	Fills list in reverse from start-value. Subtracts difference from previous value.
	"""

	for i in range(len(list), 0, -1):
		if list[i-1] == empty_value:
			list[i-1] = list[i] - difference

	return list

def list_contains_value(list, value):
	"""
	Checks of list contains value and returns boolean values
	"""

	if value in list:
		return True
	else:
		return False


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