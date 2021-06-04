####################
# Preliminary steps
####################

### Set the working directory

### Libraries
import os
import numpy as np
import pandas as pd
from tags_to_tense_1 import *
from tags_to_tense_full_sent import *

def clean_sents(BNC_SENTS, SENTS_CLEAN):
  bnc_tenses =  pd.read_csv(BNC_SENTS, na_values = "")

  ### Reorder the columns
  nC = len(bnc_tenses.columns)
  nV = ((nC-3)/3)  # number of verbs 

  ## Order column names 
  col_order = ["sentence", "sentence_length", "num_verb_tags"]

  for j in range(1,int(nV)+1):
    verb_j = "verb_%s"%(j)
    col_order.append(verb_j)

    verb_j_tag = "verb_%s_tag"%(j)
    col_order.append(verb_j_tag)

    verb_j_position = "verb_%s_position"%(j)
    col_order.append(verb_j_position)

  #set column order
  bnc_tenses = bnc_tenses.reindex(columns=col_order)

  # Remove empty sentences
  bnc_tenses.dropna(subset=["sentence"], inplace=True)

  # Check dim
  print(bnc_tenses.shape) # 4267590 453

  ##########################
  # Remove lengthy sentences
  ##########################

  ### Remove sentences with more than 60 words or with less than 3 words
  bnc_tenses = bnc_tenses[(bnc_tenses["sentence_length"] < 61) & (bnc_tenses["sentence_length"] > 2)] 
  # Check dim
  print(bnc_tenses.shape) # 4227346 453

  ### Remove empty columns
  bnc_tenses.dropna(how='all', axis=1, inplace=True)

  # Check dim
  print(bnc_tenses.shape) # 4227346 81

  ### Save resulting dataset
  bnc_tenses.to_csv(SENTS_CLEAN, encoding="utf-8")

#################
# Annotation
#################
def annotate_tenses(BNC_SENTS, SENTS_CLEAN, TENSES_ANNOTATED_NOINF, TENSES_ANNOTATED_NOINF_CLEAN, TENSES_ANNOTED_CLEAN_N):
  clean_sents(BNC_SENTS, SENTS_CLEAN)
  ### Basic data preparation
  # Reload the data
  bnc_tenses = pd.read_csv(SENTS_CLEAN, encoding="utf-8")

  # Remove 'sentence_length' and 'num_verb_tags' columns
  bnc_tenses.drop(columns= ["sentence_length", "num_verb_tags"], inplace=True)
  (nR, nC) = bnc_tenses.shape #nR=  number of rows, nC = number of columns
  nV = ((nC-1)/3)  # number of verbs 

  ## Rename column names (remove "_" and start from verb1)

  for j in range(1,int(nV)+1):
    bnc_tenses.rename(columns={"verb_%s"%(j):"Verb%s"%(j)}, inplace=True)
    bnc_tenses.rename(columns={"verb_%s_position"%(j):"Position%s"%(j)}, inplace=True)
    bnc_tenses.rename(columns={"verb_%s_tag"%(j):"Tag%s"%(j)}, inplace=True)
  # Change the name of the Sentence column
  #colnames(bnc_tenses)[colnames(bnc_tenses) == "sentence"] = "Sentence"
  bnc_tenses.rename(columns={"sentence":"Sentence"}, inplace=True)
  ### Initialise the data.table that will contain the tense annotations
  max_nV = 26
  tenses_annotated_mat = np.full((bnc_tenses.shape[0], 1+max_nV*5), "")
  tenses_annotated = pd.DataFrame(tenses_annotated_mat)

  col_names = ['Sentence']
  for j in range(1,1+max_nV):
    col_names += ["Tense%s"%(j),"VerbForm%s"%(j), "MainVerb%s"%(j), "Position%s"%(j) ,"Infinitive%s"%(j)]

  tenses_annotated.columns=col_names

  for j in range(0, tenses_annotated.shape[0]):
    tenses_annotated.loc[j] = tag_to_tense_full_sent(bnc_tenses.iloc[j,:], col_names)

  ### Save resulting dataset
  tenses_annotated.to_csv(TENSES_ANNOTATED_NOINF, encoding="utf-8", index=False)
  print(tenses_annotated.shape) # 

  ##################################
  # Remove unnecessery empty columns
  ##################################

  ### Remove empty columns (except infinitive columns of non-empty verb columns)

  # Drop these columns from the dataframe
  names2remove = [col for col in tenses_annotated.columns if (tenses_annotated[col].isnull().all()) and ("Tense" in col)]
  tenses_annotated.drop(names2remove, axis=1, inplace=True)
  tenses_annotated.to_csv(TENSES_ANNOTATED_NOINF_CLEAN, encoding="utf-8", index = False)
  
  ### Divide the full set into smaller subsets
  n_div = 6
  nR = tenses_annotated.shape[0] # number of rows
  nR_div = int(nR/n_div) # number of rows in rach subset (except the last subset which would contain all the remaining rows)
  
  ##############
  # File saving
  ##############

  for n in range(n_div):
    filename_n = "%s%s.csv"%(TENSES_ANNOTED_CLEAN_N,n)
    if (n < n_div):
      tenses_annotated.iloc[(1+(n-1)*nR_div):(n*nR_div), ].to_csv(filename_n)
    else:
      tenses_annotated.iloc[(1+(n-1)*nR_div):nR, ].to_csv(filename_n)
