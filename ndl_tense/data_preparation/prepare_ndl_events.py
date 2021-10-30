####################
# Preliminary steps
####################

### Import necessary packages
from param_file import CREATE_TRAIN_VALID_TEST_FILES
import pandas as pd
import time
#import logging
from collections import Counter
from sklearn.model_selection import train_test_split

#logger = logging.getLogger("data_preparation")
#logger.setLevel(level=logging.INFO)

### Set working directory

### Set the max width of a column
pd.set_option('display.max_colwidth', 150)
pd.set_option('display.max_columns', 150)

####################
# Preliminary steps
####################

### Import necessary packages


### Set working directory

### Parameters to use
PROP_VALID = 1/20 # proportion of validation data
PROP_TEST = 1/20 # proportion of test data

######################################################
# Split the full set into train, valid and test sets 
######################################################

def prepare_subset_df(tenses, ct_sentid_keys, count_sentid):

    count_sentid_subset = [(k, count_sentid[k]) for k in ct_sentid_keys]

    SentID_list = []
    for (k,v) in count_sentid_subset:
        SentID_list.extend([k]*v)

    # Convert the shuffled list into a dataframe 
    SentID_df = pd.DataFrame({'SentenceID': SentID_list})

    # Add the column VerbOrder
    SentID_df['VerbOrder'] = SentID_df.groupby('SentenceID').cumcount()
    SentID_df['VerbOrder'] = SentID_df['VerbOrder'] + 1

    # Change the order of SentID by merging tenses and SentID_df
    tenses_subset = SentID_df.merge(tenses)

    return tenses_subset


### Load the data
def prepare_files(CREATE_TRAIN_VALID_TEST_FILES, PROP_VALID, PROP_TEST, VERBOSE):
    TENSES_ONE_SENT_PER_VERB_SHUF_GZ = CREATE_TRAIN_VALID_TEST_FILES[0]
    TENSES_TRAIN_GZ,TENSES_VALID_GZ,TENSES_TEST_GZ = CREATE_TRAIN_VALID_TEST_FILES[1], CREATE_TRAIN_VALID_TEST_FILES[2], CREATE_TRAIN_VALID_TEST_FILES[3]
    start = time.time()
    tenses = pd.read_csv("{}.csv.gz".format(TENSES_ONE_SENT_PER_VERB_SHUF_GZ), compression='gzip')
    if VERBOSE:
        print('Loading the data took {}s\n'.format((time.time()-start)))
    # Number of examples: 7041930

    ### Remove future.perf.prog
    tenses = tenses[tenses['Tense'] != 'future.perf.prog']

    # Create a counter of sent ids
    SentID_list = list(tenses["SentenceID"])
    count_sentid = Counter()
    for id in SentID_list:
        count_sentid[id] += 1

    # Split the list of keys into train, valid and test keys
    count_keys =  list(count_sentid.keys())
    count_keys_train, count_keys_hold = train_test_split(count_keys, test_size = (PROP_TEST+PROP_VALID), random_state=1)
    count_keys_valid, count_keys_test = train_test_split(count_keys_hold, test_size = 0.5, random_state=1)

        ### Prepare the train, valid and test sets and save them
    tenses_valid = prepare_subset_df(tenses, count_keys_valid, count_sentid)
    tenses_test = prepare_subset_df(tenses, count_keys_test, count_sentid)

    tenses_valid.to_csv("{}.csv.gz".format(TENSES_VALID_GZ), compression='gzip', index = False) # Export the validation dataset
    tenses_test.to_csv("{}.csv.gz".format(TENSES_TEST_GZ), compression='gzip', index = False) # Export the test dataset
    del tenses_valid, tenses_test
    tenses = prepare_subset_df(tenses, count_keys_train, count_sentid)
    tenses_train = tenses
    tenses_train.to_csv("{}.csv.gz".format(TENSES_TRAIN_GZ), compression='gzip', index = False) # Export the train dataset
    del tenses_train
    if VERBOSE:
        print('STEP 4 1/2: Preparing NDL events files is complete\n')

    ###########################################################
    # Split the 'one-verb' set into train, valid and test sets 
    ###########################################################

    ### Load the data
    # start = time.time()
    # tenses = pd.read_csv(TENSES_ONE_VERB_SHUF_GZ, compression='gzip')
    # logger.info('Loading the data took %ds' %((time.time()-start)))

    #print(f'Number of examples: {len(tenses)}')
    # Number of examples: 1853675

    #tenses['Tense'].value_counts()
    # present.simple       810895
    # past.simple          702786
    # present.perf         114764
    # future.simple         78086
    # past.perf             54561
    # present.prog          53958
    # past.prog             29891
    # present.perf.prog      3762
    # future.prog            2646
    # past.perf.prog         1522
    # future.perf             795
    # future.perf.prog          9

    ### Remove future.perf.prog
    #tenses = tenses[tenses['Tense'] != 'future.perf.prog']

    # Create a counter of sent ids
    #SentID_list = list(tenses["SentenceID"])
    #count_sentid = Counter()
    #for id in SentID_list:
    #    count_sentid[id] += 1

    # Split the list of keys into train, valid and test keys
    #count_keys =  list(count_sentid.keys())
    #count_keys_train, count_keys_hold = train_test_split(count_keys, test_size = (PROP_TEST+PROP_VALID), random_state=1)
    #count_keys_valid, count_keys_test = train_test_split(count_keys_hold, test_size = 0.5, random_state=1)

    ### Prepare the train, valid and test sets and save them
    #tenses_valid = prepare_subset_df(tenses, count_keys_valid, count_sentid)
    #tenses_test = prepare_subset_df(tenses, count_keys_test, count_sentid)
    #tenses_valid.to_csv(TENSES_ONE_VERB_VALID_GZ, compression='gzip', index = False) # Export the validation dataset
    #tenses_test.to_csv(TENSES_ONE_VERB_TEST_GZ, compression='gzip', index = False) # Export the test dataset
    #del tenses_valid, tenses_test
    #tenses = prepare_subset_df(tenses, count_keys_train, count_sentid)
    #tenses_train = tenses
    #tenses_train.to_csv(TENSES_ONE_VERB_TRAIN_GZ, compression='gzip', index = False) # Export the train dataset

