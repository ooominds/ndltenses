#!/usr/bin/python3

####################
# Preliminary steps
####################

### Import necessary packages
import numpy as np
import pandas as pd

def run(NGRAMS, INFINITIVES, ALL_CUES):

    #################
    # Load the data 
    #################

    ### Load the list of n-grams
    ngram_df = pd.read_csv(NGRAMS)
    # Remove the freq column
    ngram_df.drop(columns = ['frequency'], inplace = True)

    ### Load the list of infinitives
    infinitives_df = pd.read_csv(INFINITIVES, header = None, names = ["infinitive"])
    infinitives_df['infinitive'] = infinitives_df['infinitive'].apply(lambda s: s.upper())

    ### Rename columns
    ngram_df.rename(columns = {'ngram': 'cue'}, inplace = True)
    infinitives_df.rename(columns = {'infinitive': 'cue'}, inplace = True)

    ### Append all cues
    all_cues_df = ngram_df.copy()
    all_cues_df = all_cues_df.append([infinitives_df.copy()])
    # # Remove infinitives that already exist in the list of 1-grams
    # all_cues_df.drop_duplicates(subset = "cue", keep = 'first', inplace = True) 
    all_cues_df['index'] = np.arange(1, (len(all_cues_df)+1))

    # Save a separate dataframe for each group
    all_cues_df.to_csv("%s.csv"%(ALL_CUES), sep = ',', index = False, header=False)
