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
            case 'AdHawk':combineSubjects.py
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

        if subj[0] == '0':
            print("Inside: ", subj[0])
            calibSummary_df['environment'] = 'Inside'
        else:
            print("Outside: ", subj[0])
            calibSummary_df['environment'] = 'Outside'

        return calibSummary_df


# loop through all subj/conditons
for subj in ['001', '002', '003', '004', '005', '006', '007', '008', '010', '011', '012', '013', '014', '015', '016',
             '017', '018', '019']:
    for glasses in ['PupilCore', 'PupilInvisible', 'AdHawk', 'Tobii']:
        for dist in ['1M', '2M', '3M']:
            for offset in ['0deg', '10Ldeg', '10Rdeg']:
                outsideSubj = subj.replace('0', '1', 1)

                thisCondInside = '_'.join([subj, glasses, dist, offset])
                thisCondOutside = '_'.join([outsideSubj, glasses, dist, offset])

                allSubjsInside_df = pd.concat(
                    [allSubjsInside_df, createSummary(allSubjsInside_df, subj, thisCondInside)])
                allSubjsInside_df = pd.concat(
                    [allSubjsInside_df, createSummary(allSubjsInside_df, outsideSubj, thisCondOutside)])

writeOutput(allSubjsInside_df, 'all_Inside_calibrationSummary.tsv')
