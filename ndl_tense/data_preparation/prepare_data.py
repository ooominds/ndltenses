#!/usr/bin/python3

####################
# Preliminary steps
####################

### Import necessary packages
import os
from param_file import PREPDAT_DIRS
import pandas as pd
import numpy as np
import re
import time
import sys
import csv 
import random
import string
#from tqdm import tqdm
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.util import ngrams
from collections import Counter
#nltk.download('wordnet')
#tqdm.pandas()

def convert_to_inf(TENSES, TENSES_WITH_INF):
    lemmatizer = WordNetLemmatizer() # Initialise the lemmatizer

    ### Set the max width of a column
    pd.set_option('display.max_colwidth', 150)
    pd.set_option('display.max_columns', 150)

    #############################################
    # Remove numbers (if any) from the sentences
    #############################################

    ### Load the data
    tenses = pd.read_csv(TENSES, encoding="utf-8")
    #print(f'Number of examples: {len(tenses)}')
    # Number of examples: 4227346

    # Columns
    tenses.columns
    # Index(['Sentence', 'Tense1', 'VerbForm1', 'MainVerb1', 'Position1',
    #        'Infinitive1', 'Tense2', 'VerbForm2', 'MainVerb2', 'Position2',
    #        'Infinitive2', 'Tense3', 'VerbForm3', 'MainVerb3', 'Position3',
    #        'Infinitive3', 'Tense4', 'VerbForm4', 'MainVerb4', 'Position4',
    #        'Infinitive4', 'Tense5', 'VerbForm5', 'MainVerb5', 'Position5',
    #        'Infinitive5', 'Tense6', 'VerbForm6', 'MainVerb6', 'Position6',
    #        'Infinitive6', 'Tense7', 'VerbForm7', 'MainVerb7', 'Position7',
    #        'Infinitive7', 'Tense8', 'VerbForm8', 'MainVerb8', 'Position8',
    #        'Infinitive8', 'Tense9', 'VerbForm9', 'MainVerb9', 'Position9',
    #        'Infinitive9', 'Tense10', 'VerbForm10', 'MainVerb10', 'Position10',
    #        'Infinitive10', 'Tense11', 'VerbForm11', 'MainVerb11', 'Position11',
    #        'Infinitive11', 'Tense12', 'VerbForm12', 'MainVerb12', 'Position12',
    #        'Infinitive12', 'Tense13', 'VerbForm13', 'MainVerb13', 'Position13',
    #        'Infinitive13', 'Tense14', 'VerbForm14', 'MainVerb14', 'Position14',
    #        'Infinitive14', 'Tense15', 'VerbForm15', 'MainVerb15', 'Position15',
    #        'Infinitive15', 'Tense16', 'VerbForm16', 'MainVerb16', 'Position16',
    #        'Infinitive16', 'Tense17', 'VerbForm17', 'MainVerb17', 'Position17',
    #        'Infinitive17'],
    #       dtype='object')

    # Remove words containing digits
    #tenses["Sentence"] = tenses["Sentence"].progress_apply(lambda s: ' '.join([w for w in s.split() if not any(l.isdigit() for l in w)]))

    #########################
    # Adding the infinitives
    #########################

    nC = tenses.shape[1] # number of columns 
    nR = tenses.shape[0] # number of rows
    nV = int((nC-1)/5)  # number of verbs 

    ### Convert infinitive columns to str
    for j in range(1, (nV+1)):
        col_name_j = "".join(['Infinitive', str(j)])
        tenses[col_name_j] = tenses[col_name_j].astype(str)

    ### Convert main verbs into infinitives using the nltk lemmatizer 
    # Record start time
    start = time.time()
    for i in range(0, nR):

        # Progress message
        if (i+1) % 100000 == 0:
            now = time.time()
            sys.stdout.write('-%d iterations completed in %.0fs\n' % ((i+1), (now - start)))
            sys.stdout.flush()

        for j in range(1, (nV+1)):
            if str(tenses.at[i, "".join(['MainVerb', str(j)])]) != 'nan':
                tenses.at[tenses.index[i], "".join(['Infinitive', str(j)])] = lemmatizer.lemmatize(tenses.loc[tenses.index[i], "".join(['MainVerb', str(j)])], 'v')
            else:
                tenses.at[tenses.index[i], "".join(['Infinitive', str(j)])] = np.nan
    tenses.to_csv(TENSES_WITH_INF, index = False, encoding="utf-8")

