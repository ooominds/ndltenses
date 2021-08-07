#!/usr/bin/python3

####################
# Preliminary steps
####################

### Import necessary packages
import os
import pandas as pd
import numpy as np

### Set working directory
#TOP = '/media/adnane/HDD drive/Adnane/PostDoc_ooominds/Programming/English_Tense/Work_in_Birmingham/'
TOP = '/rds/projects/d/divjakd-ooo-machines/Users/tekevwe/English_tense/'
WD = TOP + 'Simulations/NDL_ngram_multiverbs/'
os.chdir(WD)

### Import local packages
import preprocessing as pr
import modelling as md
import evaluation as ev

### Define file paths
NGRAM_FILT_EVENTS_MULTI_VERBS_TRAIN = TOP + "Data_preparation/Data_shared/Eventfiles_forNDL/ngram_filtered_eventfile_multiverbs_train.gz"
NGRAM_FILT_EVENTS_MULTI_VERBS_VALID = TOP + "Data_preparation/Data_shared/Eventfiles_forNDL/ngram_filtered_eventfile_multiverbs_valid.gz"
#NGRAM_EVENTS_MULTI_VERBS_TRAIN = TOP + "Data_preparation/Data_shared/Eventfiles_forNDL/ngram_eventfile_multiverbs_train.gz"
#NGRAM_EVENTS_MULTI_VERBS_VALID = TOP + "Data_preparation/Data_shared/Eventfiles_forNDL/ngram_eventfile_multiverbs_valid.gz"
#NGRAM_EVENTS_MULTI_VERBS_TEST = TOP + "Data_preparation/Data_shared/Eventfiles_forNDL/ngram_eventfile_multiverbs_test.gz"
CUE_INDEX = WD + "Data/Cue_index_ngram_multiverbs.csv"
OUTCOME_INDEX = WD + "Data/Outcome_index_ngram_multiverbs.csv"
TEMP_DIR = WD + "Data/"
TUNING_PATH = WD + 'Results/grid_search_NDL_ngram_multiverbs.csv'

### Parameters to use
N_outcomes = 11 # number of most frequent outcomes to keep 
N_cues = 44676  # number of cues to keep (len(cue_to_index) below)
no_threads = 23 # Number of CPU cores to use

###################
# Data preparation
###################

# Import the cue index system
cue_to_index = pr.import_index_system(CUE_INDEX)
pr.display_dictionary(cue_to_index, start = 0, end = 5)
# {the: 1}
# {of: 2}
# {to: 3}
# {and: 4}
# {a: 5}

# Import the outcome index system
outcome_to_index = pr.import_index_system(OUTCOME_INDEX)
outcome_to_index
# {'future.perf': 1, 'future.prog': 2, 'future.simple': 3, 'past.perf': 4, 
# 'past.perf.prog': 5, 'past.prog': 6, 'past.simple': 7, 'present.perf': 8, 
# 'present.perf.prog': 9, 'present.prog': 10, 'present.simple': 11}

# Reverse the cue dictionary
index_to_cue = pr.reverse_dictionary(cue_to_index)
# Reverse the outcome dictionary
index_to_outcome = pr.reverse_dictionary(outcome_to_index)

#############
# NDL model
#############

### Parameter tuning using grid search 
p = {'lr': [0.00001, 0.00005, 0.0001, 0.0005, 0.001, 0.005, 0.01], # learning rate (x7)
     'epochs': [10], # number of iterations on the full set (x1)
     }
# => Total number of combinations: 1*7 = 7

### Grid search 
# md.grid_search(model = 'NDL',
#                data_train = NGRAM_EVENTS_MULTI_VERBS_TRAIN, 
#                data_valid = NGRAM_EVENTS_MULTI_VERBS_VALID, 
#                cue_index = cue_to_index, 
#                outcome_index = outcome_to_index,   
#                params = p, 
#                temp_dir = TEMP_DIR,
#                remove_temp_dir = False,
#                prop_grid = 1, 
#                shuffle_grid = False,
#                tuning_output_file = TUNING_PATH, 
#                num_threads = no_threads, 
#                seed = 1,
#                verbose = 2)

### If the filtered eventfiles have already been created
md.grid_search(model = 'NDL',
               data_train = NGRAM_FILT_EVENTS_MULTI_VERBS_TRAIN, 
               data_valid = NGRAM_FILT_EVENTS_MULTI_VERBS_VALID, 
               cue_index = None, 
               outcome_index = None,   
               params = p, 
               temp_dir = TEMP_DIR,
               remove_temp_dir = False,
               prop_grid = 1, 
               shuffle_grid = False,
               tuning_output_file = TUNING_PATH, 
               num_threads = no_threads, 
               seed = 1,
               verbose = 2) 


