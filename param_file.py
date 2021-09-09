
####################################
# EXTRACT and create SENTENCES
####################################

NF = 'D:\\work\\OoOM\\ndl\\necessary_files' # necessary files that are user defined
TOP = 'D:\\work\\OoOM\\ndl\\test_location\\data_preparation' #the top level directory to place files created by the process in

WD_EXTRACT = TOP + "\\extract\\" # directory to store the results of this step
#TAGGED_FILE = 'D:\\work\\OoOM\\ndl\\BNC.tagged.null'
#TAGGED_FILE = 'D:\\work\\OoOM\\ndl\\BNC.tagged.null.short'
#TAGGED_FILE = 'D:\\work\\OoOM\\ndl\\colloquial_full_sen' # should be a .txt file
TAGGED_FILE = 'D:\\work\\OoOM\\ndl\\BNC.spoken.clean' # should be a .txt file
RESULTS = WD_EXTRACT + "example_sentences" # this should be a csv file

EXTRACT_SENTENCES_DIRS = [WD_EXTRACT] # main directory in which the results of this step are stored
EXTRACT_SENTENCES_FILES = [TAGGED_FILE, RESULTS] # list of files that need to be created (potentially with sub-directories)


#--------------------------------------------------------


######################################
# ANNOTATE TENSES                    
######################################

WD_ANNOTATE = TOP + "\\annotate_complex_sentences\\" # directory to store the results of this step
SENTS = RESULTS
TENSES_ANNOTATED_NOINF_CLEAN = WD_ANNOTATE + "tenses_annotated_noinf_clean" #csv

ANNOTATE_DIRS = [WD_ANNOTATE]
ANNOTATE_FILES = [SENTS, TENSES_ANNOTATED_NOINF_CLEAN]


#--------------------------------------------------------

######################################
# PREPARE DATA
######################################

WD_PREPDAT = TOP + '\\prepare_events\\' # directory to store the results of this step

### Define file paths
TENSES = TENSES_ANNOTATED_NOINF_CLEAN
TENSES_ONE_SENT_PER_VERB_WITH_MODALS = WD_PREPDAT + "tenses_annotated_one_sent_per_verb_with_modals" #.csv
TENSES_ONE_SENT_PER_VERB_SHUF_GZ = WD_PREPDAT + "tenses_annotated_one_sent_per_verb_shuffeled" #.csv.gz
#TENSES_ONE_VERB = WD_PREPDAT + "\\tenses_annotated_oneverb.csv"
#TENSES_ONE_VERB_READY_GZ = WD_PREPDAT + "\\tenses_annotated_oneverb_ready.csv.gz"
#TENSES_ONE_VERB_SHUF_GZ = WD_PREPDAT + "\\tenses_annotated_oneverb_shuffeled.csv.gz"
AE2BE_LIST = NF + "\\List_AE2BE.csv" #this file has to be created or obtained from the repository
INFINITIVE_CORR_LIST = NF + "\\Infinitive_corrections_freq10" #.csv file

PREPDAT_DIRS = [WD_PREPDAT]
PREPDAT_FILES = [TENSES,TENSES_ONE_SENT_PER_VERB_WITH_MODALS,TENSES_ONE_SENT_PER_VERB_SHUF_GZ,
                 AE2BE_LIST, INFINITIVE_CORR_LIST]

#--------------------------------------------------------




######################################
# PREPARE TRAIN VALID TEST
######################################

### Define file paths
WD_PREPTRAIN = TOP + "\\prep_train"
TENSES_TRAIN_GZ = WD_PREPTRAIN + "\\tenses_one_sent_per_verb_train" # will be saved as csv.gz, the file path to the training set
TENSES_VALID_GZ = WD_PREPTRAIN + "\\tenses_one_sent_per_verb_valid" # will be saved as csv.gz, the file path to the validation set
TENSES_TEST_GZ = WD_PREPTRAIN + "\\tenses_one_sent_per_verb_test" # will be saved as csv.gz, the file path to the test set

PROP_VALID = 1/20 # proportion of validation data
PROP_TEST = 1/20 # proportion of test data

#TENSES_ONE_VERB_TRAIN_GZ = WD_PREPTRAIN + "\\tenses_oneverb_train.csv.gz"
#TENSES_ONE_VERB_VALID_GZ = WD_PREPTRAIN + "\\tenses_oneverb_valid.csv.gz"
#TENSES_ONE_VERB_TEST_GZ = WD_PREPTRAIN + "\\tenses_oneverb_test.csv.gz"

# n-gram based event files ready for training NDL (verb infinitives included as cues)
NGRAM_EVENTS_MULTI_VERBS_TRAIN = WD_PREPTRAIN + "\\ngram_eventfile_multiverbs_train" # will be a .gz
NGRAM_EVENTS_MULTI_VERBS_VALID = WD_PREPTRAIN + "\\ngram_eventfile_multiverbs_valid" # will be a .gz
NGRAM_EVENTS_MULTI_VERBS_TEST = WD_PREPTRAIN + "\\ngram_eventfile_multiverbs_test" # will be a .gz

# word cue based event files ready for training NDL (verb infinitives included as cues)
#WORD_EVENTS_MULTI_VERBS_TRAIN = WD_PREPTRAIN + "\\word_eventfile_multiverbs_train.gz"
#WORD_EVENTS_MULTI_VERBS_VALID = WD_PREPTRAIN + "\\word_eventfile_multiverbs_valid.gz"
#WORD_EVENTS_MULTI_VERBS_TEST = WD_PREPTRAIN + "\\word_eventfile_multiverbs_test.gz"

