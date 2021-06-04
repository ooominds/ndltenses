####################
# Preliminary steps
####################

### Import necessary packages
import os
import time
import sys
import csv
import gc
import pandas as pd
from nltk.util import ngrams
import gzip 
from pyndl.count import cues_outcomes

### Set working directory
TOP = "/rds/projects/d/divjakd-ooo-machines/Users/tekevwe/English_tense/Data_preparation/"
#TOP = '/media/adnane/HDD drive/Adnane/PostDoc_ooominds/Programming/English_Tense/Work_in_Birmingham/Data_preparation/'
WD = TOP + 'Step5_Prepare_ngrams_for_training/'
os.chdir(WD)

### Set the max width of a column
pd.set_option('display.max_colwidth', 120)

### Define file paths
TENSES_GZ = TOP + "Data_shared/tenses_annotated_one_sent_per_verb_shuffeled.csv.gz"
NGRAM1 = WD + "Data/multi_verbs/1grams.csv"
NGRAM2 = WD + "Data/multi_verbs/2grams.csv"
NGRAM3 = WD + "Data/multi_verbs/3grams.csv"
NGRAM4 = WD + "Data/multi_verbs/4grams.csv"
NGRAM = WD + "Data/multi_verbs/ngrams.csv"
TEMP_DIR = WD + "Data"

### Parameters to use
NUM_THREADS = 4

###################
# Useful functions
###################

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
    s_ngrams = ngrams(words, n)

    return sep_ngrams.join([sep_words.join(ngram) for ngram in s_ngrams])

def create_ngram_event_df_file(df, n, sep_words = "#"):
    """[summary]
    
    Arguments:
        df {dataframe} -- event file as a dataframe. It should have two columns: one for the cues
                          and one for the outcomes
        n {int} -- ngram size
    
    Keyword Arguments:
        sep_words {str} -- symbole used to seperate the words in a single ngram (default: {"#"})
    
    Returns:
        [dataframe] -- new event file with ngrams as cues 
    """
    
    df_new = df.copy()
    df_new['cues'] = df_new['cues'].apply(lambda s: create_ngram_cues(s, n = n, sep_s = "_"))

    return df_new

def df_to_gz(data, gz_outfile):

    """Export a dataframe containing events to a .gz file

    Parameters
    ----------
    data: dataframe
        dataframe to export to a gz file
    gz_outfile: str
        path of the gz file  

    Returns
    -------
    None 
        save a .gz file
    """

    with gzip.open(gz_outfile, 'wt', encoding='utf-8') as out:
        data.to_csv(out, sep = '\t', index = False)

def compute_cue_freqs(data, temp_dir, num_threads, verbose = False):

    """Compute cue frequencies. 
    
    Arguments:
        data {str} -- dataframe or path to the .gz file containing the events
        temp_dir {str} -- directory where to store temporary event file. 
                          Required only if data is a dataframe
    
    Returns:
        dataframe -- dataframe storing the cue frequencies
    """

    ### Path to the event file
    if isinstance(data, str):     
        events_path = data
    elif isinstance(data, pd.DataFrame):
        events_path = os.path.join(temp_dir, 'events_multi_temp.gz')
        df_to_gz(data = data, gz_outfile = events_path)
    else:
        raise ValueError("data should be either a path to an event file or a dataframe")

    ### Count ngrams in events
    n_events, cue_freqs, outcome_freqs = cues_outcomes(events_path,
                                                       number_of_processes = num_threads,
                                                       verbose = verbose)

    ### Create a dataframe that contains all the co-occurrence freqs
    cue_freqs_df = pd.DataFrame(cue_freqs.most_common())
    cue_freqs_df.columns = ['ngram', 'frequency']
    #cue_freqs_df = cue_freqs_df.fillna(0)
    #del cue_freqs_df.columns.name
    #del cue_freqs_df.index.name

    # Remove the row corresponding to the empty n-gram
    cue_freqs_df = cue_freqs_df[cue_freqs_df.ngram != '']

    # Garbage collection
    gc.collect()

    return cue_freqs_df

