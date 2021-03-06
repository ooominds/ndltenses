import pandas as pd
import numpy as np
from ndl_tense.post_processing import sample_sentences


def unique_cues(sample_df, cues_index, keys):
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
    for row in range(sample_df.shape[0]):
        # to avoid repeated cues, use sets
        unique_cues_set = unique_cues_set.union(sample_df.iloc[row, cues_index].split('_'))
    # random weights
    dummy_data = np.random.rand(len(unique_cues_set), len(keys))
    cues_df = pd.DataFrame(dummy_data, index = list(unique_cues_set), columns =keys)
    cues_df.to_csv("cue_weights.csv")
    return(cues_df)

def sentences_in_cues(sens_filepath, cue_weights, n_cues):
    sens_df = pd.read_csv(sens_filepath)
    #sens_df['SplitCols'] = sens_df['NgramCuesWithInfinitive'].apply(lambda x: set(x.split('_')))
    sens_df['SplitCols'] = sens_df['FilteredCues'].apply(lambda x: set(x.split('_')))

    test_sens = sens_df[sens_df['SplitCols'].apply(lambda x: x.issubset(list(cue_weights.index)))]
    print(test_sens.columns)
    test_sens.to_csv("reduced_sentences.csv")

# Find the top n cues and their associated weights
def find_top_n_cues(cues, ta, cue_weights, n_cues):
    wanted_cues_subset = cue_weights.loc[cues]
    top_cues = wanted_cues_subset.nlargest(n_cues, ta)
    return(list(top_cues.index), list(top_cues[ta]))
    

def run(O_SENS, TENSES_FILE, CUE_WEIGHT_FILE, save_path, ratios, n_cues, sample_size):
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

    # present.simple       1410
    # past.simple           441
    # present.prog          133
    # present.perf          132
    # future.simple          91
    # past.prog              30
    # present.perf.prog       5
    # future.prog             5
    # past.perf               5

    cue_weights = pd.read_csv("%s.csv"%(CUE_WEIGHT_FILE), index_col=0)
    keys = list(cue_weights.columns)
    #keys = ["present.simple",
    #        "past.simple",
    #        "present.prog",
    #        "present.perf"]

    sentences_in_cues("%s.csv"%(TENSES_FILE), cue_weights, n_cues)
    o_sen = pd.read_csv("{}.csv".format(O_SENS))
    o_sen['SentenceID'] = np.arange(o_sen.shape[0])
    o_sen.rename(columns={'Sentence':'O_Sentence'}, inplace=True)
    o_sen.sort_values(by="SentenceID", inplace=True)
    
    o_sen = o_sen[["SentenceID", "O_Sentence"]]
    sample_sentences_df = sample_sentences.run("reduced_sentences.csv", keys, ratios, sample_size, False)
    sample_sentences_df.join(o_sen, on="SentenceID", how="left")
    sample_sentences_df.sort_values(by = "SentenceID", inplace=True)

    # getting index (an integer represnetation) of wanted columns
    cues_index = sample_sentences_df.columns.get_loc('FilteredCues')
    ta_index = sample_sentences_df.columns.get_loc('Tense')

    #cue_weights = unique_cues(sample_sentences_df, keys, cues_index)
    top_n_cues_list, top_n_cue_strengths_list = [], []    

    for row in range(sample_sentences_df.shape[0]):
        ta = sample_sentences_df.iloc[row, ta_index]
        cues = sample_sentences_df.iloc[row, cues_index].split('_')
        top_n_cues, top_n_cue_strengths = (find_top_n_cues(cues, ta, cue_weights, n_cues))

        #print("top N cues: " + str(top_n_cues) + "\n")
        top_n_cues_list.append(top_n_cues)
        top_n_cue_strengths_list.append(top_n_cue_strengths)
    
    new_df = sample_sentences_df[["SentenceID", "Tense", "O_Sentence", "MainVerb"]].copy()
    new_df.sort_values(by = "SentenceID", inplace=True)
    new_df["Cues"] = top_n_cues_list

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
        
