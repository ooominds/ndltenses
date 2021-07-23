
####################################
# EXTRACT SENTENCES
####################################

NF = 'D:\\work\\OoOM\\ndl\\necessary_files'
TOP = 'D:\\work\\OoOM\\ndl\\test_location\\data_preparation'

WD_EXTRACT = TOP + "\\extract" 
#TAGGED_FILE = 'D:\\work\\OoOM\\ndl\\BNC.tagged.txt'
TAGGED_FILE = 'D:\\work\\OoOM\\ndl\\BNC.tagged.txt' # should be a .txt file
RESULTS_TSV = WD_EXTRACT + "\\Results\\example_sentences" # a .csv file that stores the results
RESULTS_CSV = WD_EXTRACT + "\\Results\\example_sentences"
SEP_CSV_FILES = WD_EXTRACT + "\\Data_shared\\Results\\example_sentences"

EXTRACT_SENTENCES_DIRS = [WD_EXTRACT]
EXTRACT_SENTENCES_FILES = [TAGGED_FILE,RESULTS_TSV, RESULTS_CSV, SEP_CSV_FILES]

######################################
# ANNOTATE TENSES                    
######################################

WD_ANNOTATE = TOP + "\\annotate_complex_sentences"
SENTS = RESULTS_CSV

SENTS_CLEAN = WD_ANNOTATE + "\\Results\\sentences_clean" # should be a csv file
TENSES_ANNOTATED_NOINF = WD_ANNOTATE + "\\Data_shared\\NoDoparallel\\tenses_annotated_noinf"
TENSES_ANNOTATED_NOINF_CLEAN = WD_ANNOTATE + "\\Data_shared\\NoDoparallel\\tenses_annotated_noinf_clean"
TENSES_ANNOTATED_CLEAN_N = WD_ANNOTATE + "\\Data_shared\\Results\\NoDoparallel\\tenses_annotated_noinf_clean_"

ANNOTATE_DIRS = [WD_ANNOTATE]
ANNOTATE_FILES = [SENTS, SENTS_CLEAN, TENSES_ANNOTATED_NOINF, TENSES_ANNOTATED_NOINF_CLEAN, TENSES_ANNOTATED_CLEAN_N]

######################################
# PREPARE DATA
######################################

WD_PREPDAT = TOP + '\\prepare_events'

### Define file paths
TENSES = TENSES_ANNOTATED_NOINF_CLEAN
TENSES_WITH_INF = TOP + "\\Data_shared\\NoDoparallel\\tenses_annotated_withinf.csv"

TENSES_WITH_INF_NEW = TOP + "\\Data_shared\\tenses_annotated_withinf_new.csv"
TENSES_ONE_SENT_PER_VERB = TOP + "\\Data_shared\\tenses_annotated_one_sent_per_verb.csv"
TENSES_ONE_SENT_PER_VERB_WITH_MODALS = TOP + "\\Data_shared\\tenses_annotated_one_sent_per_verb_with_modals.csv"
TENSES_ONE_SENT_PER_VERB_READY_GZ = TOP + "\\Data_shared\\tenses_annotated_one_sent_per_verb_ready.csv.gz"
TENSES_ONE_SENT_PER_VERB_SHUF_GZ = TOP + "\\Data_shared\\tenses_annotated_one_sent_per_verb_shuffeled"
TENSES_ONE_VERB = TOP + "\\Data_shared\\tenses_annotated_oneverb.csv"
TENSES_ONE_VERB_READY_GZ = TOP + "\\Data_shared\\tenses_annotated_oneverb_ready.csv.gz"
TENSES_ONE_VERB_SHUF_GZ = TOP + "\\Data_shared\\tenses_annotated_oneverb_shuffeled.csv.gz"
AE2BE_LIST = NF + "\\List_AE2BE.csv" #this file has to be created or obtained from the repository
INFINITIVE_CORR_LIST = NF + "\\Infinitive_corrections_freq10.csv" 

PREPDAT_DIRS = [WD_PREPDAT]
PREPDAT_FILES = [TENSES, TENSES_WITH_INF, TENSES_WITH_INF_NEW, TENSES_ONE_SENT_PER_VERB,
                 TENSES_ONE_SENT_PER_VERB_WITH_MODALS, TENSES_ONE_SENT_PER_VERB_READY_GZ, TENSES_ONE_SENT_PER_VERB_SHUF_GZ, TENSES_ONE_VERB,
                 TENSES_ONE_VERB_READY_GZ, TENSES_ONE_VERB_SHUF_GZ, AE2BE_LIST, INFINITIVE_CORR_LIST]

######################################
# PREPARE TRAIN VALID TEST
######################################

### Define file paths

TENSES_TRAIN_GZ = TOP + "Data_shared/tenses_one_sent_per_verb_train.csv.gz"
TENSES_VALID_GZ = TOP + "Data_shared/tenses_one_sent_per_verb_valid.csv.gz"
TENSES_TEST_GZ = TOP + "Data_shared/tenses_one_sent_per_verb_test.csv.gz"

TENSES_ONE_VERB_SHUF_GZ = TOP + "Data_shared/tenses_annotated_oneverb_shuffeled.csv.gz"
TENSES_ONE_VERB_TRAIN_GZ = TOP + "Data_shared/tenses_oneverb_train.csv.gz"
TENSES_ONE_VERB_VALID_GZ = TOP + "Data_shared/tenses_oneverb_valid.csv.gz"
TENSES_ONE_VERB_TEST_GZ = TOP + "Data_shared/tenses_oneverb_test.csv.gz"

