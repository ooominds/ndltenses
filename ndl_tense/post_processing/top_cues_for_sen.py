from enum import unique
import pandas as pd
import numpy as np
from ndl_tense.post_processing import sample_sentences


def unique_cues(sample_df,keys):
    """
        Create a dummy weight matrix for different cues
    -----
    PARAMETERS
    -----
        sample_df: pandas DataFrame
            Dataframe produced by TENSES_FILE, used to get cues
        keys: list
            A list of keys (tense/aspect pairs) to be the columns of this dummy table
    -----
    RETURN
    -----
        cues_df: pandas DataFrame
            a dataframe with cues as indexes and keys (tense/aspect pairs) as columns and random weights as cell entries
    """
    unique_cues_set = set()
    cues = sample_df.columns.get_loc('NgramCuesWithInfinitive')
    for row in range(sample_df.shape[0]):
        # to avoid repeated cues, use sets
        unique_cues_set = unique_cues_set.union(sample_df.iloc[row, cues].split('_'))
    # random weights
    dummy_data = np.random.rand(len(unique_cues_set), len(keys))
    cues_df = pd.DataFrame(dummy_data, index = list(unique_cues_set), columns =keys)
    cues_df.to_csv("cue_weights.csv")
    return(cues_df)


# Find the top n cues and their associated weights
def find_top_n_cues(cues, ta, cue_weights, n_cues):
    wanted_cues_subset = cue_weights.loc[cues]
    top_cues = wanted_cues_subset.nlargest(n_cues, ta)
    return(list(top_cues.index), list(top_cues[ta]))
    

def run(TENSES_FILE, CUE_WEIGHT_FILE, save_path, ratios, n_cues, sample_size):
    """
        create an excel file using data of the learned weights of an NDL model with a sample of the sentences it was trained on:
        SentenceID, Sentence, TA, StrongestCues, StrongCue1_Strength, ...StrongCueN_Strength
    -----
    PARAMETERS
    -----
        TENSES_FILE: str
            this is by default the tenses_annotated_one_sent_per_verb_shuffeled.csv file (it is zipped)
        CUE_WEIGHT_FILE:
            this is a file created after the model is trained and after some post-processing,
            not ready to be added to the package
        save_path: str
            where to save the excel file to be created
        ratios: list
            wanted ratio of keys
        n_cues: int
            n strongest cues
        sample_size: int
            size of the sample
    -----
    RETURN
    -----
        Creates an excel file.
    """
    #cue_weights = pd.read_csv("%s.csv"%(CUE_WEIGHT_FILE))
    
    keys = ["present.simple",
            "past.simple",
            "present.perf",
            "future.simple"]
    
    sample_sentences_df = sample_sentences.run("%s.csv"%(TENSES_FILE), keys, ratios, sample_size, False)
    print(sample_sentences_df.columns)
    sample_sentences_df.sort_values(by = "SentenceID", inplace=True)

    cue_weights = unique_cues(sample_sentences_df, keys)
    top_n_cues_list, top_n_cue_strengths_list = [], []
    
    # getting index (an integer represnetation) of wanted columns
    cues_index = sample_sentences_df.columns.get_loc('NgramCuesWithInfinitive')
    ta_index = sample_sentences_df.columns.get_loc('Tense')
    
    for row in range(sample_sentences_df.shape[0]):
        ta = sample_sentences_df.iloc[row, ta_index]
        cues = sample_sentences_df.iloc[row, cues_index].split('_')
        
        #print("sentence: " + str(sample_sentences_df.iloc[row,2]) + "\n")
        #print("cues in table: " + str(sample_sentences_df.iloc[row, cues_index]) + "\n")
        #print("cues created: " + str(cues) + "\n")

        top_n_cues, top_n_cue_strengths = (find_top_n_cues(cues, ta, cue_weights, n_cues))

        #print("top N cues: " + str(top_n_cues) + "\n")
        top_n_cues_list.append(top_n_cues)
        top_n_cue_strengths_list.append(top_n_cue_strengths)
    
    new_df = sample_sentences_df[["SentenceID", "Tense", "O_Sentence", "MainVerb"]].copy()
    new_df.sort_values(by = "SentenceID", inplace=True)
    new_df["Cues"] = top_n_cues_list

    #print("SENTENCE: " + str(new_df.iloc[0,1]))
    #print("sentence: " + str(sample_sentences_df.iloc[0,2]) + "\n")
    #print("CUES: " + str(new_df.iloc[0,3]))

    # Adding additional columns that represnt each cue's strength
    for i in range(0,n_cues-1):
        column_vals = []
        for row in top_n_cue_strengths_list:
            column_vals.append(row[i])
        new_df["StrongCue%s_Strength"%(i+1)] = column_vals

    new_df.rename(columns = {"O_Sentence": "Sentence", 
                            "Tense": "TA",
                            "MainVerb": "TargetVerb"}, inplace = True)
    new_df.to_excel("%s.xlsx"%(save_path))
        