##############################################
# Adding Sentence lengths and number of verbs
##############################################
def add_sen_length(TENSES_WITH_INF, TENSES_WITH_INF_NEW):
    ### Load the data
    tenses = pd.read_csv(TENSES_WITH_INF)

    nC = tenses.shape[1] # number of columns 
    nR = tenses.shape[0] # number of rows
    nV = int((nC-1)/5)  # number of verbs 

    #print("number of verbs: %s"%(nV))

    ### Add SentLength column
    tenses['SentenceLength'] = tenses['Sentence'].apply(lambda s: len(s.split(' '))) 

    ### Add NumOfVerbs column
    # Initialising the column
    tenses['NumOfVerbs'] = 0
    # Record start time
    start = time.time()
    for i in range(0, nR):
        # Progress message
        if (i+1) % 100000 == 0:
            now = time.time()
            sys.stdout.write('-%d iterations completed in %.0fs\n' % ((i+1), (now - start)))
            sys.stdout.flush()
        for j in range(1, (nV+1)):
            if str(tenses.at[i, "".join(['Tense', str(j)])]) != 'nan':
                continue
            else:
                break 
        tenses.at[i, 'NumOfVerbs'] = j

    # move the columns after the 'Sentence' column
    cols = list(tenses.columns)
    cols.insert(1, cols.pop(cols.index('SentenceLength')))
    cols.insert(2, cols.pop(cols.index('NumOfVerbs')))
    tenses = tenses.loc[:, cols]
    tenses = tenses[tenses.NumOfVerbs !=0 ]
    ### Add a column that has SentenceID (useful when dividing into train/valid/test sets)
    tenses['SentenceID'] = np.arange(1, (len(tenses)+1))

    # Move the columns before the 'Sentence' column
    cols = list(tenses.columns)
    cols.insert(0, cols.pop(cols.index('SentenceID')))
    tenses = tenses.loc[:, cols]

    # Export the dataset
    tenses.to_csv(TENSES_WITH_INF_NEW, index = False, encoding="utf-8")

######################################
# Remove sentences with no tense/verb
######################################

