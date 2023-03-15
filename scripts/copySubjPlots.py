"""
Move the individual subject plots (calibration raw and calibration summary) to a dedicated folder in the figs directory.
This will make for easy sharing down the line.
"""

# python 2/3 compatibility
from __future__ import division
from __future__ import print_function

import sys, os
import shutil
from os.path import join

data_dir = '../Results'
dest_dir = '../001'
if not os.path.isdir(dest_dir):
    os.makedirs(dest_dir)

## Loop through all subject data folders in the data dir
for subj in ['111']:
    for glasses in ['AdHawk']:
        for dist in ['1M', '2M', '3M']:
            for angle in ['0deg', '10Ldeg', '10Rdeg']:

                # path to this specific condition dir
                cond_dir = join(data_dir, '_'.join([subj, glasses, dist, angle]))

                output_prefix = '_'.join([subj, glasses, dist, angle])

                # Raw Plot:
                raw_src = join(cond_dir, 'calibration/calibrationPlot_raw.pdf')
                try:
                    shutil.copy(raw_src, join(dest_dir, (output_prefix + '_RAW.pdf')))
                except FileNotFoundError as e:
                    print(e)

                # Summary Plot:
                summary_src = join(cond_dir, 'calibration/calibrationPlot_summary.pdf')
                try:
                    shutil.copy(summary_src, join(dest_dir, (output_prefix + '_SUMMARY.pdf')))
                except FileNotFoundError as e:
                    print(e)

                print('copied ' + output_prefix)
