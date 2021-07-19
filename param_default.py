
####################################
# EXTRACT SENTENCES
####################################


NF = "necessary_files\\" # Where necessary files downloaded from the repo are stored
TOP = "" # Top level directory from which each subsequent process and file is run and saved

WD_EXTRACT = "" # The directory from which the sentence extraction takes place
TAGGED_FILE = "" # location of the tagged .txt file from which sentences are extracted
RESULTS_TSV = "" # Saved results of the sentence extraction as a .tsv
RESULTS_CSV = "" # Saved results of the sentence extraction as a .csv
SEP_CSV_FILES = "" # Saved results of the sentence extraction as a .csv to be used by other processes

EXTRACT_SENTENCES = [WD_EXTRACT, TAGGED_FILE, RESULTS_TSV, RESULTS_CSV, SEP_CSV_FILES]
######################################
# ANNOTATE TENSES                    
######################################

WD_ANNOTATE = "" # the directory from which sentence annotation takes place
SENTS = "" # the same as RESULTS_CSV

SENTS_CLEAN = "" # should be a csv file, the sentences are "cleaned" and then saved here
TENSES_ANNOTATED_NOINF = "" # a .csv file that holds the results of the annotation process on the sentences
TENSES_ANNOTATED_NOINF_CLEAN = "" # a .csv file that holds the results of the annotation process on the sentences but with unecessary columns removed
TENSES_ANNOTATED_CLEAN_N = "" # a .csv file that holds the results of the annotation process on the sentences but with unecessary columns removed

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
TENSES_ONE_SENT_PER_VERB_READY = TOP + "\\Data_shared\\tenses_annotated_one_sent_per_verb_ready.csv"
TENSES_ONE_SENT_PER_VERB_READY_GZ = TOP + "\\Data_shared\\tenses_annotated_one_sent_per_verb_ready.csv.gz"
TENSES_ONE_SENT_PER_VERB_SHUF_GZ = TOP + "\\Data_shared\\tenses_annotated_one_sent_per_verb_shuffeled.csv.gz"
TENSES_ONE_VERB = TOP + "\\Data_shared\\tenses_annotated_oneverb.csv"
TENSES_ONE_VERB_READY_GZ = TOP + "\\Data_shared\\tenses_annotated_oneverb_ready.csv.gz"
TENSES_ONE_VERB_SHUF_GZ = TOP + "\\Data_shared\\tenses_annotated_oneverb_shuffeled.csv.gz"
AE2BE_LIST = WD_PREPDAT +  "\\Data\\List_AE2BE.csv"
INFINITIVE_CORR_LIST = WD_PREPDAT +  "\\Data\\Infinitive_corrections_freq10.csv" 

######################################
# PREPARE TRAIN VALID TEST
######################################

### Define file paths
TENSES_MULTI_VERBS_TRAIN_GZ = TOP + "\\Data_shared\\tenses_one_sent_per_verb_train.csv.gz"
TENSES_MULTI_VERBS_VALID_GZ = TOP + "\\Data_shared\\tenses_one_sent_per_verb_valid.csv.gz"
TENSES_MULTI_VERBS_TEST_GZ = TOP + "\\Data_shared\\tenses_one_sent_per_verb_test.csv.gz"
# n-gram based event files ready for training NDL (verb infinitives included as cues)
NGRAM_EVENTS_MULTI_VERBS_TRAIN = TOP + "\\Data_shared\\Eventfiles_forNDL\\ngram_eventfile_multiverbs_train.gz"
NGRAM_EVENTS_MULTI_VERBS_VALID = TOP + "\\Data_shared\\Eventfiles_forNDL\\ngram_eventfile_multiverbs_valid.gz"
NGRAM_EVENTS_MULTI_VERBS_TEST = TOP + "\\Data_shared\\Eventfiles_forNDL\\ngram_eventfile_multiverbs_test.gz"
# word cue based event files ready for training NDL (verb infinitives included as cues)
WORD_EVENTS_MULTI_VERBS_TRAIN = TOP + "\\Data_shared\\Eventfiles_forNDL\\word_eventfile_multiverbs_train.gz"
WORD_EVENTS_MULTI_VERBS_VALID = TOP + "\\Data_shared\\Eventfiles_forNDL\\word_eventfile_multiverbs_valid.gz"
WORD_EVENTS_MULTI_VERBS_TEST = TOP + "\\Data_shared\\Eventfiles_forNDL\\word_eventfile_multiverbs_test.gz"

######################################
# EXTRACT INFINITIVES FOR TRAINING
######################################

WD_EXTRACT_INF = TOP + "\\extract_infinitives"
### Define file paths
TENSES_GZ = TOP + "\\Data_shared\\tenses_annotated_one_sent_per_verb_shuffeled.csv.gz"
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