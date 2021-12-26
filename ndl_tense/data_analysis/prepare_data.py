#!/usr/bin/python3

####################
# Preliminary steps
####################

### Import necessary packages
import os
import pandas as pd
import numpy as np
import sys

### Import local packages
from ndl_tense.simulations import preprocessing as pr
from ndl_tense.simulations import modelling as md
from ndl_tense.simulations import evaluation as ev

from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix

from tqdm import tqdm
tqdm.pandas()

import logging
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

###################
# Data preparation
##################

### Find the kth top choice
def find_top_tense(row, i, cols):
    row_np = np.array(row[0:11].tolist())
    row_np_sorted = np.argsort(-row_np)
    return cols[row_np_sorted[i]]

def calculate_activation_support(x, activ_cols):
    for j in range(activ_cols):
        name = "{}.activ.support".format(activations_df.columns[j])
        sub = (activations_df.iloc[x, [y for y in activ_cols if y > j or y < j]])
        activations_df[name] = min([activations_df.iloc[x,j] - s for s in sub])


### Add other_tense label
def ifelse_tense(s, list_to_check):
    if s not in list_to_check:
        res = "other"
    else: 
        res = s
    return res


def create_predictions_df(activations_df):
    ### Prepare the predictions from the activations dataframe 
    activ_cols = activations_df.columns.tolist()
    for j in range(activ_cols):
        name = "{}.activ.support".format(activations_df.columns[j])
        activations_df[name] = ""
    activations_df['PredictedTense1'] = activations_df.progress_apply(lambda x: find_top_tense(x, 0, activ_cols), axis=1) 
    activations_df['PredictedTense2'] = activations_df.progress_apply(lambda x: find_top_tense(x, 1, activ_cols), axis=1) 
    activations_df['PredictedTense3'] = activations_df.progress_apply(lambda x: find_top_tense(x, 2, activ_cols), axis=1)
    activations_df['PredictedTensePart'] = activations_df['PredictedTense1'].progress_apply(lambda s: s.split('.')[0]) 
    activations_df['PredictedAspectPart'] = activations_df['PredictedTense1'].progress_apply(lambda s: s.split('.')[1]) 
    predictions_df = activations_df[['PredictedTense1', 'PredictedTense2', 'PredictedTense3', 'PredictedTensePart', 'PredictedAspectPart']]
    return(predictions_df)



def create_results_df(RESULTS_TEST, RESULT_ALL_TEST, predictions_df):
    results_df = pd.read_csv(RESULTS_TEST)
    ### Prepare the corpus dataframe before merging it with the predictions dataframe
    results_df = results_df[['SentenceID', 'Sentence', 'FilteredCues', 'Tense', 'VerbForm', 
                            'MainVerb', 'Position', 'Infinitive', 'VerbOrder', 'SentenceLength', 
                            'NumOfVerbs', 'NumOfVerbsOriginal']]
    results_df['TensePart'] = results_df['Tense'].progress_apply(lambda s: s.split('.')[0]) 
    results_df['AspectPart'] = results_df['Tense'].progress_apply(lambda s: s.split('.')[1])

    ### Merging the two previous dataframes
    results_df = pd.concat([results_df, predictions_df], axis=1)

    ### Add accuracy measures
    results_df['Accuracy'] = results_df.progress_apply(lambda x: int(x.loc['Tense'] == x.loc['PredictedTense1']), axis = 1)
    results_df['AccuracyTopTwo'] = results_df.progress_apply(lambda x: int(x.loc['Tense'] in (x.loc['PredictedTense1'], x.loc['PredictedTense2'])), axis = 1)
    results_df['AccuracyTopThree'] = results_df.progress_apply(lambda x: int(x.loc['Tense'] in (x.loc['PredictedTense1'], 
                                                                                    x.loc['PredictedTense2'], 
                                                                                    x.loc['PredictedTense3'])), axis = 1)
    results_df['AccuracyTensePart'] = results_df.progress_apply(lambda x: int(x.loc['TensePart'] == x.loc['PredictedTensePart']), axis = 1)
    results_df['AccuracyAspectPart'] = results_df.progress_apply(lambda x: int(x.loc['AspectPart'] == x.loc['PredictedAspectPart']), axis = 1)
    results_df.to_csv(RESULTS_ALL_TEST, sep = ',', index = False)
    # Accuracy per tense-aspect combination
    
    cmat = confusion_matrix(results_df['Tense'], results_df['PredictedTense1'], labels = list(outcome_to_index.keys())) # Confusion matrix
    pmat = cmat.diagonal()/cmat.sum(axis=1) # Confusion matrix in terms of proportions
    if VERBOSE:
        logger.INFO({index_to_outcome[j+1]:round(pmat[j],4) for j in range(len(pmat))})


    results_df = pd.read_csv(RESULTS_ALL_TEST)
    results_df.head()
    results_df.shape # (351431, 24)


    ### Add Accuracy1 (accuracy for the top choice from the model), 
    ### Accuracy2 (accuracy for the second to top choice from the model) and Accuracy3
    results_df['Accuracy1'] = results_df.progress_apply(lambda x: int(x.loc['Tense'] == x.loc['PredictedTense1']), axis = 1)
    results_df['Accuracy2'] = results_df.progress_apply(lambda x: int(x.loc['Tense'] == x.loc['PredictedTense2']), axis = 1)
    results_df['Accuracy3'] = results_df.progress_apply(lambda x: int(x.loc['Tense'] == x.loc['PredictedTense3']), axis = 1)

    results_df['Tense_compact'] = results_df['Tense'].progress_apply(lambda x: ifelse_tense(x, ['present.simple', 'past.simple']))
    results_df.to_csv(RESULTS_ALL_TEST, sep = ',', index = False)


def run(DATA_ANALYSIS_FILES, VERBOSE = True):

    ### Set the max width of a column
    pd.set_option('display.max_colwidth', 120)
    pd.set_option('display.max_columns', 10)
    np.set_printoptions(precision=4)

    ### Set the max width of a column
    pd.set_option('display.max_colwidth', 120)
    pd.set_option('display.max_columns', 10)
    np.set_printoptions(precision=4)

    RESULTS_TEST =  DATA_ANALYSIS_FILES[0]
    RESULT_ALL_TEST = DATA_ANALYSIS_FILES[1]
    ACTIVATION_TEST = DATA_ANALYSIS_FILES[2]
    OUTCOME_INDEX =  DATA_ANALYSIS_FILES[3]
    # Import the outcome index system
    outcome_to_index = pr.import_index_system(OUTCOME_INDEX)
    # Reverse the outcome dictionary
    index_to_outcome = pr.reverse_dictionary(outcome_to_index)
    activations_df = pd.read_csv(ACTIVATION_TEST)
    predictions_df = create_predictions_df(activations_testset_ngrams_multiverbs)
    create_results_df(RESULTS_TEST, RESULT_ALL_TEST, predictions_df)
    if VERBOSE:
        logger.INFO("Step 1: Preparation for data analysis complete")


