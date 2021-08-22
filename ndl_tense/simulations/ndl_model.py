#!/usr/bin/python3

####################
# Preliminary steps
####################

### Import necessary packages
import pandas as pd
import numpy as np
import xarray as xr
import logging
logging.basicConfig(level=logging.DEBUG)

import time

from pyndl.ndl import ndl
from keras.models import Sequential, load_model, save_model
from pyndl.activation import activation
from sklearn.metrics import confusion_matrix
# from tqdm import tqdm
# tqdm.pandas()

### Import local packages
import ndl_tense.simulations.preprocessing as pr
import ndl_tense.simulations.modelling as md
import ndl_tense.simulations.evaluation as ev

# ### To reload packages
# import imp
# imp.reload(pr)
# imp.reload(md)
# imp.reload(ev)

### Set the max width of a column
pd.set_option('display.max_colwidth', 120)
pd.set_option('display.max_columns', 10)
np.set_printoptions(precision=4)

### Parameters to use
N_outcomes = 11 # number of most frequent outcomes to keep 
N_cues = 44676  # number of cues to keep (len(cue_to_index) below)
#no_threads = int(os.environ['SLURM_NTASKS']) # if you are requesting ressources from bluebear 
no_threads = 15 # Number of CPU cores to use
#chunk_size = 20000 # Number of lines to use seperately for computing the activation matrix

###################
# Data preparation
###################

#####################################################
# NDL model (with evaluation on the validation set)
#####################################################

# ### Build a simple NDL
# p = {'epochs': 1, # number of iterations on the full set 
#     'lr': 0.0001}

# # Model fitting
# NDL_history, NDL_model = md.train_NDL(data_train = NGRAM_FILT_EVENTS_ONE_VERB_TRAIN, 
#                                       data_valid = NGRAM_FILT_EVENTS_ONE_VERB_VALID,  
#                                       #cue_index = cue_to_index, 
#                                       #outcome_index = outcome_to_index, 
#                                       temp_dir = TEMP_DIR,
#                                       #remove_temp_dir = False,
#                                       #chunksize = chunk_size,
#                                       num_threads = no_threads, 
#                                       verbose = 2,
#                                       params = p)

# # Save the weights and training history
# md.export_model(model = NDL_model, path = MODEL_PATH)  # create a HDF5 file 
# md.export_history(history_dict = NDL_history, path = HISTORY_PATH)
# #del NDL_model, NDL_history_dict  # delete the existing model and history dictionary

############
# NDL model 
############

def train_model(NGRAM_FILT_EVENTS_MULTI_VERBS_TRAIN, NGRAM_FILT_EVENTS_MULTI_VERBS_VALID, TEMP_DIR,
                MODEL_PATH, WEIGHTS_PATH, cue_to_index, outcome_to_index):
    """
    
    ----
    PARAMETERS
    ----

    ----
    RETURN
    ----
    """

    ### Build a simple NDL
    p = {'epochs': 10, # number of iterations on the full set 
        'lr': 0.0001}

    # Model fitting
    NDL_model = md.train_NDL(data_train = NGRAM_FILT_EVENTS_MULTI_VERBS_TRAIN, 
                            data_valid = NGRAM_FILT_EVENTS_MULTI_VERBS_VALID,  
                            cue_index = cue_to_index,
                            outcome_index = outcome_to_index,
                            temp_dir = TEMP_DIR,
                            #remove_temp_dir = False,
                            #chunksize = chunk_size,
                            num_threads = no_threads, 
                            verbose = 0,
                            params = p)

    # Save the weights and training history
    #md.export_model(model = NDL_model, path = "%s.h5"%(MODEL_PATH))  # create a HDF5 file 
    #NDL_model.save("%s.h5"%(MODEL_PATH)) #save_model(model = NDL_model, path = )
    #NDL_model.save(MODEL_PATH) #save_model(model = NDL_model, path = )
    NDL_model.weights.to_netcdf("%s.nc"%(WEIGHTS_PATH)) 
    #md.export_history(history_dict = NDL_history, path = HISTORY_PATH)
    #del NDL_model, NDL_history_dict  # delete the existing model and history dictionary
    return(NDL_model)


################################

# #### Estimate the weight matrix
# # Train ndl to get the weight matrix 
# start_weight = time.time()
# weights = ndl(events = NGRAM_FILT_EVENTS_ONE_VERB_TRAIN,
#               alpha = 0.0001, 
#               betas = (1, 1),
#               method ='openmp',
#               number_of_threads = no_threads,
#               remove_duplicates = True,
#               temporary_directory = TEMP_DIR,
#               verbose = False)
# logging.info('Weight mat estimated in %.0fs\n' % ((time.time() - start_weight)))

# ### Model object
# NDL_model = md.NDLmodel(weights)

# # Save the weights and training history
# md.export_model(model = NDL_model, path = MODEL_PATH)  # create a HDF5 file 

#############
# Evaluation
#############

