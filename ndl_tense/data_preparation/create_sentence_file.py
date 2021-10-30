####################
# Preliminary steps
####################

### Import necessary libraries
import os
import re
import logging
#logger = logging.getLogger("data_preparation")
#logger.setLevel(level=logging.INFO)

from collections import OrderedDict
import pandas as pd
import numpy as np
import time
#from nltk.stem.wordnet import WordNetLemmatizer


###################
# Useful functions
###################
    

def process_token(line, end_sent_marks, to_remove, KEEP_ORIGINAL_TOKEN, NORMALISE=True):

    """Skip or extract a cleaned token from a tagged line from a written COCA file

    ----------
    PARAMETERS
    ----------
    line: str
        one line from a COCA file

    -------
    RETURNS
    -------
    str or None
        cleaned token or nothing
    Note: the returned token will be lower-cased 
    """

    ### Initialise regex patterns
    seq_dash_pattern = re.compile(r'^[a-z0-9]+(\-[a-z0-9]+){1,}$') # for sequence of words seperated with dashs
    seq_slash_pattern = re.compile(r'^[a-z0-9]+(\/[a-z0-9]+){1,}$') # for sequence of words seperated with slashs
    wrong_dot_pattern = re.compile(r'^[a-z]{5,}\.$') # for words that mistakenly end with a dot. 
                                                    # (the dot should be seperated with spaces).
    wrong_dot_pattern_digits = re.compile(r'^[0-9]+\.$') # for words that mistakenly end with a dot. 
                                                    # (the dot should be seperated with spaces).
    abbreviation_dot_pattern = re.compile(r'^[a-z]{2,4}\.$')   
    wrong_end_pattern = re.compile(r'^[a-z]{2,}[\-|\/]$') # for words that mistakenly end with a dash or a slash. 
    special_char_pattern = re.compile(r'[\d\W]+') # for words containing special characters (@@)
    num_char_pattern = re.compile(r'[0-9]+') # for words containing numbers characters
    
    # Format of the line
    line_elements = line.strip('\n').split('\t')
    try: 
        token, tag = line_elements
        if NORMALISE:
            token = token.lower()
    # skip lines with no token or tag
    except(ValueError):
            return None 

    ### Going through all the filters using if statements
    for token_r, tag_r in to_remove.items():            
        # remove unwanted tags and tokens
        if token == token_r and tag == tag_r:
            return "CTBD", "DEL"
    # Remove possessive 's
    if tag == 'POS':
        return None

    # Convert contractions
    elif token == "n't":
        return 'not', tag
    elif token == "'m" and tag == 'VBB':
        return 'am', tag
    elif token == "'s" and tag == 'VBZ':
        return 'is', tag
    elif token == "'re" and tag == 'VBB':
        return 'are', tag
    elif token == "'ve" and tag == 'VHB':
        return 'have', tag
    elif token == "'s" and tag == 'VHZ':
        return 'has', tag
    elif token == "'d" and tag in ('VHD', 'VHN'):
        return 'had', tag
    elif token == "'d" and tag == 'VM0':
        return 'would', tag
    elif token == "'ll" and tag == 'VM0':
        return 'will', tag
    elif token == "'s" and tag == 'VDZ':
        return 'does', tag
    # Correct can (from can't) and will (from won't)
    elif token == 'ca' and tag == 'VM0':
        return 'can', tag
    elif token == 'wo' and tag == 'VM0':
        return 'will', tag    
    # Split words seperated with a dash
    elif seq_dash_pattern.search(token):
        if NORMALISE:
            words = token.lower().split('-')
        else:
            words = token.split('-')
        for word in words:
            if special_char_pattern.search(word):
                words.remove(word)
        if len(words) == 1:
            return words[0], tag
        elif len(words) > 1:
            return words, tag
        else:
            return None
    
    # Split words seperated with a slash
    elif seq_slash_pattern.search(token):
        if NORMALISE:
            words = token.lower().split('/')
        else:
            words = token.split('/')
        for word in words:
            if special_char_pattern.search(word):
                words.remove(word)
        if len(words) == 1:
            return words[0], tag
        elif len(words) > 1:
            return words, tag
        else:
            return None

    # Process words that end with a sentence's end marker 
    elif wrong_dot_pattern.search(token):
        return [token[:-1], token[-1]], tag

    # Process numbers that end with a sentence's end marker 
    elif wrong_dot_pattern_digits.search(token):
        return token[-1], 'PUN'

    # Process abbreviations that end with a dot
    elif abbreviation_dot_pattern.search(token):
        return token[:-1], tag 

    # Process words that mistakenly end with a dash or a slash
    elif wrong_end_pattern.search(token):
        return token[:-1], tag 

    # Keep end of sentence or paragraph markers 
    elif token in end_sent_marks and tag == 'PUN':
        return token, tag

    # Remove words containing special characters other than '.', '!' or end of document markers (e.g. @ and numbers)
    elif special_char_pattern.search(token):
        if num_char_pattern.search(token) and KEEP_ORIGINAL_TOKEN:
            return token, tag
        else:
            return None
    else:
        return token, tag

"""
        # Record start time
        start = time.time()
        keep_sen = True
        for ii, line in enumerate(f):
            try:
                if KEEP_ORIGINAL_SEN:
                    token, tag = process_token(line, end_sent_marks, to_remove, True, False)
                else:
                    token, tag = process_token(line, end_sent_marks, to_remove, False, True)
            except:
                continue
            if token == "CTBD":
                current_sent, current_verbs, o_current_sent = [], [], []
                keep_sen = False
            if keep_sen:
"""


