import ndl_tense as ndlt
from param_file import *
import os

def step_1():
    os.chdir(WD_EXTRACT)
    ndlt.data_preparation.create_sentence_file(BNC_TAGGED_ALL, RESULTS_TSV, RESULTS_CSV, SEP_CSV_FILES)

def step_2():
    os.chdir(WD_ANNOTATE)
    ndlt.data_preparation.annotate_tenses(RESULTS_CSV, BNC_SENTS_CLEAN, TENSES_ANNOTATED_NOINF, TENSES_ANNOTATED_NOINF_CLEAN, TENSES_ANNOTED_CLEAN_N)

def step_3():
    os.chdir(WD_PREPDAT)
    ndlt.data_preparation.prepare_data(TENSES, TENSES_WITH_INF, TENSES_WITH_INF_NEW, TENSES_ONE_SENT_PER_VERB,
                                       TENSES_ONE_SENT_PER_VERB_WITH_MODALS, TENSES_ONE_SENT_PER_VERB_READY, TENSES_ONE_SENT_PER_VERB_READY_GZ,
                                       TENSES_ONE_SENT_PER_VERB_SHUF_GZ, TENSES_ONE_VERB, TENSES_ONE_VERB_READY_GZ,
                                       TENSES_ONE_VERB_SHUF_GZ, AE2BE_LIST, INFINITIVE_CORR_LIST)
    ndlt.data_preparation.prepare_ndl_events(TENSES_MULTI_VERBS_TRAIN_GZ, TENSES_MULTI_VERBS_VALID_GZ, TENSES_MULTI_VERBS_TEST_GZ,
                                             NGRAM_EVENTS_MULTI_VERBS_TRAIN, NGRAM_EVENTS_MULTI_VERBS_VALID, NGRAM_EVENTS_MULTI_VERBS_TEST,
                                             WORD_EVENTS_MULTI_VERBS_TRAIN, WORD_EVENTS_MULTI_VERBS_VALID,WORD_EVENTS_MULTI_VERBS_TEST)
def step_4():
    os.chdir(WD_EXTRACT_INF)
    ndlt.data_preparation.extract_infinitives(TENSES_GZ, COOC_FREQ_CSV, INFINITIVES_CSV)

def step_5():
    os.chdir(WD_EXTRACT_NGRAM)
    ndlt.data_preparation.extract_ngrams(TENSES_GZ,NGRAM,NGRAM1,NGRAM2,NGRAM3,NGRAM4,TEMP_DIR, NUM_THREADS)
    ndlt.data_preparation.prepare_ngrams(TARGETS,NGRAM,NGRAM1,NGRAM2,NGRAM3,NGRAM4,TEMP_DIR, NGRAMN)

def step_6():
    os.chdir(WD_CUES)
    ndlt.data_preparation.prepare_cues(NGRAMS, INFINITIVES, ALL_CUES)
