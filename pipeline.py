from ndl_tense.data_preparation import create_sentence_file,annotate_tenses, prepare_data, prepare_ndl_events, extract_infinitive, extract_ngrams, prepare_ngrams, prepare_cues
#from ndl_tense.simulations import ndl_model
from ndl_tense.post_processing import top_cues_for_sen
from ndl_tense import file_tools
from param_file import *
from os import chdir

def step_1():
    file_tools.manage_directories(EXTRACT_SENTENCES_DIRS, False)

    chdir(WD_EXTRACT)
    file_tools.manage_directories(EXTRACT_SENTENCES_FILES, True)
    
    # we remove colloquial spelling tokens like "gon", "wan" and "innit" here
    # the final parameter is for verbosity (whether to print the output of the process as we go along)
    #create_sentence_file.run(EXTRACT_SENTENCES_FILES, {"gon":"VVG", "wan":"VVB", "innit":"VBB"}, False,True, False)
    create_sentence_file.run(EXTRACT_SENTENCES_FILES, {}, False, True, True)
    #create_sentence_file.run(EXTRACT_SENTENCES_FILES, {}, True, False)

def step_2():
    file_tools.manage_directories(ANNOTATE_DIRS, False)
    chdir(WD_ANNOTATE)
    file_tools.manage_directories(ANNOTATE_FILES, True)

    # the final parameter is for verbosity (whether to print the output of the process as we go along)
    annotate_tenses.run(ANNOTATE_FILES, False)

def step_3():
    file_tools.manage_directories(PREPDAT_DIRS, False)
    chdir(WD_PREPDAT)
    file_tools.manage_directories(PREPDAT_FILES, True)
    file_tools.manage_directories(PREPARE_TRAIN_VALID_TEST_FILES, False)

    #optional
    #sample_sentences.run(TENSES_ONE_SENT_PER_VERB_WITH_MODALS, kets, ratios, 500, False)

    # the final parameter is for verbosity (whether to print the output of the process as we go along)
    file_tools.manage_directories(CREATE_TRAIN_VALID_TEST_FILES, False)

    #for one verb per sent, so this is optional
    prepare_data.run(PREPDAT_FILES, False)
    chdir(WD_PREPDAT)
    prepare_ndl_events.prepare_files(CREATE_TRAIN_VALID_TEST_FILES, PROP_TEST, PROP_VALID, False)

    # the final parameter is for verbosity (whether to print the output of the process as we go along)
    prepare_ndl_events.run(PREPARE_TRAIN_VALID_TEST_FILES, False)

def step_4():
    file_tools.manage_directories(EXTRACT_SENTENCES_FOLDERS, False)
    file_tools.manage_directories(EXTRACT_INFINITIVE_FILES, True)
    chdir(WD_EXTRACT_INF)

    # the final parameter is for verbosity (whether to print the output of the process as we go along)
    extract_infinitive.run(EXTRACT_INFINITIVE_FILES, False)

def step_5():
    file_tools.manage_directories(NGRAM_FOLDERS, False)
    chdir(WD_EXTRACT_NGRAM)
    file_tools.manage_directories(NGRAM_FILES, True)
    file_tools.manage_directories(TARGETS_FILES, True)

    # extracting ngrams by frequency is optional
    # extract_ngrams.run(TENSES_GZ, NGRAM_FILES, TEMP_DIR_EXT, NUM_THREADS)

    # the final parameter is for verbosity (whether to print the output of the process as we go along)
    prepare_ngrams.run(NGRAM_FILES, K_NGRAMS, TARGETS_FILES, False)

def step_6():
    file_tools.manage_directories([WD_CUES], False)
    chdir(WD_CUES)

    # the final parameter is for verbosity (whether to print the output of the process as we go along)
    prepare_cues.run(NGRAMS, INFINITIVES, ALL_CUES, False)

def step_7():
    file_tools.manage_directories(SIM_DIR, False)
    chdir(WD_SIM)
    ndl_model.run(SIM_FILES, SIM_PARAMS)

def main():
    #uncomment each step you wish to complete
    step_1()
    #step_2()
    #step_3()
    #step_4()
    #step_5()
    #step_6()
    #step_7()
    # keys = ["present.simple","past.simple",
    #        "present.perf","future.simple",
    #        "present.prog","past.perf",
    #        "present.perf.prog","future.prog",
    #        "past.perf.prog","future.perf",
    #        "future.perf.prog"]

    # ratios = [655438,610475,100503,67433,46884,45191,26264,3398,2336,1288,660,9]
    #chdir('D:\\work\\OoOM\\ndl\\test_location\\test')
    #top_cues_for_sen.run("tenses_file", "cue_weights", "result_file", [1410, 441, 133, 132], 5, 500)
    #top_cues_for_sen.run("tenses_file", "cue_weights", "result_file", [655438,610475,100503,67433,46884,45191,26264,3398,2336,1288,660,9], 5, 500)

if __name__ == "__main__":
    main()