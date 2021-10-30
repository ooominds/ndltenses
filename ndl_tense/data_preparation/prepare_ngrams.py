#!/usr/bin/python3

####################
# Preliminary steps
####################

### Import necessary packages
import pandas as pd
#import logging
#logger = logging.getLogger("data_preparation")
#logger.setLevel(level=logging.INFO)

### Set working directory

def run(NGRAM_FILES, K_NGRAMS, TARGETS_FILES, VERBOSE):

    FREQ_1G_PATH = NGRAM_FILES[1]
    FREQ_2G_PATH = NGRAM_FILES[2]
    FREQ_3G_PATH = NGRAM_FILES[3]
    FREQ_4G_PATH = NGRAM_FILES[4]

    TARGETS = "{}.csv".format(TARGETS_FILES[0])
    TARGETS_1G = "{}.csv".format(TARGETS_FILES[1])
    TARGETS_2G = "{}.csv".format(TARGETS_FILES[2])
    TARGETS_3G = "{}.csv".format(TARGETS_FILES[3])
    TARGETS_4G = "{}.csv".format(TARGETS_FILES[4])
    
    #################################################################
    # Load the frequency files as dictionaries prior to band-sampling
    #################################################################

    ########## 1-grams ##########
    # Load as dataframe and retain only 10k ngrams whose freq >= 10
    Freq_1G_df = pd.read_csv("{}.csv".format(FREQ_1G_PATH))
    Freq_1G_df.dropna(inplace = True) # Remove the row corresponding to the empty n-gram
    Freq_1G_df = Freq_1G_df[Freq_1G_df['frequency']>=10] # Remove ngrams whose freq < 10
    Freq_1G_df = Freq_1G_df.sample(frac=1) # Shuffle ngrams with the same frequency
    Freq_1G_df = Freq_1G_df.sort_values(by = ['frequency'], ascending = False).reset_index(drop=True) # Sort in a descending order by the frequency
    Freq_1G_df = Freq_1G_df.iloc[0:K_NGRAMS] # Extract N ngrams 

    ########## 2-grams ##########
    # Load as dataframe and retain only 10k ngrams whose freq >= 10
    Freq_2G_df = pd.read_csv("{}.csv".format(FREQ_2G_PATH))
    Freq_2G_df.dropna(inplace = True) # Remove the row corresponding to the empty n-gram
    Freq_2G_df = Freq_2G_df[Freq_2G_df['frequency']>=10] # Remove ngrams whose freq < 10
    Freq_2G_df = Freq_2G_df.sample(frac=1) # Shuffle ngrams with the same frequency
    Freq_2G_df = Freq_2G_df.sort_values(by = ['frequency'], ascending = False).reset_index(drop=True) # Sort in a descending order by the frequency
    Freq_2G_df = Freq_2G_df.iloc[0:K_NGRAMS] # Extract N ngrams 

    ########## 3-grams ##########
    # Load as dataframe and retain only 10k ngrams whose freq >= 10
    Freq_3G_df = pd.read_csv("{}.csv".format(FREQ_3G_PATH))
    Freq_3G_df.dropna(inplace = True) # Remove the row corresponding to the empty n-gram
    Freq_3G_df = Freq_3G_df[Freq_3G_df['frequency']>=10] # Remove ngrams whose freq < 10
    Freq_3G_df = Freq_3G_df.sample(frac=1) # Shuffle ngrams with the same frequency
    Freq_3G_df = Freq_3G_df.sort_values(by = ['frequency'], ascending = False).reset_index(drop=True) # Sort in a descending order by the frequency
    Freq_3G_df = Freq_3G_df.iloc[0:K_NGRAMS] # Extract N ngrams 


    ########## 4-grams ##########
    # Load as dataframe and retain only 10k ngrams whose freq >= 10
    Freq_4G_df = pd.read_csv("{}.csv".format(FREQ_4G_PATH))
    Freq_4G_df.dropna(inplace = True) # Remove the row corresponding to the empty n-gram
    Freq_4G_df = Freq_4G_df[Freq_4G_df['frequency']>=10] # Remove ngrams whose freq < 10
    Freq_4G_df = Freq_4G_df.sample(frac=1) # Shuffle ngrams with the same frequency
    Freq_4G_df = Freq_4G_df.sort_values(by = ['frequency'], ascending = False).reset_index(drop=True) # Sort in a descending order by the frequency
    Freq_4G_df = Freq_4G_df.iloc[0:K_NGRAMS] # Extract N ngrams 

    ########## All n-grams ##########
    # Append all datasets
    Freq_all_df = Freq_1G_df.copy()
    Freq_all_df = Freq_all_df.append([Freq_2G_df.copy(), Freq_3G_df.copy(), Freq_4G_df.copy()])

    # Save a separate dataframe for each group
    Freq_1G_df.to_csv("{}.csv".format(TARGETS_1G), sep = ',', index = False)
    Freq_2G_df.to_csv("{}.csv".format(TARGETS_2G), sep = ',', index = False)
    Freq_3G_df.to_csv("{}.csv".format(TARGETS_3G), sep = ',', index = False)
    Freq_4G_df.to_csv("{}.csv".format(TARGETS_4G), sep = ',', index = False)
    Freq_all_df.to_csv("{}.csv".format(TARGETS), sep = ',', index = False)
    if VERBOSE:
        print("STEP 5: Preparing ngrams is complete\n")
