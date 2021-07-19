####################
# Preliminary steps
####################

### Import necessary packages
import os
import pandas as pd
import time
import sys

### Set working directory

### Set the max width of a column
pd.set_option('display.max_colwidth', 150)
pd.set_option('display.max_columns', 150)


##################################################
# ngram based event files for the multi verbs set
##################################################
def ngram_event_files(tenses_multiverbs_train, tenses_multiverbs_valid, tenses_multiverbs_test,
                      NGRAM_EVENTS_MULTI_VERBS_TRAIN, NGRAM_EVENTS_MULTI_VERBS_VALID, NGRAM_EVENTS_MULTI_VERBS_TEST):

    print(f'Number of examples: {len(tenses_multiverbs_train)}') # Number of examples: 6343547
    print(f'Number of examples: {len(tenses_multiverbs_valid)}') # Number of examples: 352168
    print(f'Number of examples: {len(tenses_multiverbs_test)}') # Number of examples: 351408

    ### Rename cue and outcome columns and reorder
    tenses_multiverbs_train.rename(columns = {'NgramCuesWithInfinitive': 'cues',
                                        'Tense': 'outcomes'}, inplace = True)
    tenses_multiverbs_valid.rename(columns = {'NgramCuesWithInfinitive': 'cues',
                                        'Tense': 'outcomes'}, inplace = True)
    tenses_multiverbs_test.rename(columns = {'NgramCuesWithInfinitive': 'cues',
                                        'Tense': 'outcomes'}, inplace = True)

    tenses_multiverbs_train = tenses_multiverbs_train[['cues', 'outcomes']]
    tenses_multiverbs_valid = tenses_multiverbs_valid[['cues', 'outcomes']]
    tenses_multiverbs_test = tenses_multiverbs_test[['cues', 'outcomes']]

    # Export the ngram-based event files
    tenses_multiverbs_train.to_csv(NGRAM_EVENTS_MULTI_VERBS_TRAIN, sep='\t' , index = False, compression='gzip')
    tenses_multiverbs_valid.to_csv(NGRAM_EVENTS_MULTI_VERBS_VALID, sep='\t', index = False, compression='gzip')
    tenses_multiverbs_test.to_csv(NGRAM_EVENTS_MULTI_VERBS_TEST, sep='\t', index = False, compression='gzip')
    del tenses_multiverbs_train, tenses_multiverbs_valid, tenses_multiverbs_test

def word_cues(tenses_multiverbs_train, tenses_multiverbs_valid, tenses_multiverbs_test,
              WORD_EVENTS_MULTI_VERBS_TRAIN, WORD_EVENTS_MULTI_VERBS_VALID, WORD_EVENTS_MULTI_VERBS_TEST):
    #####################################################
    # word cue based event files for the multi verbs set
    #####################################################

    ### Rename cue and outcome columns and reorder
    tenses_multiverbs_train.rename(columns = {'WordCuesWithInfinitive': 'cues',
                                        'Tense': 'outcomes'}, inplace = True)
    tenses_multiverbs_valid.rename(columns = {'WordCuesWithInfinitive': 'cues',
                                        'Tense': 'outcomes'}, inplace = True)
    tenses_multiverbs_test.rename(columns = {'WordCuesWithInfinitive': 'cues',
                                        'Tense': 'outcomes'}, inplace = True)

    tenses_multiverbs_train = tenses_multiverbs_train[['cues', 'outcomes']]
    tenses_multiverbs_valid = tenses_multiverbs_valid[['cues', 'outcomes']]
    tenses_multiverbs_test = tenses_multiverbs_test[['cues', 'outcomes']]

    # Export the ngram-based event files
    tenses_multiverbs_train.to_csv(WORD_EVENTS_MULTI_VERBS_TRAIN, sep='\t' , index = False, compression='gzip')
    tenses_multiverbs_valid.to_csv(WORD_EVENTS_MULTI_VERBS_VALID, sep='\t', index = False, compression='gzip')
    tenses_multiverbs_test.to_csv(WORD_EVENTS_MULTI_VERBS_TEST, sep='\t', index = False, compression='gzip')

    del tenses_multiverbs_train, tenses_multiverbs_valid, tenses_multiverbs_test

def run(PREPARE_TRAIN_VALID_TEST_FILES):
    
    TENSES_MULTI_VERBS_TRAIN_GZ = PREPARE_TRAIN_VALID_TEST_FILES[0]
    TENSES_MULTI_VERBS_VALID_GZ = PREPARE_TRAIN_VALID_TEST_FILES[1]
    TENSES_MULTI_VERBS_TEST_GZ = PREPARE_TRAIN_VALID_TEST_FILES[2]
    
    ### Load the data
    start = time.time()
    tenses_multiverbs_train = pd.read_csv(TENSES_MULTI_VERBS_TRAIN_GZ, compression='gzip', usecols=['WordCuesWithInfinitive', 'Tense'])
    tenses_multiverbs_valid = pd.read_csv(TENSES_MULTI_VERBS_VALID_GZ, compression='gzip', usecols=['WordCuesWithInfinitive', 'Tense'])
    tenses_multiverbs_test = pd.read_csv(TENSES_MULTI_VERBS_TEST_GZ, compression='gzip', usecols=['WordCuesWithInfinitive', 'Tense'])
    _ = sys.stdout.write('Loading the data sets took %ds' %((time.time()-start)))