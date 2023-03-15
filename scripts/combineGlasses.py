"""
Combine the calibrationSummary.tsv files for all
conditions for all subjects
"""
from __future__ import print_function
from __future__ import division
import os
from os.path import join
import pandas as pd

data_dir = '/Users/leonardrossert/Documents/User_Study/Recordings/Results'
analysis_dir = '/Users/leonardrossert/Documents/User_Study/Results/analysis/Glasses'

allSubjsInside_df = pd.DataFrame()
allSubjsOutside_df = pd.DataFrame()


def writeOutput(allSubjs_df, name):
    # write the output
    allSubjs_df.to_csv(join(analysis_dir, name),
                       index=False,
                       sep='\t',
                       float_format='%.4f')


def loadCalibSummary(data_dir, subj, thisCond):
    calibSummary_path = join(data_dir, thisCond, 'calibration/calibrationSummary.tsv')
    try:
        calibSummary_df = pd.read_table(calibSummary_path, sep='\t')
        return calibSummary_df
    except FileNotFoundError as e:
        print(e)


def createSummary(allSubjs_df, subj, thisCond):
    # load the calib summary for this condition
    calibSummary_df = loadCalibSummary(data_dir, subj, thisCond)

    # add condition cols to the summmary
    if type(calibSummary_df) != None.__class__:

        calibSummary_df['subj'] = subj
        match glasses:
            case 'PupilInvisible':
                model = 'Pupil Labs Invisible'
            case 'PupilCore':
                model = 'Pupil Labs Core'
            case 'AdHawk':
                model = 'AdHawk MindLink'
            case 'Tobii':
                model = 'Tobii Pro Glasses 2'

        if glasses == 'PupilInvisible':
            model = 'Pupil Labs Invisible'  # reformat pupil labs to include space
        else:
            model = glasses

        calibSummary_df['glasses'] = model
        calibSummary_df['dist'] = dist
        calibSummary_df['offset'] = offset

        calibSummary_df['condition'] = thisCond

        return calibSummary_df


# loop through all subj/conditons
for subj in ['003', '010', '011', '015', '018']:
    for glasses in ['Adhawk']:
        for dist in ['1M', '2M', '3M']:
            for offset in ['0deg', '10Ldeg', '10Rdeg']:
                subjOutside = subj.replace('0', '1', 1)
                thisCondInside = '_'.join([subj, glasses, dist, offset])
                thisCondOutside = '_'.join([subjOutside, glasses, dist, offset])

                allSubjsInside_df = pd.concat(
                    [allSubjsInside_df, createSummary(allSubjsInside_df, subj, thisCondInside)])
                allSubjsOutside_df = pd.concat(
                    [allSubjsOutside_df, createSummary(allSubjsOutside_df, subjOutside, thisCondOutside)])

writeOutput(allSubjsInside_df, 'all_AdHawk_Inside_calibrationSummary.tsv')
writeOutput(allSubjsOutside_df, 'all_AdHawk_Outside_calibrationSummary.tsv')