def evaluate(TENSE_SET, ACTIVATION_TEST, NGRAM_EVENTS_MULTI_VERBS_TEST,
             NDL_model, outcome_to_index, index_to_outcome):
    """
    
    ----
    PARAMETERS
    ----

    ----
    RETURN
    ----
    """

    # ### Load the model and training history
    # NDL_model = md.import_model(MODEL_PATH)
    # # NDL_history_dict = md.import_history(path = HISTORY_PATH)

    ### Check the weight matrix
    #list_tenses =  NDL_model.weights.coords["outcomes"].values.tolist()
    # ['present.simple', 'past.simple', 'past.perf', 'present.perf', 'future.simple', 
    # 'future.perf', 'past.prog', 'present.prog', 'future.prog', 'present.perf.prog', 
    # 'past.perf.prog']

    ### Check some weights
    #NDL_model.weights.loc[{'outcomes': 'past.simple', 'cues': 'yesterday'}].values.item()
    # 

    tense_list_NDL = NDL_model.weights.coords['outcomes'].values.tolist()
    outcome_to_index_NDL = {tense:i for i,tense in enumerate(tense_list_NDL)}
    index_to_outcome_NDL = {i:tense for i,tense in enumerate(tense_list_NDL)}

    # Test prediction for a single given cue sequence. Model expect input as array of shape (1, N_cues) 
    #sent1 = 'I will meet you tomorrow'
    cue1_seq = 'I_you_tomorrow_I#you_you#tomorrow_I#you#tomorrow'
    outcome1_prob_pred = ev.predict_proba_oneevent_NDL(model = NDL_model, 
                                                    cue_seq = cue1_seq)
    print({index_to_outcome_NDL[j]:round(outcome1_prob_pred[j],4) for j in range(len(outcome1_prob_pred))})
    # {'past.simple': 0.0772, 'present.simple': 0.1036, 'past.perf': 0.0875, 'future.simple': 0.1028, 
    # 'present.perf': 0.0896, 'present.prog': 0.0926, 'past.prog': 0.0889, 'present.perf.prog': 0.0893, 
    # 'future.prog': 0.09, 'future.perf': 0.0894, 'past.perf.prog': 0.0891} 

    # Calculate the activations
    start_activ = time.time()
    activ_test = activation(events = NGRAM_EVENTS_MULTI_VERBS_TEST, 
                            weights = NDL_model.weights,
                            number_of_threads = 1,
                            remove_duplicates = True,
                            ignore_missing_cues = True)
    logging.info('Activations calculated in %.0fs\n' % ((time.time() - start_activ)))

    activ_test2 = activ_test.transpose()
    activ_test_df = activ_test2.to_pandas()
    #del activ_test_df.columns.name
    #del activ_test_df.index.name
    activ_test_df.shape
    activ_test_df.head()
    activ_test_df.to_csv(ACTIVATION_TEST, sep = ',', index = False)

    # Evaluate the model on the test set
    tenses_events = pd.read_csv(NGRAM_EVENTS_MULTI_VERBS_TEST, sep='\t', na_filter = False, encoding='utf8')
    tenses_test = pd.read_csv(TENSE_SET, sep=',', na_filter = False, encoding='utf8')
    y_test = tenses_events['outcomes'].tolist()
    # Predicted outcomes from the activations
    start_pred = time.time()
    y_pred = ev.activations_to_predictions(activ_test)
    logging.info('Predictions generated in %.0fs\n' % ((time.time() - start_pred)))

    # start_pred = time.time()
    # y_pred = ev.predict_outcomes_NDL(model = NDL_model,
    #                                  data_test = NGRAM_EVENTS_MULTI_VERBS_TEST,  
    #                                  temp_dir = TEMP_DIR, 
    #                                  num_threads = no_threads)
    # logging.info('Predictions generated in %.0fs\n' % ((time.time() - start_pred)))

    # Overall test accuracy
    #test_accuracy = accuracy_score(y_test, y_pred)
    # 

    cmat = confusion_matrix(y_test, y_pred, labels = list(outcome_to_index.keys())) # Confusion matrix
    pmat = cmat.diagonal()/cmat.sum(axis=1) # Confusion matrix in terms of proportions
    print({index_to_outcome[j+1]:round(pmat[j],4) for j in range(len(pmat))})
    # {'future.perf': 0.0, 'future.prog': 0.0, 'future.simple': 0.0162, 'past.perf': 0.0134, 
    # 'past.perf.prog': 0.0, 'past.prog': 0.0005, 'past.simple': 0.7416, 'present.perf': 0.0557, 
    # 'present.perf.prog': 0.0, 'present.prog': 0.0675, 'present.simple': 0.8643}
    return(tenses_test, y_pred)

