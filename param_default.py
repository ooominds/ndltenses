
####################################
# STEP 1: EXTRACT and create SENTENCES
####################################

NF = "" # path to the folder containing the necessary files that are user defined
TOP = "" #the top level directory to place files created by the process in

WD_EXTRACT = TOP + "" # directory to store the results of this step
#TAGGED_FILE = 'D:\\work\\OoOM\\ndl\\BNC.tagged.txt'
TAGGED_FILE = "" # should be a .txt file
RESULTS = WD_EXTRACT + "" # this should be a csv file

EXTRACT_SENTENCES_DIRS = [WD_EXTRACT] # main directory in which the results of this step are stored
EXTRACT_SENTENCES_FILES = [TAGGED_FILE, RESULTS] # list of files that need to be created (potentially with sub-directories)


#--------------------------------------------------------


######################################
# STEP 2: ANNOTATE TENSES                    
######################################

WD_ANNOTATE = TOP + "" # directory to store the results of this step
SENTS = RESULTS
TENSES_ANNOTATED_NOINF_CLEAN = WD_ANNOTATE + "" #csv

ANNOTATE_DIRS = [WD_ANNOTATE]
ANNOTATE_FILES = [SENTS, TENSES_ANNOTATED_NOINF_CLEAN]


#--------------------------------------------------------

######################################
# STEP 3: PREPARE DATA
######################################

WD_PREPDAT = TOP + "" # directory to store the results of this step

### Define file paths
TENSES = TENSES_ANNOTATED_NOINF_CLEAN
TENSES_ONE_SENT_PER_VERB_WITH_MODALS = WD_PREPDAT + "" #.csv
TENSES_ONE_SENT_PER_VERB_SHUF_GZ = WD_PREPDAT + "" #.csv.gz
#TENSES_ONE_VERB = WD_PREPDAT + "\\tenses_annotated_oneverb.csv"
#TENSES_ONE_VERB_READY_GZ = WD_PREPDAT + "\\tenses_annotated_oneverb_ready.csv.gz"
#TENSES_ONE_VERB_SHUF_GZ = WD_PREPDAT + "\\tenses_annotated_oneverb_shuffeled.csv.gz"
AE2BE_LIST = NF + "" # this file has to be created or obtained from the repository
INFINITIVE_CORR_LIST = NF + "" #.csv file

PREPDAT_DIRS = [WD_PREPDAT]
PREPDAT_FILES = [TENSES,TENSES_ONE_SENT_PER_VERB_WITH_MODALS,TENSES_ONE_SENT_PER_VERB_SHUF_GZ,
                 AE2BE_LIST, INFINITIVE_CORR_LIST]

#--------------------------------------------------------


######################################
# STEP 3: PREPARE TRAIN VALID TEST
######################################

### Define file paths
WD_PREPTRAIN = TOP + ""
TENSES_TRAIN_GZ = WD_PREPTRAIN + "" # will be saved as csv.gz, the file path to the training set
TENSES_VALID_GZ = WD_PREPTRAIN + "" # will be saved as csv.gz, the file path to the validation set
TENSES_TEST_GZ = WD_PREPTRAIN + "" # will be saved as csv.gz, the file path to the test set

PROP_VALID = 1/20 # proportion of validation data
PROP_TEST = 1/20 # proportion of test data

#TENSES_ONE_VERB_TRAIN_GZ = WD_PREPTRAIN + "\\tenses_oneverb_train.csv.gz"
#TENSES_ONE_VERB_VALID_GZ = WD_PREPTRAIN + "\\tenses_oneverb_valid.csv.gz"
#TENSES_ONE_VERB_TEST_GZ = WD_PREPTRAIN + "\\tenses_oneverb_test.csv.gz"

# n-gram based event files ready for training NDL (verb infinitives included as cues)
NGRAM_EVENTS_MULTI_VERBS_TRAIN = WD_PREPTRAIN + "" # will be a .gz
NGRAM_EVENTS_MULTI_VERBS_VALID = WD_PREPTRAIN + "" # will be a .gz
NGRAM_EVENTS_MULTI_VERBS_TEST = WD_PREPTRAIN + "" # will be a .gz

# word cue based event files ready for training NDL (verb infinitives included as cues)
#WORD_EVENTS_MULTI_VERBS_TRAIN = WD_PREPTRAIN + "\\word_eventfile_multiverbs_train.gz"
#WORD_EVENTS_MULTI_VERBS_VALID = WD_PREPTRAIN + "\\word_eventfile_multiverbs_valid.gz"
#WORD_EVENTS_MULTI_VERBS_TEST = WD_PREPTRAIN + "\\word_eventfile_multiverbs_test.gz"

