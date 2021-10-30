from ndl_tense.data_preparation import create_sentence_file,annotate_tenses, prepare_data, prepare_ndl_events, extract_infinitive, extract_ngrams, prepare_ngrams, prepare_cues

#below import commented out for now, uncomment if you want to run step 6
from ndl_tense.simulations import ndl_model
#from ndl_tense.post_processing import top_cues_for_sen, sample_sentences
from ndl_tense import file_tools
from param_file import *
from os import chdir

def step_1():
    # create folders specified by the list stored in EXTRACT_SNETNECES_DIRS
    file_tools.manage_directories(EXTRACT_SENTENCES_DIRS, False)
    chdir(WD_EXTRACT) # change working directory to the path in WD_EXTRACT

    # create folders specified by the list stored in EXTRACT_SNETNECES_FILES
    # the "True" means that the paths in the list are for files and not directories
    file_tools.manage_directories(EXTRACT_SENTENCES_FILES, True)
    
    # (The default paramenters are the ones set here)
    # create_sentence_file: (list of file paths),
    #                       {dictionary of token:tag pairs to remove from corpus} - # we remove colloquial spelling tokens like "gon", "wan" and "innit" here,
    #                       "True" = create a .tsv of the output,
    #                       True = keep the original sentence | False = "clean" it to be used for training an ndl model
    #                       the final parameter is for verbosity True = print the output of the process as we go along
    # The default paramenters are the ones set here 
    #  so this can be run with a call like create_sentence_file.run(EXTRACT_SENTENCES_FILES, {"gon":"VVG", "wan":"VVB", "innit":"VBB"}) and have the same result

    create_sentence_file.run(EXTRACT_SENTENCES_FILES, {"gon":"VVG", "wan":"VVB", "innit":"VBB"}, False, False, True)

def step_2():
    # create folders specified by the list stored in ANNOTATE_DIRS
    file_tools.manage_directories(ANNOTATE_DIRS, False)
    chdir(WD_ANNOTATE) # change working directory to the path in WD_EXTRACT

    # create folders specified by the list stored in ANNOTATE_FILES
    # the "True" means that the paths in the list are for files and not directories
    file_tools.manage_directories(ANNOTATE_FILES, True)

    # the final parameter is for verbosity (True = print the output of the process as we go along)
    annotate_tenses.run(ANNOTATE_FILES, True)

def step_3():
    file_tools.manage_directories(PREPDAT_DIRS, False)
    chdir(WD_PREPDAT)
    file_tools.manage_directories(PREPDAT_FILES, True)
    file_tools.manage_directories(PREPARE_TRAIN_VALID_TEST_FILES, True)

    #optional
    #sample_sentences.run(TENSES_ONE_SENT_PER_VERB_WITH_MODALS, kets, ratios, 500, False)

    # the final parameter is for verbosity (True =  print the output of the process as we go along)
    file_tools.manage_directories(CREATE_TRAIN_VALID_TEST_FILES, True)

    prepare_data.run(PREPDAT_FILES, True)
    chdir(WD_PREPDAT)
    prepare_ndl_events.prepare_files(CREATE_TRAIN_VALID_TEST_FILES, PROP_TEST, PROP_VALID, True)

    # the final parameter is for verbosity (True =  print the output of the process as we go along)
    prepare_ndl_events.run(PREPARE_TRAIN_VALID_TEST_FILES, 'NgramCuesWithInfinitive', True)

def step_4():
    file_tools.manage_directories(EXTRACT_SENTENCES_FOLDERS, False)
    file_tools.manage_directories(EXTRACT_INFINITIVE_FILES, True)
    chdir(WD_EXTRACT_INF)

    # the final parameter is for verbosity (True = print the output of the process as we go along)
    extract_infinitive.run(EXTRACT_INFINITIVE_FILES, True)

def step_5():
    file_tools.manage_directories(NGRAM_FOLDERS, False)
    chdir(WD_EXTRACT_NGRAM)
    file_tools.manage_directories(NGRAM_FILES, True)
    file_tools.manage_directories(TARGETS_FILES, True)

    # extracting ngrams by frequency is optional
    extract_ngrams.run(TENSES_GZ, NGRAM_FILES, TEMP_DIR_EXT, NUM_THREADS)

    # the final parameter is for verbosity (whether to print the output of the process as we go along)
    prepare_ngrams.run(NGRAM_FILES, K_NGRAMS, TARGETS_FILES, False)

def step_6():
    file_tools.manage_directories([WD_CUES], False)
    chdir(WD_CUES)

    # the final parameter is for verbosity (whether to print the output of the process as we go along)
    prepare_cues.run(NGRAMS, INFINITIVES, ALL_CUES, True)

def step_7():
    file_tools.manage_directories(SIM_DIR, False)
    chdir(WD_SIM)
    ndl_model.run(SIM_FILES, SIM_PARAMS)

def main():
    # uncomment by deleting hashtag for each step you wish to complete
    #step_1()
    #step_2()
    #step_3()
    #step_4()
    #step_5()
    #step_6() 
    step_7() #requires you to uncomment an import line at the top

if __name__ == "__main__":
    main()