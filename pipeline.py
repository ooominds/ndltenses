from ndl_tense.data_preparation import create_sentence_file, annotate_tenses, prepare_data, prepare_ndl_events
from ndl_tense import file_tools
from param_file import *
from os import chdir

def step_1():
    file_tools.manage_directories(EXTRACT_SENTENCES_DIRS, False)
    chdir(WD_EXTRACT)
    file_tools.manage_directories(EXTRACT_SENTENCES_FILES, True)
    create_sentence_file.run(EXTRACT_SENTENCES_FILES, {"gon":"VVG", "wan":"VVB", "innit":"VBB"})
    print("Step 1 complete")

def step_2():
    file_tools.manage_directories(ANNOTATE_DIRS, False)
    chdir(WD_ANNOTATE)
    file_tools.manage_directories(ANNOTATE_FILES, True)
    annotate_tenses.run(ANNOTATE_FILES)

def step_3():
    file_tools.manage_directories(PREPDAT_DIRS, False)
    chdir(WD_PREPDAT)
    file_tools.manage_directories(PREPDAT_FILES, True)
    file_tools.manage_directories(PREPARE_TRAIN_VALID_TEST_FILES, True)
    file_tools.manage_directories(CREATE_TRAIN_VALID_TEST_FILES, True)
    #for one verb per sent, so this is optional
    prepare_data.run(PREPDAT_FILES[0], PREPDAT_FILES[1:])
    prepare_ndl_events.prepare_files(CREATE_TRAIN_VALID_TEST_FILES)
    prepare_ndl_events.run(PREPARE_TRAIN_VALID_TEST_FILES)

#def step_4():
    #chdir(WD_EXTRACT_INF)
    #ndlt.data_preparation.extract_infinitives(TENSES_GZ, COOC_FREQ_CSV, INFINITIVES_CSV)

#def step_5():
#    os.chdir(WD_EXTRACT_NGRAM)
#    ndlt.data_preparation.extract_ngrams(TENSES_GZ,NGRAM,NGRAM1,NGRAM2,NGRAM3,NGRAM4,TEMP_DIR, NUM_THREADS)
#    ndlt.data_preparation.prepare_ngrams(TARGETS,NGRAM,NGRAM1,NGRAM2,NGRAM3,NGRAM4,TEMP_DIR, NGRAMN)

#def step_6():
#    os.chdir(WD_CUES)
#    ndlt.data_preparation.prepare_cues(NGRAMS, INFINITIVES, ALL_CUES)
def main():
    step_1()
    step_2()
    step_3()

if __name__ == "__main__":
    main()