PREPARE_TRAIN_VALID_TEST_FILES = [TENSES_TRAIN_GZ, TENSES_VALID_GZ, TENSES_TEST_GZ,
                                  NGRAM_EVENTS_MULTI_VERBS_TRAIN, NGRAM_EVENTS_MULTI_VERBS_VALID, NGRAM_EVENTS_MULTI_VERBS_TEST]

CREATE_TRAIN_VALID_TEST_FILES = [TENSES_ONE_SENT_PER_VERB_SHUF_GZ, TENSES_TRAIN_GZ,TENSES_VALID_GZ,TENSES_TEST_GZ]


#--------------------------------------------------------


######################################
# STEP 4: EXTRACT INFINITIVES FOR TRAINING
######################################

WD_EXTRACT_INF = TOP + ""
### Define file paths
TENSES_GZ = TENSES_ONE_SENT_PER_VERB_SHUF_GZ
COOC_FREQ_CSV = WD_EXTRACT_INF + "" #co-occurence frequencies, a .csv file
INFINITIVES_CSV = WD_EXTRACT_INF + "" #top 10 most frequent infinitives, a .csv file

EXTRACT_SENTENCES_FOLDERS = [WD_EXTRACT_INF]
EXTRACT_INFINITIVE_FILES =  [TENSES_GZ, COOC_FREQ_CSV, INFINITIVES_CSV]


#--------------------------------------------------------

WD_EXTRACT_NGRAM = TOP + ""

### Parameters to use
NUM_THREADS = 4
### Get up to N ngrams from each ngram group such as all extracted ngrams have freq>=10
NGRAMN = 10000

### Define file paths
NGRAM1 = WD_EXTRACT_NGRAM + "" #csv
NGRAM2 = WD_EXTRACT_NGRAM + "" #csv
NGRAM3 = WD_EXTRACT_NGRAM + "" #csv
NGRAM4 = WD_EXTRACT_NGRAM + "" #csv
NGRAM = WD_EXTRACT_NGRAM + "" #csv
TEMP_DIR_EXT = WD_EXTRACT_NGRAM + "data"

######################################
# STEP 5: PREPARE NGRAMs TO USE
######################################


# Final list of ngrams to use in training (5000)
TARGETS = WD_EXTRACT_NGRAM + "" #.csv file
# Separate lists of chunks
TARGETS_1G = WD_EXTRACT_NGRAM + "" #csv
TARGETS_2G = WD_EXTRACT_NGRAM + "" #csv
TARGETS_3G = WD_EXTRACT_NGRAM + "" #csv 
TARGETS_4G = WD_EXTRACT_NGRAM + "" #csv
EVENT_FILE = WD_EXTRACT_NGRAM + "" #csv

NGRAM_FOLDERS = [WD_EXTRACT_NGRAM, TEMP_DIR_EXT]
NGRAM_FILES = [NGRAM, NGRAM1, NGRAM2, NGRAM3, NGRAM4, EVENT_FILE]
TARGETS_FILES = [TARGETS, TARGETS_1G, TARGETS_2G, TARGETS_3G, TARGETS_4G]
K_NGRAMS = 10000



#--------------------------------------------------------



######################################
# STEP 6: PREPARE CUES
######################################

WD_CUES = TOP + ""

### File paths
# list of ngrams to use in training (10k n-grams from each n level with 1<= n< =4)
NGRAMS = TARGETS
# list of ngrams to use in training (4681)
INFINITIVES = INFINITIVES_CSV
# final list of all cues
ALL_CUES = WD_CUES + "" #csv



#--------------------------------------------------------

######################################
# STEP 7: SIMULATIONS
######################################

WD_SIM = ""

### Define file paths
#TENSE_SET_WITH_PRED = TOP + "Data_preparation/Data_shared/tenses_multiverbs_test_withpreds.csv.gz"
CUE_INDEX = ALL_CUES
OUTCOME_INDEX = NF + "" #user defined csv to determine what the possible outcomes are
TEMP_DIR_SIM = WD_SIM + ""
MODEL_PATH = WD_SIM + "" #h5 file (h5py)
WEIGHTS_PATH = WD_SIM + "" #.nc file (netCDF)
RESULTS_TEST = WD_SIM + "" #.csv
ACTIVATION_TEST = WD_SIM + "" #.csv
NO_THREADS = 15 # number of threads
SIM_DIR = [WD_SIM, TEMP_DIR_SIM]
SIM_FILES = [NGRAM_EVENTS_MULTI_VERBS_TRAIN, NGRAM_EVENTS_MULTI_VERBS_VALID, NGRAM_EVENTS_MULTI_VERBS_TEST,
             TENSES_TEST_GZ, CUE_INDEX, OUTCOME_INDEX, TEMP_DIR_SIM,
             WEIGHTS_PATH, MODEL_PATH, RESULTS_TEST, ACTIVATION_TEST]
SIM_PARAMS = [NO_THREADS]

#--------------------------------------------------------             