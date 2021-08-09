####################
# Preliminary steps
####################

### Set the working directory

### Libraries
import os
from ndl_tense.data_preparation import tags_to_tense
import numpy as np
import pandas as pd

def clean_sents(bnc_tenses):

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

  ##########################
  # Remove lengthy sentences
  ##########################

  ### Remove sentences with more than 60 words or with less than 3 words
  bnc_tenses = bnc_tenses[(bnc_tenses["sentence_length"] < 61) & (bnc_tenses["sentence_length"] > 2)] 

  ### Remove empty columns
  bnc_tenses.dropna(how='all', axis=1, inplace=True)

  # Check dim
  print(bnc_tenses.shape) # 4227346 81

  ### Save resulting dataset
  return(bnc_tenses)

#################
# Annotation
#################
def run(ANNOTATE_FILES):
  SENTS, TENSES_ANNOTATED_NOINF_CLEAN = ANNOTATE_FILES[0], ANNOTATE_FILES[1]
  ### Basic data preparation
  bnc_tenses =  pd.read_csv("%s.csv"%(SENTS), na_values = "")

  bnc_tenses = clean_sents(bnc_tenses)
  
  # Remove 'sentence_length' and 'num_verb_tags' columns
  bnc_tenses.drop(columns= ["sentence_length", "num_verb_tags"], inplace=True)
  (nR, nC) = bnc_tenses.shape #nR=  number of rows, nC = number of columns
  nV = int((nC-1)/3)  # number of verbs 

  ## Rename column names (remove "_" and start from verb1)

  for j in range(1,int(nV)+1):
    bnc_tenses.rename(columns={"verb_%s"%(j):"Verb%s"%(j)}, inplace=True)
    bnc_tenses.rename(columns={"verb_%s_position"%(j):"Position%s"%(j)}, inplace=True)
    bnc_tenses.rename(columns={"verb_%s_tag"%(j):"Tag%s"%(j)}, inplace=True)
  # Change the name of the Sentence column
  #colnames(bnc_tenses)[colnames(bnc_tenses) == "sentence"] = "Sentence"
  bnc_tenses.rename(columns={"sentence":"Sentence"}, inplace=True)
  ### Initialise the data.table that will contain the tense annotations
  tenses_annotated_mat = np.full((bnc_tenses.shape[0], 1+nV*4), "")
  tenses_annotated = pd.DataFrame(tenses_annotated_mat)

  col_names = ['Sentence']
  for j in range(1,1+nV):
    col_names += ["Tense%s"%(j),"VerbForm%s"%(j), "MainVerb%s"%(j), "Position%s"%(j)]
  tenses_annotated.columns=col_names

  for j in range(0, tenses_annotated.shape[0]):
    tenses_annotated.loc[j] = tags_to_tense.get_vect_tenses(bnc_tenses.iloc[j,:])

  ##################################
  # Remove unnecessery empty columns
  ##################################

  ### Remove empty columns (except infinitive columns of non-empty verb columns)

  # Drop these columns from the dataframe
  names2remove = [col for col in tenses_annotated.columns if (tenses_annotated[col].isnull().all())]
  tenses_annotated.drop(names2remove, axis=1, inplace=True)
  non_empty_verb_col = len([col for col in tenses_annotated.columns if "MainVerb" in col])
  for j in range(non_empty_verb_col):
    tenses_annotated["Infinitive%s"%(j+1)] = np.nan

  tenses_annotated.to_csv("%s.csv"%(TENSES_ANNOTATED_NOINF_CLEAN), encoding="utf-8", index = False)
  
  ### Divide the full set into smaller subsets
  #n_div = 6
  #nR = tenses_annotated.shape[0] # number of rows
  #nR_div = int(nR/n_div) # number of rows in rach subset (except the last subset which would contain all the remaining rows)
  
  ##############
  # File saving
  ##############

  #for n in range(n_div):
  #  filename_n = "%s%s.csv"%(TENSES_ANNOTATED_CLEAN_N,n)
  #  if (n < n_div):
  #    tenses_annotated.iloc[(1+(n-1)*nR_div):(n*nR_div), ].to_csv(filename_n)
  #  else:
  #    tenses_annotated.iloc[(1+(n-1)*nR_div):nR, ].to_csv(filename_n)
