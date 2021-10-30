####################
# Preliminary steps
####################

### Set the working directory

### Libraries
import os
import logging
logging.basicConfig(level=logging.INFO)

from ndl_tense.data_preparation import tags_to_tense
import numpy as np
import pandas as pd

def clean_sents(tenses_df):
  """
  Remove empty and lengthy sentences from the dataframe

  ----
  PARAMETERS
  ----
  
  tenses_df: pd.DataFrame
    dataframe of the tenses, sentences, sentence lengths and location of verb tags
  ----
  RETURN
  ----
  tenses_df: pd.DataFrame
    The same as the input but with empty and lengthy sentences removed
  """  

  ### Reorder the columns
  nC = len(tenses_df.columns)
  nV = ((nC-3)/3)  # number of verbs 

  ## Order column names 
  if "O_sentence" in tenses_df.columns:
    col_order = ["sentence", "O_sentence", "sentence_length", "num_verb_tags"]
  else:
    col_order = ["sentence", "sentence_length", "num_verb_tags"]

  for j in range(1,int(nV)+1):
    verb_j = "verb_%s"%(j)
    col_order.append(verb_j)

    verb_j_tag = "verb_%s_tag"%(j)
    col_order.append(verb_j_tag)

    verb_j_position = "verb_%s_position"%(j)
    col_order.append(verb_j_position)

  #set column order
  tenses_df = tenses_df.reindex(columns=col_order)

  # Remove empty sentences
  tenses_df.dropna(subset=["sentence"], inplace=True)

  ##########################
  # Remove lengthy sentences
  ##########################

  ### Remove sentences with more than 60 words or with less than 3 words
  tenses_df = tenses_df[(tenses_df["sentence_length"] < 61) & (tenses_df["sentence_length"] > 2)] 

  ### Remove empty columns
  tenses_df.dropna(how='all', axis=1, inplace=True)

  ### Save resulting dataset
  return(tenses_df)

#################
# Annotation
#################
def run(ANNOTATE_FILES, VERBOSE):
  """
  Carry out this stage of processing and annotate the input csv file for tense

  ----
  PARAMETERS
  ----
  ANNOTATE_FILES: list
    files needed to complete this stage of the processing,
    these can be found in the parameter file

  VERBOSE: boolean
    whether to log the process
  ----
  RETURN: Does not return anything, creates an annotated file
  ----
  """  
  
  SENTS, TENSES_ANNOTATED_NOINF_CLEAN = ANNOTATE_FILES[0], ANNOTATE_FILES[1]
  ### Basic data preparation
  tenses_df =  pd.read_csv("%s.csv"%(SENTS), na_values = "")

  tenses_df = clean_sents(tenses_df)
  
  # Remove 'sentence_length' and 'num_verb_tags' columns
  tenses_df.drop(columns= ["sentence_length", "num_verb_tags"], inplace=True)
  (nR, nC) = tenses_df.shape #nR=  number of rows, nC = number of columns
  nV = int((nC-1)/3)  # number of verbs 

  ## Rename column names (remove "_" and start from verb1)

  for j in range(1,int(nV)+1):
    tenses_df.rename(columns={"verb_%s"%(j):"Verb%s"%(j)}, inplace=True)
    tenses_df.rename(columns={"verb_%s_position"%(j):"Position%s"%(j)}, inplace=True)
    tenses_df.rename(columns={"verb_%s_tag"%(j):"Tag%s"%(j)}, inplace=True)
  # Change the name of the Sentence column
  #colnames(tenses_df)[colnames(tenses_df) == "sentence"] = "Sentence"
  tenses_df.rename(columns={"sentence":"Sentence"}, inplace=True)
  ### Initialise the data.table that will contain the tense annotations
  tenses_annotated_mat = np.full((tenses_df.shape[0], 1+nV*4), "")
  tenses_annotated = pd.DataFrame(tenses_annotated_mat)

  col_names = ['Sentence']
  for j in range(1,1+nV):
    col_names += ["Tense%s"%(j),"VerbForm%s"%(j), "MainVerb%s"%(j), "Position%s"%(j)]
  tenses_annotated.columns=col_names

  for j in range(0, tenses_annotated.shape[0]):
    tenses_annotated.loc[j] = tags_to_tense.get_vect_tenses(tenses_df.iloc[j,:])
    #print(tenses_annotated.iloc[j,4:8])

  ##################################
  # Remove unnecessery empty columns
  ##################################

  ### Remove empty columns (except infinitive columns of non-empty verb columns)

  # Drop these columns from the dataframe
  names2remove = [col for col in tenses_annotated.columns if (tenses_annotated[col].isnull().values.all())]
  
  tenses_annotated.drop(names2remove, axis=1, inplace=True)

  non_empty_verb_col = len([col for col in tenses_annotated.columns if "MainVerb" in col])
  for j in range(non_empty_verb_col):
    tenses_annotated["Infinitive%s"%(j+1)] = np.nan
  
  if "O_sentence" in tenses_df.columns:
    tenses_annotated["O_Sentence"] = tenses_df['O_sentence']

  tenses_annotated.to_csv("%s.csv"%(TENSES_ANNOTATED_NOINF_CLEAN), encoding="utf-8", index = False)
  if VERBOSE:
    logging.info("STEP 2: Annotating tenses complete\n")
  