####################
# Data preparation
####################
def extract_ngrams(TENSES_GZ,NGRAM,NGRAM1,NGRAM2,NGRAM3,NGRAM4,TEMP_DIR, NUM_THREADS):
    ### Load the data
    start = time.time()
    tenses_full = pd.read_csv(TENSES_GZ, compression='gzip', usecols = ['WordCuesNoInfinitive', 'Tense'])
    _ = sys.stdout.write('Loading the data took %ds' %((time.time()-start)))
    print(f'Number of examples: {len(tenses_full)}')
    # Number of examples: 7047168

    ### Keep only the cues and outcomes then rename columns 
    tenses_full = tenses_full.rename(columns={"WordCuesNoInfinitive": "cues", "Tense": "outcomes"}) 
    tenses_full = tenses_full[["cues", "outcomes"]]  

    #################################
    # Compute the n-gram frequencies
    #################################

    ######## Calculate the frequency of co-occurence between each 1-gram and tense #############
    tenses_1gram = create_ngram_event_df_file(tenses_full, 1, sep_words = "#")
    ngram_freqs1 = compute_cue_freqs(tenses_1gram, TEMP_DIR, num_threads = 4, verbose = True) 
    ngram_freqs1.shape # (286911, 2)
    ngram_freqs1.head() 
    #   ngram  frequency
    # 0   the    9419620
    # 1    of    4482465
    # 2   and    4278936
    # 3    to    4267642
    # 4     a    3445382

    ### Number of n-grams that appear at least 10 times
    len(ngram_freqs1[ngram_freqs1['frequency']>=10]) # 103915

    ### Export the co-occurence dataset
    ngram_freqs1.to_csv(NGRAM1, sep = ',', index = False)
    del ngram_freqs1, tenses_1gram

    ######## Calculate the frequency of co-occurence between each 2-gram and tense #############
    tenses_2grams = create_ngram_event_df_file(tenses_full, 2, sep_words = "#")
    ngram_freqs2 = compute_cue_freqs(tenses_2grams, TEMP_DIR, num_threads = 4, verbose = True) 
    ngram_freqs2.shape # (9444152, 2)
    ngram_freqs2.head() 
    #     ngram  frequency
    # 0  of#the    1124747
    # 1  in#the     800043
    # 2  to#the     452096
    # 3   it#is     349753
    # 4  on#the     338707

    ### Number of n-grams that appear at least 10 times
    len(ngram_freqs2[ngram_freqs2['frequency']>=10]) # 1103795

    ### Export the co-occurence dataset
    ngram_freqs2.to_csv(NGRAM2, sep = ',', index = False)
    del ngram_freqs2, tenses_2grams

    ######## Calculate the frequency of co-occurence between each 3-gram and tense #############
    tenses_3grams = create_ngram_event_df_file(tenses_full, 3, sep_words = "#")
    ngram_freqs3 = compute_cue_freqs(tenses_3grams, TEMP_DIR, num_threads = 4, verbose = True) 
    ngram_freqs3.shape # (33851071, 2)
    ngram_freqs3.head() 
    #         ngram  frequency
    # 1    i#do#not      58839
    # 2  one#of#the      58365
    # 3  the#end#of      32642
    # 4   it#is#not      32553
    # 5     it#is#a      31347

    ### Number of n-grams that appear at least 10 times
    len(ngram_freqs3[ngram_freqs3['frequency']>=10]) # 1458210

    ### Export the co-occurence dataset
    ngram_freqs3.to_csv(NGRAM3, sep = ',', index = False)
    del ngram_freqs3, tenses_3grams

    ######## Calculate the frequency of co-occurence between each 4-gram and tense #############

    ### Create event file in dataframe format
    tenses_4grams = create_ngram_event_df_file(tenses_full, 4, sep_words = "#")

    # Convert to gz file
    EVENT_FILE = WD + "Data/multi_verbs/events_4grams.gz"
    df_to_gz(tenses_4grams, EVENT_FILE)
    del tenses_4grams

    # Count ngrams in events
    start = time.time()
    n_events, cue_freqs, outcome_freqs = cues_outcomes(EVENT_FILE,
                                                    number_of_processes = 1,
                                                    verbose = True)
    sys.stdout.write('Frequency counts completed in %.3fs\n' % ((time.time()- start)))  

    # save cue frequencies to file
    with open(NGRAM4, mode = 'w') as o:
        csv_writer = csv.writer(o, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        heading = ['ngram', 'frequency']
        _ = csv_writer.writerow(heading)
        for cue, frequency in cue_freqs.most_common():
            _ = csv_writer.writerow([cue, frequency])
            o.flush()