def remove_sen(TENSES_WITH_INF_NEW, TENSES_ONE_SENT_PER_VERB_WITH_MODALS):
    #####################################
    # New dataset with one verb per row
    #####################################

    ### Load the data
    tenses = pd.read_csv(TENSES_WITH_INF_NEW)
    ### Extract all verbs from each sentence and put them in seperate rows (these will be the bases of our events)
    nC = tenses.shape[1] # number of columns 
    nR = tenses.shape[0] # number of rows
    nV = int((nC-4)/5)  # number of verbs 

    # Write to the csv file that encodes the results
    with open(TENSES_ONE_SENT_PER_VERB_WITH_MODALS, mode = 'w', encoding="utf-8") as o:
        csv_writer = csv.writer(o, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        heading = list(tenses.columns[0:4])
        heading.extend(['Tense', 'VerbForm', 'MainVerb', 'Position', 'Infinitive'])
        csv_writer.writerow(heading)

        # Record start time
        start = time.time()
        for i in range(0, nR):

            # Progress message
            if (i+1) % 100000 == 0:
                now = time.time()
                sys.stdout.write('-%d iterations completed in %.0fs\n' % ((i+1), (now - start)))
                sys.stdout.flush()

            for j in range(1, (nV+1)):
                if str(tenses.at[i, "".join(['Tense', str(j)])]) != 'nan':
                    # Write the row
                    colnames_touse = ['SentenceID', 'Sentence', 'SentenceLength', 'NumOfVerbs']
                    colnames_touse.extend([colname + str(j) for colname in ['Tense', 'VerbForm', 'MainVerb', 'Position', 'Infinitive']])
                    _ = csv_writer.writerow(list(tenses.iloc[i][colnames_touse]))
                    o.flush()
                else:
                    break

#################################################################################
# Convert words in the Sentence, VerbForm and MainVerb columns to British English


### Useful functions

# Function that can load a dictionary from a csv file
def import_dict(dict_path):

    """Import a two-column csv file as dictionary

    Parameters
    ----------
    dict_path: str
        path of the csv file 

    Returns
    -------
    dict
        mapping from keys to values
    """

    # Load the index system 
    with open(dict_path, 'r') as file:
        mapping_df = csv.reader(file)
        mapping_dict = {}
        # Import all indices if N_tokens is not given
        for line in mapping_df:
            k, v = line
            mapping_dict[k] = v


    return mapping_dict

# Function that can convert a string of words
def convert_string_AE2BE(string, AE_to_BE):
    

    """convert a text from American English to British English

    Parameters
    ----------
    string: str
        text to convert

    Returns
    -------
    str
        new text in British English
    """

    string_new = " ".join([AE_to_BE[w] if w in AE_to_BE.keys() else w for w in string.split()])

    return string_new

# Function that can convert verbs in the MainVerb column from American English to British English
def convert_word_AE2BE(word, AE_to_BE):

    """convert a word from American English to British English

    Parameters
    ----------
    word: str
        word to convert

    Returns
    -------
    str
        new word in British English
    """

    try:
        if word in AE_to_BE.keys():
            return AE_to_BE[word]
        else:
            return word
    except:
        return word

def convert_sens(TENSES_ONE_SENT_PER_VERB_WITH_MODALS, AE2BE_LIST, INFINITIVE_CORR_LIST):
    # Load the data
    tenses = pd.read_csv(TENSES_ONE_SENT_PER_VERB_WITH_MODALS, encoding="utf-8")
    # Load the dictionary that can convert AE to BE
    AE_to_BE = import_dict(dict_path = AE2BE_LIST)

    # Load the dictionary that Laurence prepared to convert AE to BE
    inf_corrections = import_dict(dict_path = INFINITIVE_CORR_LIST)

    # Correct the infinitives in the dataframe
    tenses["Infinitive_BE"] = tenses["Infinitive"].apply(lambda s: correct_infinitive(inf_corrections, s))

    #############################################
    # Convert the infinitves to British English
    #############################################

    # Convert the verbforms in the dataframe
    tenses["Infinitive_BE"] = tenses["Infinitive_BE"].apply(lambda s: convert_word_AE2BE(s, AE_to_BE))
    # Convert the sentences in the dataframe
    tenses["Sentence_BE"] = tenses["Sentence"].apply(lambda s: convert_string_AE2BE(s, AE_to_BE))

    # Convert the verbforms in the dataframe
    tenses["VerbForm_BE"] = tenses["VerbForm"].apply(lambda s: convert_word_AE2BE(s, AE_to_BE))

    # Convert the verbforms in the dataframe
    tenses["MainVerb_BE"] = tenses["MainVerb"].apply(lambda s: convert_word_AE2BE(s, AE_to_BE))

    # Remove the unnecessary columns
    tenses.drop(columns = ["Sentence", "VerbForm", "MainVerb", "Infinitive"], inplace = True)

    # Rename some columnns columns
    tenses.rename(columns = {"Sentence_BE": "Sentence", 
                            "VerbForm_BE": "VerbForm", 
                            "MainVerb_BE": "MainVerb",
                            "Infinitive_BE": "Infinitive"}, inplace = True)
    # Reorder the columns
    tenses = tenses[['SentenceID', 
            'Sentence', 
            'SentenceLength', 
            'NumOfVerbs', 
            'Tense', 
            'VerbForm', 
            'MainVerb',
            'Position',    
            'Infinitive']]
    return(tenses)

########################################################################
# Correct the infinitives using Laurence list
########################################################################

# Function that correct the infinitives using Laurence's list
def correct_infinitive(inf_corrections, verb):

    """Correct the infinitives using Laurence's list

    Parameters
    ----------
    verb: str
        verb to correct

    Returns
    -------
    str
        corrected infinitive
    """

    try:
        if verb in inf_corrections.keys() and inf_corrections[verb] != "":
            return inf_corrections[verb]
        else:
            return verb
    except:
        return verb



########################################################
# Creating context with infinitive out of each sentence
########################################################
                                                                                                                
### Function that create context with infinitive replacing the verb form. 
#def extract_context(sent, verb_form, pos, inf):
def extract_context(row):
    ''' Add a description
    '''
    sent = row.loc['Sentence']
    verb_form = row.loc['VerbForm']
    pos = row.loc['Position']
    inf = row.loc['Infinitive']

    # Create list of words that makes up the verb form
    words_to_remove = verb_form.split(" ") 
    num_to_remove = len(words_to_remove)

    # Remove the words from the sentence
    sent_list = sent.split(" ")
    context_list = []
    for i, w in enumerate(sent_list):
        if (w in words_to_remove) and (i>pos-num_to_remove-4) and (i<pos-1):
            continue
        elif (i == (pos-1)):
            context_list.append(inf.upper())
        else:
            context_list.append(w)

    # Remove the extra spaces
    context = " ".join(context_list)
    # Return the context
    return context 


###########################################################
# Creating context without infinitive out of each sentence
###########################################################

### Function that create context without infinitive. It removes the verb form from a sentence
def remove_verb_form(row):
    sent = row.loc['Sentence']
    verb_form = row.loc['VerbForm'] 
    pos = row.loc['Position']
    ''' Add a description
    '''
    # Create list of words that makes up the verb form
    words_to_remove = verb_form.split(" ") 
    num_to_remove = len(words_to_remove)

    # Remove the words from the sentence
    sent_list = sent.split(" ")
    context_list = []
    for i, w in enumerate(sent_list):
        if (w in words_to_remove) and (i>pos-num_to_remove-4) and (i<pos):
            continue
        else:
            context_list.append(w)

    # Remove the extra spaces
    context = " ".join(context_list)

    # Return the context
    return context 



#######################
# Creating n-gram cues
#######################

def create_ngram_cues(s, n, sep_s = " ", sep_words = "#", sep_ngrams = '_'):
    """Generate ngram cues from a string of cues. 
    
    Arguments:
        s {str} -- string of cues to generate the ngrams for. 
                   To process a sentence, use sep_s = " "
        n {int} -- ngram size
    
    Keyword Arguments:
        sep_s {str} -- symbole used to seperate the words in the string of cues (default: {'_'})
        sep_words {str} -- symbole used to seperate the words in a single ngram (default: {"#"})
        sep_ngrams {str} -- symbole used to seperate the ngrams (default: {'_'})
    
    Returns:
        str -- ngrams seperated using sep_ngrams
    """

    words = [w for w in s.split(sep_s) if w != ""]

    s_ngrams = []
    for i in range(1,n+1):
        s_ngrams.extend(list(ngrams(words, i)))

    return sep_ngrams.join([sep_words.join(ngram) for ngram in s_ngrams])



################################################################
# Add information about the order of each verb within a sentence 
#################################################################
def add_info(tenses, TENSES_ONE_VERB_READY_GZ):
    #print(f'Number of examples: {len(tenses)}')
    # Number of examples: 7047168

    ### Tests on a small sample of 10k sentences
    SentID_list = list(tenses["SentenceID"].unique())
    tenses = tenses[tenses['SentenceID'].isin(SentID_list)]

    # Create a column to encode the order of the verb relative to the other verbs and move it after the 'NumOfVerbs' column 
    tenses['VerbOrder'] = tenses.groupby('SentenceID').cumcount()
    tenses['VerbOrder'] =  tenses['VerbOrder'] + 1

    # Change the order of the column 'VerbOrder'
    cols = list(tenses.columns)
    cols.insert(5, cols.pop(cols.index('VerbOrder')))
    tenses = tenses.loc[:, cols]

    ##################################################
    # Extract sentences with one verb only 
    ##################################################

    ### Data set containing only sentences with one verb
    tenses1 = tenses[tenses.NumOfVerbs == 1]

    tenses1['Tense'].value_counts()

    # Export the dataset
    tenses1.to_csv(TENSES_ONE_VERB_READY_GZ, compression='gzip', index = False, encoding="utf-8")

#############################################################
# Shuffle the sentences while keeping the order of the events 
#############################################################
def shuffle_sents(tenses, TENSES_ONE_SENT_PER_VERB_SHUF_GZ):
    # Create a counter of sent ids
    SentID_list = list(tenses["SentenceID"])
    count_sentid = Counter()
    for id in SentID_list:
        count_sentid[id] += 1

    # Shuffle the keys of the counter
    count_keys =  list(count_sentid.keys())
    random.Random(1).shuffle(count_keys)
    count_sentid_semidict = [(k, count_sentid[k]) for k in count_keys]

    SentID_list_shuf = []
    for (k,v) in count_sentid_semidict:
        SentID_list_shuf.extend([k]*v)

    # Convert the shuffled list into a dataframe 
    SentID_df = pd.DataFrame({'SentenceID': SentID_list_shuf})

    # Add the column VerbOrder
    SentID_df['VerbOrder'] = SentID_df.groupby('SentenceID').cumcount()
    SentID_df['VerbOrder'] = SentID_df['VerbOrder'] + 1

    # Change the order of SentID by merging tenses and SentID_df
    tenses = SentID_df.merge(tenses)

    # Export the dataset
    tenses.to_csv("%s.csv.gz"%(TENSES_ONE_SENT_PER_VERB_SHUF_GZ), compression='gzip', index = False, encoding="utf-8")

def remove_modals(tenses, TENSES_ONE_SENT_PER_VERB):
        #######################################################################
    # Remove modals and imperatives from the dataset with one verb per row
    #######################################################################

    # Number of modals without information about VerbForm, Infinitive or position since they appear at the end of their sentences
    len(tenses[tenses['Position'].isnull()]) # => 16187

    # Remove them
    tenses = tenses[~tenses['Position'].isnull()]
    tenses['Tense'].value_counts()
    # present.simple       3201494
    # past.simple          2639252
    # modal                 900459
    # present.perf          370457
    # future.simple         257377
    # past.perf             253239
    # present.prog          180522
    # past.prog             115705
    # imperative             84294
    # present.perf.prog      11319
    # future.prog             7832
    # past.perf.prog          7038
    # future.perf             2954
    # future.perf.prog          30

    pd.set_option('display.width', 150)
    pd.set_option('display.max_columns', 9)
    #    SentenceID                                                                                              Sentence  SentenceLength  NumOfVerbs  \
    # 0           1                                                                                factsheet what is aids               4         1.0   
    # 1           2  immune deficiency syndrome is a condition caused by a virus called hiv human immuno deficiency virus              16         1.0   
    # 2           3                         this virus affects the body defence system so that it can not fight infection              14         2.0   

    #             Tense   VerbForm MainVerb  Position Infinitive  
    # 0  present.simple         is       is       3.0         be  
    # 1  present.simple  is caused   caused       7.0      cause  
    # 2  present.simple    affects  affects       3.0     affect 

    # Remove the modals and imperatives
    tenses = tenses[~tenses['Tense'].isin(['modal', 'imperative'])]
    #print(tenses['Tense'].value_counts())
    # present.simple       3201494
    # past.simple          2639252
    # present.perf          370457
    # future.simple         257377
    # past.perf             253239
    # present.prog          180522
    # past.prog             115705
    # present.perf.prog      11319
    # future.prog             7832
    # past.perf.prog          7038
    # future.perf             2954
    # future.perf.prog          30

    # Export the dataset
    tenses.to_csv(TENSES_ONE_SENT_PER_VERB, index = False, encoding="utf-8")

    ### Add ContextWithInfinitive column
    tenses["ContextWithInfinitive"] = tenses.apply(lambda x: extract_context(x), axis=1)

    ### Add ContextNoInfinitive column
    tenses["ContextNoInfinitive"] = tenses.apply(lambda x: remove_verb_form(x), axis=1)
    # Export the dataset
    tenses.to_csv(TENSES_ONE_SENT_PER_VERB, index = False, encoding="utf-8")

def run(TENSES, PREPDAT_FILES):
    TENSES_WITH_INF, TENSES_WITH_INF_NEW, TENSES_ONE_SENT_PER_VERB, = PREPDAT_FILES[0], PREPDAT_FILES[1], PREPDAT_FILES[2] 
    TENSES_ONE_SENT_PER_VERB_WITH_MODALS, TENSES_ONE_SENT_PER_VERB_READY_GZ = PREPDAT_FILES[3], PREPDAT_FILES[4]
    TENSES_ONE_SENT_PER_VERB_SHUF_GZ, TENSES_ONE_VERB, TENSES_ONE_VERB_READY_GZ = PREPDAT_FILES[5], PREPDAT_FILES[6], PREPDAT_FILES[7]
    TENSES_ONE_VERB_SHUF_GZ, AE2BE_LIST, INFINITIVE_CORR_LIST = PREPDAT_FILES[8], PREPDAT_FILES[9], PREPDAT_FILES[10]
    #tenses = pd.read_csv(TENSES, keep_default_na = False, encoding="utf-8")
    #print(tenses)
    convert_to_inf("%s.csv"%(TENSES), TENSES_WITH_INF)
    add_sen_length(TENSES_WITH_INF, TENSES_WITH_INF_NEW)
    remove_sen(TENSES_WITH_INF_NEW, TENSES_ONE_SENT_PER_VERB_WITH_MODALS)
    tenses = convert_sens(TENSES_ONE_SENT_PER_VERB_WITH_MODALS, AE2BE_LIST, INFINITIVE_CORR_LIST)
    remove_modals(tenses, TENSES_ONE_SENT_PER_VERB)

    ######################
    # Creating word cues
    ######################

    # Load the data
    tenses = pd.read_csv(TENSES_ONE_SENT_PER_VERB, keep_default_na = False, encoding="utf-8")

    # Remove sentences with only the verb (no context)
    tenses = tenses[~tenses["ContextNoInfinitive"].isin([""])]

    # Add word cues without infinitives
    tenses["WordCuesNoInfinitive"] = tenses["ContextNoInfinitive"].apply(lambda s: "_".join(s.split(" ")))

    # Add word cues with infinitives
    tenses["WordCuesWithInfinitive"] = tenses["ContextWithInfinitive"].apply(lambda s: "_".join(s.split(" ")))

    # Remove the context columns
    tenses.drop(columns = ['ContextNoInfinitive', 'ContextWithInfinitive'], inplace = True)

    # Export the dataset
    tenses.to_csv(TENSES_ONE_SENT_PER_VERB, index = False, encoding="utf-8")

    # Add n-gram cues without infinitives
    tenses["NgramCuesNoInfinitive"] = tenses["WordCuesNoInfinitive"].apply(lambda s: create_ngram_cues(s, n = 4, sep_s = "_"))

    # Add n-gram cues with infinitives
    tenses["NgramCuesWithInfinitive"] = tenses.apply(lambda x: "_".join([x.loc["NgramCuesNoInfinitive"],
                                                                        x.loc["Infinitive"].upper()]), axis = 1)

    # Export the dataset
    tenses.to_csv(TENSES_ONE_SENT_PER_VERB_READY_GZ, compression='gzip', index = False, encoding="utf-8")

    ###########################################################################
    # Add new NumOfVerbs that doesn't take into account modals and imperatives 
    ###########################################################################

    add_info(tenses, TENSES_ONE_VERB_READY_GZ)
    shuffle_sents(tenses, TENSES_ONE_SENT_PER_VERB_SHUF_GZ)

    ### Load the data
    start = time.time()
    tenses = pd.read_csv(TENSES_ONE_SENT_PER_VERB_READY_GZ, compression='gzip', encoding="utf-8")
    _ = sys.stdout.write('Loading the data took %ds' %((time.time()-start)))

    #print(f'Number of examples: {len(tenses)}')
    # Number of examples: 7047168

    tenses.columns

    ### Rename the column of original num of verbs
    tenses.rename(columns = {'NumOfVerbs': 'NumOfVerbsOriginal'}, inplace = True)

    tenses['NumOfVerbs'] = tenses.groupby(['SentenceID'])['Sentence'].transform('count')
    cols = list(tenses.columns)
    cols.insert(3,cols.pop(cols.index('NumOfVerbs')))
    tenses = tenses.loc[:, cols]
    ##################################################
    # Extract sentences with one verb only (shuffeled)
    ##################################################

    ### Data set containing only sentences with one verb
    tenses1 = tenses[tenses.NumOfVerbs == 1]

    #print(tenses1['Tense'].value_counts())

    # Export the dataset
    tenses1.to_csv(TENSES_ONE_VERB_SHUF_GZ, compression='gzip', index = False, encoding="utf-8")