# n-gram based event files ready for training NDL (verb infinitives included as cues)
NGRAM_EVENTS_MULTI_VERBS_TRAIN = TOP + "\\Data_shared\\Eventfiles_forNDL\\ngram_eventfile_multiverbs_train.gz"
NGRAM_EVENTS_MULTI_VERBS_VALID = TOP + "\\Data_shared\\Eventfiles_forNDL\\ngram_eventfile_multiverbs_valid.gz"
NGRAM_EVENTS_MULTI_VERBS_TEST = TOP + "\\Data_shared\\Eventfiles_forNDL\\ngram_eventfile_multiverbs_test.gz"
# word cue based event files ready for training NDL (verb infinitives included as cues)
WORD_EVENTS_MULTI_VERBS_TRAIN = TOP + "\\Data_shared\\Eventfiles_forNDL\\word_eventfile_multiverbs_train.gz"
WORD_EVENTS_MULTI_VERBS_VALID = TOP + "\\Data_shared\\Eventfiles_forNDL\\word_eventfile_multiverbs_valid.gz"
WORD_EVENTS_MULTI_VERBS_TEST = TOP + "\\Data_shared\\Eventfiles_forNDL\\word_eventfile_multiverbs_test.gz"

PREPARE_TRAIN_VALID_TEST_FILES = [TENSES_TRAIN_GZ, TENSES_VALID_GZ, TENSES_TEST_GZ,
                                  TENSES_ONE_VERB_SHUF_GZ,TENSES_ONE_VERB_TRAIN_GZ,TENSES_ONE_VERB_VALID_GZ,TENSES_ONE_VERB_TEST_GZ,
                                  NGRAM_EVENTS_MULTI_VERBS_TRAIN, NGRAM_EVENTS_MULTI_VERBS_VALID, NGRAM_EVENTS_MULTI_VERBS_TEST,
                                  WORD_EVENTS_MULTI_VERBS_TRAIN, WORD_EVENTS_MULTI_VERBS_VALID, WORD_EVENTS_MULTI_VERBS_TEST]

CREATE_TRAIN_VALID_TEST_FILES = [TENSES_ONE_SENT_PER_VERB_SHUF_GZ,  TENSES_ONE_VERB_SHUF_GZ, TENSES_TRAIN_GZ,TENSES_VALID_GZ,TENSES_TEST_GZ,
                                 TENSES_ONE_VERB_TRAIN_GZ, TENSES_ONE_VERB_VALID_GZ, TENSES_ONE_VERB_TEST_GZ]
######################################
# EXTRACT INFINITIVES FOR TRAINING
######################################

WD_EXTRACT_INF = TOP + "\\extract_infinitives"
### Define file paths
TENSES_GZ = TENSES_ONE_SENT_PER_VERB_SHUF_GZ
COOC_FREQ_CSV = WD_EXTRACT + "\\Results\\multi_verbs\\Cooc_freq.csv"
INFINITIVES_CSV = WD_EXTRACT + "\\Data\\multi_verbs\\infinitives_freq10.csv"

######################################
# EXTRACT NGRAM WITH FREQ
######################################

WD_EXTRACT_NGRAM = TOP + '\\Prepare_ngrams'

### Define file paths
NGRAM1 = WD_EXTRACT_NGRAM + "\\Data\\multi_verbs\\1grams.csv"
NGRAM2 = WD_EXTRACT_NGRAM + "\\Data\\multi_verbs\\2grams.csv"
NGRAM3 = WD_EXTRACT_NGRAM + "\\Data\\multi_verbs\\3grams.csv"
NGRAM4 = WD_EXTRACT_NGRAM + "\\Data\\multi_verbs\\4grams.csv"
NGRAM = WD_EXTRACT_NGRAM + "\\Data\\multi_verbs\\ngrams.csv"
TEMP_DIR = WD_EXTRACT_NGRAM + "\\Data"

# Final list of ngrams to use in training (5000)
TARGETS = WD_EXTRACT_NGRAM + "\\Data\\multi_verbs\\ngrams_touse.csv"
# Separate lists of chunks
TARGETS_1G = WD_EXTRACT_NGRAM + "\\Data\\multi_verbs\\1grams_touse.csv"
TARGETS_2G = WD_EXTRACT_NGRAM + "\\Data\\multi_verbs\\2grams_touse.csv"
TARGETS_3G = WD_EXTRACT_NGRAM + "\\Data\\multi_verbs\\3grams_touse.csv"
TARGETS_4G = WD_EXTRACT_NGRAM + "\\Data\\multi_verbs\\4grams_touse.csv"

### Parameters to use
NUM_THREADS = 4

### Get up to N ngrams from each ngram group such as all extracted ngrams have freq>=10
NGRAMN = 10000

######################################
# PREPARE CUES
######################################

WD_CUES = TOP + '\\Prepare_events'

### File paths
# list of ngrams to use in training (10k n-grams from each n level with 1<= n< =4)
NGRAMS = TARGETS
# list of ngrams to use in training (4681)
INFINITIVES = INFINITIVES_CSV
# final list of all cues
ALL_CUES = WD_CUES + '\\Data\\multi_verbs\\cues_touse.csv'