def extend_all_sents(current_verbs, current_sent, all_sents):

    if len(current_verbs) > 0 and len(current_sent) > 2: # no one-word sentences or sentences without verbs
        current_sent_str = " ".join(current_sent)
        # only if sentence is new, add to dictionary
        if current_sent_str not in all_sents:
            all_sents[current_sent_str] = current_verbs
    return(all_sents)

def extract_sentences(file, to_remove, KEEP_ORIGINAL_SEN, VERBOSE):

    """ Extract a cleaned list of all sentences in a tagged BNC file

    Parameters
    ----------
    file: str
        path to the tagged BNC file to extract the sentences from 

    Returns
    -------
    list
        cleaned list of all sentences in file
    """ 

    ### Useful variables
    # End of sentence marks
    end_sent_marks = (".", "!", "?", "</s>", "</u>")

    all_sents = OrderedDict()
    current_sent = [] # Current list of words in the currently processed sentence
    current_verbs = [] # Current list of verbs in the currently processed sentence

    with open(file, mode = 'r', encoding = 'utf-8') as f:

        # Record start time
        start = time.time()
        keep_sen = True
        for ii, line in enumerate(f):
            try:
                if KEEP_ORIGINAL_SEN:
                    token, tag = process_token(line, end_sent_marks, to_remove, True, False)
                else:
                    token, tag = process_token(line, end_sent_marks, to_remove, False, True)
            except:
                continue
            if token == "CTBD":
                current_sent, current_verbs = [], []
                keep_sen = False
            if keep_sen:
                if isinstance(token, list) : 
                    current_sent.extend(token) 
                elif token in end_sent_marks: # marker for the end of a sentence
                    if KEEP_ORIGINAL_SEN:
                        current_sent.extend(token)
                    all_sents = extend_all_sents(current_verbs, current_sent, all_sents)
                    current_sent, current_verbs = [], [] # reinitialise the sent and verbs
                else:
                    current_sent.append(token)
                    if tag.lower().startswith("v"): 
                        if "-" in tag: # Exclude sentences having ambiguous verb tags
                            current_sent = [] # reinitialise the sent
                            current_verbs = [] # reinitialise the verbs
                        else:
                            current_verbs.append([token, tag, len(current_sent) - 1])     
            else:
                if token in end_sent_marks:
                    keep_sen = True
            if (ii+1) % 1000000 == 0 and VERBOSE:
                print('{} lines processed in {}s\n'.format(ii+1, (time.time() - start)))
        if VERBOSE:
            print('{} lines processed in {}\n'.format(ii+1, (time.time() - start)))
        return all_sents

def add_column_to_file(file_1, file_2, col_to_join, new_col_name, position):
    table1 = pd.read_csv("{}.csv".format(file_1))
    table2 = pd.read_csv("{}.csv".format(file_2))
    table1[new_col_name] = table2[col_to_join]
    
    new_col = table1.pop(new_col_name)
    table1.insert(position, new_col.name, new_col)

    table1.to_csv("%s.csv"%(file_1), index=False)

def run(EXTRACT_SENTENCES_FILES, TO_REMOVE, TO_TSV=False, KEEP_ORIGINAL_SEN=False, VERBOSE=True):
    """
    Carry out this step of processing and create a file of sentences with
    verbs, verb tags, verb tags, sentences and sentence length

    ----
    PARAMETERS
    ----
    EXTRACT_SENTENCES_FILES: list
        files needed to complete this stage of the processing,
        these can be found in the parameter file

    TO_REMOVE: list
        A list of tags of types of words to remove from the processing. This could be useful for removing
        unclear words or colloqual terms.
    TO_TSV: boolean
        whether to also save .tsv files of the results of this step
    KEEP_ORIGINAL_SEN:
        whether to keep the original sentence
    VERBOSE: boolean
        whether to log the process
    ----
    RETURN: Does not return anything, creates an annotated file
    ----
    """  

    TAGGED_FILE, RESULTS = EXTRACT_SENTENCES_FILES[0], EXTRACT_SENTENCES_FILES[1] 
    sentences = extract_sentences("{}.txt".format(TAGGED_FILE), TO_REMOVE, KEEP_ORIGINAL_SEN, VERBOSE) # 43264 with ambiguous verb tags / 40436 without
    # turn into dictionary of dictionary representation
    start = time.time()
    sentences_dict = dict()
    for i, (sent, verbs) in enumerate(sentences.items()):
        sentences_dict[i] = dict()
        sentences_dict[i]["sentence"] = sent
        sentences_dict[i]["sentence_length"] = len(sent.split())
        sentences_dict[i]["num_verb_tags"] = len(verbs)
        for j, (verb, tag, position) in enumerate(verbs):
            sentences_dict[i]["verb_{}".format(j+1)] = verb
            sentences_dict[i]["verb_{}_tag".format(j+1)] = tag
            sentences_dict[i]["verb_{}_position".format(j+1)] = position + 1
    if VERBOSE:
        print('Dictionary of dictionary constructed in {}s\n'.format((time.time()- start)))

    # turn into data frame
    start = time.time()
    sentences_df = pd.DataFrame.from_dict(sentences_dict, orient="index")
    if VERBOSE:
        print('Dataframe constructed in {}s\n'.format((time.time()- start)))

    if TO_TSV:
        file_type = "tsv"
    else:
        file_type = "csv"
    # write to csv file
    with open("%s.%s"%(RESULTS, file_type), "w", encoding="utf-8") as res_csv:
        sentences_df.to_csv(res_csv, sep = ",", index = False, encoding="utf-8")
    if VERBOSE:
        print('STEP 1: Creating the extracted sentences file is complete')
