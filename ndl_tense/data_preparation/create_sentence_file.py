####################
# Preliminary steps
####################

### Import necessary libraries
import os
import re
from collections import OrderedDict
import pandas as pd
import numpy as np
import sys
import time
#from nltk.stem.wordnet import WordNetLemmatizer


###################
# Useful functions
###################
    

def process_token(line, end_sent_marks, to_remove):

    """Skip or extract a cleaned token from a tagged line from a written COCA file

    Parameters
    ----------
    line: str
        one line from a COCA file

    Returns
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
    special_char_pattern = re.compile(r'[\d\W]+') # for words containing special characters (e.g. numbers or @@)
    
    # Format of the line
    line_elements = line.strip('\n').split('\t')
    try: 
        token, tag = line_elements
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
        words = token.lower().split('-')
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
        words = token.lower().split('/')
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
        return None

    else:
        return token, tag

def extract_sentences(file, to_remove):

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

    #all_sents = [] # Current list of all extracted sentences  
    all_sents = OrderedDict()
    current_sent = [] # Current list of words in the currently processed sentence
    current_verbs = [] # Current list of verbs in the currently processed sentence

    with open(file, mode = 'r', encoding = 'utf-8') as f:

        # Record start time
        start = time.time()
        keep_sen = True
        for ii, line in enumerate(f):
            try:
                token, tag = process_token(line, end_sent_marks, to_remove)
            except:
                continue
            if token == "CTBD":
                current_sent, current_verbs = [], []
                keep_sen = False
            if keep_sen:
                # For sequence of tokens
                if isinstance(token, list): 
                    if (token[-1] == '.'): 
                        current_sent.extend(token[:-1])
                        if len(current_verbs) > 0 and len(current_sent) > 2: # no one-word sentences or sentences without verbs
                            current_sent_str = " ".join(current_sent)
                            # only if sentence is new, add to dictionary
                            if current_sent_str not in all_sents:
                                all_sents[current_sent_str] = current_verbs
                        current_sent = [] # reinitialise the sent
                        current_verbs = [] # reinitialise the verbs
                    else: # Case of a sequence of words
                        current_sent.extend(token) 
                elif token in end_sent_marks: # marker for the end of a sentence
                    if len(current_verbs) > 0 and len(current_sent) > 2: # no one-word sentences or sentences without verbs
                        current_sent_str = " ".join(current_sent)
                        if current_sent_str not in all_sents:
                            all_sents[current_sent_str ] = current_verbs
                    current_sent = [] # reinitialise the sent
                    current_verbs = [] # reinitialise the verbs
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
            if (ii+1) % 1000000 == 0:
                sys.stdout.write('%d lines processed in %.0fs\n' % (ii+1, (time.time() - start)))
                sys.stdout.flush()

        sys.stdout.write('%d lines processed in %.0fs\n' % (ii+1, (time.time() - start)))
        sys.stdout.flush()
        return all_sents


def run(EXTRACT_SENTENCES_FILES, TO_REMOVE, TO_TSV):
    TAGGED_FILE, RESULTS = EXTRACT_SENTENCES_FILES[0], EXTRACT_SENTENCES_FILES[1]
    sentences = extract_sentences("%s.txt"%(TAGGED_FILE), TO_REMOVE) # 43264 with ambiguous verb tags / 40436 without
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
    sys.stdout.write('Dictionary of dictionary constructed in %.3fs\n' % ((time.time()- start)))
    sys.stdout.flush()

    # turn into data frame
    start = time.time()
    sentences_df = pd.DataFrame.from_dict(sentences_dict, orient="index")
    sys.stdout.write('Dataframe constructed in %.3fs\n' % ((time.time()- start)))
    sys.stdout.flush()

    if TO_TSV:
        file_type = "tsv"
    else:
        file_type = "csv"
    # write to csv file
    with open("%s.%s"%(RESULTS, file_type), "w", encoding="utf-8") as res_csv:
        sentences_df.to_csv(res_csv, sep = ",", index = False, encoding="utf-8")