PREPARE_TRAIN_VALID_TEST_FILES = [TENSES_TRAIN_GZ, TENSES_VALID_GZ, TENSES_TEST_GZ,
                                  NGRAM_EVENTS_MULTI_VERBS_TRAIN, NGRAM_EVENTS_MULTI_VERBS_VALID, NGRAM_EVENTS_MULTI_VERBS_TEST]

CREATE_TRAIN_VALID_TEST_FILES = [TENSES_ONE_SENT_PER_VERB_SHUF_GZ, TENSES_TRAIN_GZ,TENSES_VALID_GZ,TENSES_TEST_GZ]


#--------------------------------------------------------


######################################
# EXTRACT INFINITIVES FOR TRAINING
######################################

WD_EXTRACT_INF = TOP + "\\extract_infinitives"
### Define file paths
TENSES_GZ = TENSES_ONE_SENT_PER_VERB_SHUF_GZ
COOC_FREQ_CSV = WD_EXTRACT_INF + "\\Cooc_freq" #co-occurence frequencies, a .csv file
INFINITIVES_CSV = WD_EXTRACT_INF + "\\infinitives_freq10" #top 10 most frequent infinitives, a .csv file

EXTRACT_SENTENCES_FOLDERS = [WD_EXTRACT_INF]
EXTRACT_INFINITIVE_FILES =  [TENSES_GZ, COOC_FREQ_CSV, INFINITIVES_CSV]


#--------------------------------------------------------


######################################
# OPTIONAL: EXTRACT NGRAM WITH FREQ
######################################

WD_EXTRACT_NGRAM = TOP + '\\prepare_ngrams\\'

### Parameters to use
NUM_THREADS = 4
### Get up to N ngrams from each ngram group such as all extracted ngrams have freq>=10
NGRAMN = 10000

### Define file paths
NGRAM1 = WD_EXTRACT_NGRAM + "1grams" #csv
NGRAM2 = WD_EXTRACT_NGRAM + "2grams" #csv
NGRAM3 = WD_EXTRACT_NGRAM + "3grams" #csv
NGRAM4 = WD_EXTRACT_NGRAM + "4grams" #csv
NGRAM = WD_EXTRACT_NGRAM + "ngrams" #csv
TEMP_DIR_EXT = WD_EXTRACT_NGRAM + "data"

######################################
# NGRAMs TO USE
######################################


# Final list of ngrams to use in training (5000)
TARGETS = WD_EXTRACT_NGRAM + "ngrams_touse" #.csv file
# Separate lists of chunks
TARGETS_1G = WD_EXTRACT_NGRAM + "1grams_touse"
TARGETS_2G = WD_EXTRACT_NGRAM + "2grams_touse"
TARGETS_3G = WD_EXTRACT_NGRAM + "3grams_touse"
TARGETS_4G = WD_EXTRACT_NGRAM + "4grams_touse"
EVENT_FILE = WD_EXTRACT_NGRAM + "events_4grams"

NGRAM_FOLDERS = [WD_EXTRACT_NGRAM]
NGRAM_FILES = [NGRAM, NGRAM1, NGRAM2, NGRAM3, NGRAM4, EVENT_FILE]
TARGETS_FILES = [TARGETS, TARGETS_1G, TARGETS_2G, TARGETS_3G, TARGETS_4G]
K_NGRAMS = 10000



#--------------------------------------------------------



######################################
# PREPARE CUES
######################################

WD_CUES = TOP + '\\prepare_events'

### File paths
# list of ngrams to use in training (10k n-grams from each n level with 1<= n< =4)
NGRAMS = TARGETS
# list of ngrams to use in training (4681)
INFINITIVES = INFINITIVES_CSV
# final list of all cues
ALL_CUES = WD_CUES + '\\cues_touse'



#--------------------------------------------------------

######################################
#SIMULATIONS
######################################

WD_SIM = 'D:\\work\\OoOM\\ndl\\test_location\\simulations\\'

### Define file paths
#TENSE_SET_WITH_PRED = TOP + "Data_preparation/Data_shared/tenses_multiverbs_test_withpreds.csv.gz"
CUE_INDEX = ALL_CUES
OUTCOME_INDEX = NF + "\\outcome_index_ngram_multiverbs" #user defined csv to determine what the possible outcomes are
TEMP_DIR_SIM = WD_SIM + "data\\"
MODEL_PATH = WD_SIM + 'NDL_model_ngrams_multiverbs' #h5 file (h5py)
WEIGHTS_PATH = WD_SIM + 'NDL_weights_ngrams_multiverbs' #.nc file (netCDF)
RESULTS_TEST = WD_SIM + "results_testset_ngrams_multiverbs" #.csv
ACTIVATION_TEST = WD_SIM + "Activations_testset_ngrams_multiverbs" #.csv
NO_THREADS = 15

SIM_DIR = [WD_SIM, TEMP_DIR_SIM]
SIM_FILES = [NGRAM_EVENTS_MULTI_VERBS_TRAIN, NGRAM_EVENTS_MULTI_VERBS_VALID, NGRAM_EVENTS_MULTI_VERBS_TEST,
             TENSES_TEST_GZ, CUE_INDEX, OUTCOME_INDEX, TEMP_DIR_SIM,
             WEIGHTS_PATH, MODEL_PATH, RESULTS_TEST, ACTIVATION_TEST]
SIM_PARAMS = [NO_THREADS]


#--------------------------------------------------------             