def run(PREPARE_TRAIN_VALID_TEST_FILES, BY='NgramCuesWithInfinitive', VERBOSE=True):
    TENSES_TRAIN_GZ = PREPARE_TRAIN_VALID_TEST_FILES[0]
    TENSES_VALID_GZ = PREPARE_TRAIN_VALID_TEST_FILES[1]
    TENSES_TEST_GZ = PREPARE_TRAIN_VALID_TEST_FILES[2]

    NGRAM_EVENTS_MULTI_VERBS_TRAIN = PREPARE_TRAIN_VALID_TEST_FILES[3]
    NGRAM_EVENTS_MULTI_VERBS_VALID = PREPARE_TRAIN_VALID_TEST_FILES[4]
    NGRAM_EVENTS_MULTI_VERBS_TEST = PREPARE_TRAIN_VALID_TEST_FILES[5]
    
    ### Load the data
    start = time.time()
    tenses_multiverbs_train = pd.read_csv("{}.csv.gz".format(TENSES_TRAIN_GZ), compression='gzip', usecols=[BY, 'Tense'])
    tenses_multiverbs_valid = pd.read_csv("{}.csv.gz".format(TENSES_VALID_GZ), compression='gzip', usecols=[BY, 'Tense'])
    tenses_multiverbs_test = pd.read_csv("{}.csv.gz".format(TENSES_TEST_GZ), compression='gzip', usecols=[BY, 'Tense'])
    
    tenses_multiverbs_train.rename(columns = {BY: 'cues',
                                        'Tense': 'outcomes'}, inplace = True)
    tenses_multiverbs_valid.rename(columns = {BY: 'cues',
                                        'Tense': 'outcomes'}, inplace = True)
    tenses_multiverbs_test.rename(columns = {BY: 'cues',
                                        'Tense': 'outcomes'}, inplace = True)

    tenses_multiverbs_train = tenses_multiverbs_train[['cues', 'outcomes']]
    tenses_multiverbs_valid = tenses_multiverbs_valid[['cues', 'outcomes']]
    tenses_multiverbs_test = tenses_multiverbs_test[['cues', 'outcomes']]
    
    tenses_multiverbs_train.to_csv("{}.gz".format(NGRAM_EVENTS_MULTI_VERBS_TRAIN), sep='\t' , index = False, compression='gzip')
    tenses_multiverbs_valid.to_csv("{}.gz".format(NGRAM_EVENTS_MULTI_VERBS_VALID), sep='\t', index = False, compression='gzip')
    tenses_multiverbs_test.to_csv("{}.gz".format(NGRAM_EVENTS_MULTI_VERBS_TEST), sep='\t', index = False, compression='gzip')

    if VERBOSE:
        logger.info('Loading the data sets took {}s\n'.format((time.time()-start)))
        logger.info('STEP 4 2/2: Preparing NDL events is complete\n')