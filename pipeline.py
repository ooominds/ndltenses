from ndl_tense.data_preparation import create_sentence_file,annotate_tenses, prepare_data, prepare_ndl_events, extract_infinitive, extract_ngrams, prepare_ngrams, prepare_cues
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
    print("Step 2 complete")

def step_3():
    file_tools.manage_directories(PREPDAT_DIRS, False)
    chdir(WD_PREPDAT)
    file_tools.manage_directories(PREPDAT_FILES, True)
    file_tools.manage_directories(PREPARE_TRAIN_VALID_TEST_FILES, True)
    file_tools.manage_directories(CREATE_TRAIN_VALID_TEST_FILES, True)
    #for one verb per sent, so this is optional
    prepare_data.run(PREPDAT_FILES[0], PREPDAT_FILES[1:])
    chdir(WD_PREPDAT)
    prepare_ndl_events.prepare_files(CREATE_TRAIN_VALID_TEST_FILES)
    prepare_ndl_events.run(PREPARE_TRAIN_VALID_TEST_FILES)
    print("Step 3 complete")

def step_4():
    file_tools.manage_directories(EXTRACT_SENTENCES_FOLDERS, False)
    file_tools.manage_directories(EXTRACT_INFINITIVE_FILES, True)
    chdir(WD_EXTRACT_INF)
    extract_infinitive.run(EXTRACT_INFINITIVE_FILES)
    print("Step 4 complete")

def step_5():
    file_tools.manage_directories(NGRAM_FOLDERS, False)
    chdir(WD_EXTRACT_NGRAM)
    file_tools.manage_directories(NGRAM_FILES, True)
    file_tools.manage_directories(TARGETS_FILES, True)
    extract_ngrams.run(TENSES_GZ, NGRAM_FILES, TEMP_DIR, NUM_THREADS)
    prepare_ngrams.run(NGRAM_FILES, K_NGRAMS, TARGETS_FILES)

def step_6():
    file_tools.manage_directories([WD_CUES], False)
    chdir(WD_CUES)
    prepare_cues.run(NGRAMS, INFINITIVES, ALL_CUES)

def main():
    #step_1()
    #step_2()
    #step_3()
    #step_4()
    #step_5()
    #step_6()

if __name__ == "__main__":
    main()