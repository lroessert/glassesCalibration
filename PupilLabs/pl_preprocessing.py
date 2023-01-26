"""
Format Pupil Labs data exported from Pupil Player 3.5.7.
Tested with Python 3.11, open CV 4.7.0

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
from os.path import join
import numpy as np
import pandas as pd
import csv
from itertools import chain

import gc
import msgpack

def preprocessData(inputDir, output_root):
    """
	Run all preprocessing steps for pupil lab data
	"""

    # Get the time and date from the info.csv file
    info_file = join(inputDir, 'export_info.csv')
    date_dir, time_dir = save_info_from_csv(info_file)

    # Create the output directory (if necessary)
    outputDir = create_output_directory(output_root, date_dir, time_dir)

    # Format the gaze data
    print('formatting gaze data...')
    gazeData_world, frame_timestamps = formatGazeData(inputDir)

    # write the gazeData to to a csv file
    print('writing file to csv...')
    csv_file = join(outputDir, 'gazeData_world.tsv')
    export_csv(csv_file, gazeData_world, frame_timestamps, outputDir)

    ### Compress and Move the world camera movie to the output
    print('copying world recording movie...')
    export_video(inputDir, outputDir)

def export_video(inputDir, outputDir):
    if not 'worldCamera.mp4' in os.listdir(outputDir):
        # compress
        print('compressing world camera video')
        cmd_str = ' '.join(
            ['ffmpeg', '-i', join(inputDir, 'world.mp4'), '-pix_fmt', 'yuv420p', join(inputDir, 'worldCamera.mp4')])
        print(cmd_str)
        os.system(cmd_str)

        # move the file to the output directory
        shutil.move(join(inputDir, 'worldCamera.mp4'), join(outputDir, 'worldCamera.mp4'))

def export_csv(csv_file, gazeData_world, frame_timestamps, outputDir):
    """
    Read date_dir, time_dir, worldCamRes_y which are stored in .csv file and return them.
    """
    export_range = slice(0, len(gazeData_world))
    with open(csv_file, 'w', encoding='utf-8', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_NONE)
        csv_writer.writerow(['{}\t{}\t{}\t{}\t{}'.format("timestamp",
                                                         "frame_idx",
                                                         "confidence",
                                                         "norm_pos_x",
                                                         "norm_pos_y")])
        for g in list(chain(*gazeData_world[export_range])):
            data = ['{:.3f}\t{:d}\t{:.1f}\t{:.3f}\t{:.3f}'.format(g["gaze_timestamp"] * 1000,
                                                                  g["world_idx"],
                                                                  g["confidence"],
                                                                  g["norm_pos_x"],
                                                                  1 - g["norm_pos_y"])]  # translate y coord to origin in top-left
            csv_writer.writerow(data)

    # write the frametimestamps to a csv file
    frameNum = np.arange(1, frame_timestamps.shape[0] + 1)
    frame_ts_df = pd.DataFrame({'frameNum': frameNum, 'timestamp': frame_timestamps})
    frame_ts_df.to_csv(join(outputDir, 'frame_timestamps.tsv'), sep='\t', float_format='%.3f', index=False)

def save_info_from_csv(info_file):
    """
    Read date_dir, time_dir, worldCamRes_y which are stored in .csv file and return them.
    """
    with open(info_file, 'r') as f:
        for line in f:
            if 'Export Date' in line:
                startDate = datetime.strptime(line.split(',')[1].strip('\n'), '%d.%m.%Y')
                date_dir = startDate.strftime('%Y_%m_%d')
            if 'Export Time' in line:
                startTime = datetime.strptime(line.split(',')[1].strip('\n'), '%H:%M:%S')
                time_dir = startTime.strftime('%H-%M-%S')

    return date_dir, time_dir

def create_output_directory(output_root, date_dir, time_dir):
    outputDir = join(output_root, date_dir, time_dir)
    if not os.path.isdir(outputDir):
        os.makedirs(outputDir)

    return outputDir

def formatGazeData(inputDir):
    """
    - load the pupil_data and timestamps
    - get the "gaze" fields from pupil data (i.e. the gaze lcoation w/r/t world camera)
    - sync gaze data with the world_timestamps array
    """
    # load pupil data
    info_file = join(inputDir, 'gaze_positions.csv')
    gaze_data_frame = load_pupil_data_from_csv(info_file)

    # load timestamps
    timestamps_path = join(inputDir, 'world_timestamps.npy')
    frame_timestamps = np.load(timestamps_path)

    # align gaze with world camera timestamps
    gaze_by_frame = correlate_data(gaze_data_frame, frame_timestamps)

    # Set start timestamp
    frame_timestamps = set_start_timeStamp(gaze_by_frame, frame_timestamps)

    return gaze_by_frame, frame_timestamps

def set_start_timeStamp(gaze_by_frame, frame_timestamps):
    """
    Make frame_timestamps relative to the first data timestamp
    """
    i = 0
    while i < len(gaze_by_frame):
        if len(gaze_by_frame[i]) != 0:
            start_timeStamp = gaze_by_frame[i][1]['gaze_timestamp']
            break
        i += 1
    frame_timestamps = (frame_timestamps - start_timeStamp) * 1000  # convert to ms

    return frame_timestamps

def load_pupil_data_from_csv(info_file):
    """
    Load the pupil_data from .csv file and return as dataFrame
    """
    # import .csv file as pandas dataframe
    gaze_data_frame = remove_columns_from_data_frame(pd.read_csv(info_file), ['base_data', 'gaze_point_3d_x',
                                                                              'gaze_point_3d_y', 'gaze_point_3d_z',
                                                                              'eye_center0_3d_x', 'eye_center0_3d_y',
                                                                              'eye_center0_3d_z', 'gaze_normal0_x',
                                                                              'gaze_normal0_y', 'gaze_normal0_z',
                                                                              'eye_center1_3d_x', 'eye_center1_3d_y',
                                                                              'eye_center1_3d_z', 'gaze_normal1_x',
                                                                              'gaze_normal1_y', 'gaze_normal1_z'])
    return gaze_data_frame

def remove_columns_from_data_frame(data_frame, remove_columns_list):
	try:
		for i in remove_columns_list:
			del data_frame[i]
	except KeyError as e:
		print('Error: No column with that name in dataframe:', e)

	return data_frame

def correlate_data(data, timestamps):
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
    timestamps = list(timestamps)
    data_by_frame = [[] for i in timestamps]

    frame_idx = 0
    data_index = 0

    data.sort_values(by=['gaze_timestamp'])

    while True:
        try:
            # get each row of data and convert from DataFrame to Dict
            datum = data.iloc[data_index].to_dict()

            # we can take the midpoint between two frames in time: More appropriate for SW timestamps
            ts = (timestamps[frame_idx] + timestamps[frame_idx + 1]) / 2.
        	# or the time of the next frame: More appropriate for Sart Of Exposure Timestamps (HW timestamps).
        	# ts = timestamps[frame_idx+1]
        except IndexError:
            # we might loose a data point at the end but we dont care
            break

        if datum['gaze_timestamp'] <= ts:
            datum['world_idx'] = frame_idx
            data_by_frame[frame_idx].append(datum)
            data_index += 1
        else:
            frame_idx += 1

    return data_by_frame


if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('inputDir', help='path to the raw pupil labs recording dir')
    parser.add_argument('outputDir',
                        help='output directory root. Raw data will be written to recording specific dirs within this directory')
    args = parser.parse_args()

    # check if input directory is valid
    if not os.path.isdir(args.inputDir):
        print('Invalid input dir: {}'.format(args.inputDir))
        sys.exit()
    else:
        # run preprocessing on this data
        preprocessData(args.inputDir, args.outputDir)
