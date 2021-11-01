####################
# Preliminary steps
####################

### Import necessary packages
import os
import time
import logging
import csv
import gc
import pandas as pd
from nltk.util import ngrams
from pyndl.count import cues_outcomes

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)

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

def create_ngram_event_df_file(df, n):
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
    data.to_csv(gz_outfile, sep = '\t', index = False)

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
        events_path = os.path.join(temp_dir, 'events_multi_temp.csv.gz')
        df_to_gz(data = data, gz_outfile = events_path)
    else:
        raise ValueError("data should be either a path to an event file or a dataframe")
    
    ### Count ngrams in events
    n_events, cue_freqs, outcome_freqs = cues_outcomes(events_path, number_of_processes = num_threads, verbose = verbose)

    ### Create a dataframe that contains all the co-occurrence freqs
    cue_freqs_df = pd.DataFrame(cue_freqs.most_common())
    cue_freqs_df.columns = ['ngram', 'frequency']

    # Remove the row corresponding to the empty n-gram
    cue_freqs_df = cue_freqs_df[cue_freqs_df.ngram != '']

    # Garbage collection
    gc.collect()
    return cue_freqs_df

####################
# Data preparation
####################
def run(TENSES_GZ, NGRAM_FILES, TEMP_DIR, NUM_THREADS):

    NGRAM1 = NGRAM_FILES[1]
    NGRAM2 = NGRAM_FILES[2]
    NGRAM3 = NGRAM_FILES[3]
    NGRAM4 = NGRAM_FILES[4]
    EVENT_FILE = "{}.gz".format(NGRAM_FILES[5])

    ### Load the data
    start = time.time()
    tenses_full = pd.read_csv("{}.csv.gz".format(TENSES_GZ), compression='gzip', usecols = ['WordCuesNoInfinitive', 'Tense'])
    logger.info('Loading the data took {}s'.format((time.time()-start)))

    ### Keep only the cues and outcomes then rename columns 
    tenses_full = tenses_full.rename(columns={"WordCuesNoInfinitive": "cues", "Tense": "outcomes"}) 
    tenses_full = tenses_full[["cues", "outcomes"]]  

    #################################
    # Compute the n-gram frequencies
    #################################

    ######## Calculate the frequency of co-occurence between each 1-gram and tense #############
    tenses_1gram = create_ngram_event_df_file(tenses_full, 1)
    ngram_freqs1 = compute_cue_freqs(tenses_1gram, TEMP_DIR, NUM_THREADS, True) 
    ngram_freqs1.shape 
    ngram_freqs1.head() 

    ### Number of n-grams that appear at least 10 times
    len(ngram_freqs1[ngram_freqs1['frequency']>=10]) # 103915

    ### Export the co-occurence dataset
    ngram_freqs1.to_csv("{}.csv".format(NGRAM1), sep = ',', index = False)
    del ngram_freqs1, tenses_1gram

    ######## Calculate the frequency of co-occurence between each 2-gram and tense #############
    tenses_2grams = create_ngram_event_df_file(tenses_full, 2)
    ngram_freqs2 = compute_cue_freqs(tenses_2grams, TEMP_DIR, NUM_THREADS, True) 
    ngram_freqs2.shape
    ngram_freqs2.head() 

    ### Number of n-grams that appear at least 10 times
    len(ngram_freqs2[ngram_freqs2['frequency']>=10]) # 1103795

    ### Export the co-occurence dataset
    ngram_freqs2.to_csv("{}.csv".format(NGRAM2), sep = ',', index = False)
    del ngram_freqs2, tenses_2grams

    ######## Calculate the frequency of co-occurence between each 3-gram and tense #############
    tenses_3grams = create_ngram_event_df_file(tenses_full, 3)
    ngram_freqs3 = compute_cue_freqs(tenses_3grams, TEMP_DIR, NUM_THREADS, True) 
    ngram_freqs3.shape 
    ngram_freqs3.head() 

    ### Number of n-grams that appear at least 10 times
    len(ngram_freqs3[ngram_freqs3['frequency']>=10]) # 1458210

    ### Export the co-occurence dataset
    ngram_freqs3.to_csv("{}.csv".format(NGRAM3), sep = ',', index = False)
    del ngram_freqs3, tenses_3grams

    ######## Calculate the frequency of co-occurence between each 4-gram and tense #############

    ### Create event file in dataframe format
    tenses_4grams = create_ngram_event_df_file(tenses_full, 4)

    # Convert to gz file
    df_to_gz(tenses_4grams, EVENT_FILE)
    del tenses_4grams

    # Count ngrams in events
    start = time.time()
    n_events, cue_freqs, outcome_freqs = cues_outcomes(EVENT_FILE,
                                                    number_of_processes = 1,
                                                    verbose = True)
    logger.info('Frequency counts completed in {}s\n'.format((time.time()- start)))  

    # save cue frequencies to file
    with open("%s.csv"%(NGRAM4), mode = 'w') as o:
        csv_writer = csv.writer(o, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        heading = ['ngram', 'frequency']
        _ = csv_writer.writerow(heading)
        for cue, frequency in cue_freqs.most_common():
            _ = csv_writer.writerow([cue, frequency])
            o.flush()