def save_results(RESULTS_TEST, tenses_test, cue_to_index, y_pred):
    """
    
    ----
    PARAMETERS
    ----

    ----
    RETURN
    ----
    """

    #### Data set containing the final results

    # Load dataset containing test indices
    results_test = tenses_test[['SentenceID', 'Sentence', 'Tense', 'VerbForm', 'MainVerb', 'Position',
                                'Infinitive', 'VerbOrder', 'NgramCuesWithInfinitive', 'SentenceLength', 'NumOfVerbs',
                                'NumOfVerbsOriginal']].copy()
    # Rename the cue column
    results_test.rename(columns={'NgramCuesWithInfinitive':'Cues'}, inplace = True)
    # Add the test predictions as a column
    results_test['PredictedTense'] = y_pred
    # Add column of filtered cues
    allowed_cues = set(cue_to_index.keys())
    results_test['FilteredCues'] = results_test['Cues'].apply(lambda s: '_'.join([cue for cue in s.split('_') if cue in allowed_cues]))
    # Remove the column cues
    results_test.drop(columns = ['Cues'], inplace = True)
    # Add accuracy column
    results_test['Accuracy'] = results_test.apply(lambda x: int(x.loc['Tense'] == x.loc['PredictedTense']), axis = 1)
    # Reorder the columns
    results_test = results_test.loc[:, ['SentenceID', 'Sentence', 'FilteredCues', 'Tense', 'PredictedTense', 'Accuracy', 
                                        'VerbForm', 'MainVerb', 'Position', 'Infinitive', 'VerbOrder', 'SentenceLength', 
                                        'NumOfVerbs', 'NumOfVerbsOriginal']]
    results_test.to_csv(RESULTS_TEST, sep = ',', index = False)

def read_model(NGRAM_EVENTS_MULTI_VERBS_TEST, TENSE_SET, MODEL_PATH):
    """
    
    ----
    PARAMETERS
    ----

    ----
    RETURN
    ----
    """

    NDL_model = md.import_model("%s.h5"%(MODEL_PATH))
    activ_test = activation(events = NGRAM_EVENTS_MULTI_VERBS_TEST, 
                            weights = NDL_model.weights,
                            number_of_threads = 1,
                            remove_duplicates = True,
                            ignore_missing_cues = True)
    tenses_events = pd.read_csv(NGRAM_EVENTS_MULTI_VERBS_TEST, sep='\t', na_filter = False, encoding='utf8')
    tenses_test = pd.read_csv(TENSE_SET, sep=',', na_filter = False, encoding='utf8')
    # Predicted outcomes from the activations
    start_pred = time.time()
    y_pred = ev.activations_to_predictions(activ_test)

    return(tenses_test, y_pred)

def run(SIM_FILES):
    """
    Runs this stage of the processsing. This includes training an NDL model and producing accuracy scores
    ----
    PARAMETERS
    ----

    ----
    RETURN
    ----
    """

    # Import the cue index system
    NGRAM_EVENTS_MULTI_VERBS_TRAIN = "%s.gz"%(SIM_FILES[0])
    NGRAM_EVENTS_MULTI_VERBS_VALID = "%s.gz"%(SIM_FILES[1])
    NGRAM_EVENTS_MULTI_VERBS_TEST = "%s.gz"%(SIM_FILES[2])
    TENSE_SET, CUE_INDEX, OUTCOME_INDEX = "%s.csv.gz"%(SIM_FILES[3]), SIM_FILES[4], "%s.csv"%(SIM_FILES[5])
    TEMP_DIR, WEIGHTS_PATH, MODEL_PATH = SIM_FILES[6], SIM_FILES[7], SIM_FILES[8]
    RESULTS_TEST, ACTIVATION_TEST = "%s.csv"%(SIM_FILES[9]), "%s.csv"%(SIM_FILES[10])

    cue_to_index = pr.import_index_system("%s.csv"%(CUE_INDEX))
    pr.display_dictionary(cue_to_index, start = 0, end = 5)
    # {the: 1}
    # {of: 2}
    # {to: 3}
    # {and: 4}
    # {a: 5}

    # Import the outcome index system
    outcome_to_index = pr.import_index_system(OUTCOME_INDEX)
    # {'future.perf': 1, 'future.prog': 2, 'future.simple': 3, 'past.perf': 4, 
    # 'past.perf.prog': 5, 'past.prog': 6, 'past.simple': 7, 'present.perf': 8, 
    # 'present.perf.prog': 9, 'present.prog': 10, 'present.simple': 11}

    # Reverse the cue dictionary
    index_to_cue = pr.reverse_dictionary(cue_to_index)
    # Reverse the outcome dictionary
    index_to_outcome = pr.reverse_dictionary(outcome_to_index)
    NDL_model = train_model(NGRAM_EVENTS_MULTI_VERBS_TRAIN, NGRAM_EVENTS_MULTI_VERBS_VALID, TEMP_DIR,
                MODEL_PATH, WEIGHTS_PATH, cue_to_index, outcome_to_index)
    #NDL_model = md.load_NDL_model("%s.nc"%(WEIGHTS_PATH))
    tenses_test, y_pred = evaluate(TENSE_SET, ACTIVATION_TEST, NGRAM_EVENTS_MULTI_VERBS_TEST,
             NDL_model, outcome_to_index, index_to_outcome)
    

    save_results(RESULTS_TEST, tenses_test, cue_to_index, y_pred)