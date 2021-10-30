from numpy import transpose
from pandas import DataFrame
from ndl_tense.data_preparation import row_tenses
import re

def shift_and_rename(vect_tags, diff, start):
    # renaming the shifted columns
    rename_col = dict()
    for j in range(start, len(vect_tags.columns)):
        name_j = vect_tags.columns[j]
        ind_old = int(re.sub("[^0-9]", "",(name_j)))
        ind_new = ind_old - diff
        new_name = name_j.replace(str(ind_old), str(ind_new))
        rename_col.update({name_j: new_name})
    return(rename_col)

def get_vect_tenses(vect_tags, o_sents):
    # Function that accepts a row vector containing verbs, tags, and positions then convert it
    # to a row vector that includes the same variables as well as verb form, main verb and tense   
    ############ Generating the tenses ##############

    ### Define tense of the first verb 
    vect_tenses = {"Sentence": vect_tags['Sentence']}
    i = 0 # Counter for the number of tenses extracted so far
    vect_tags = vect_tags.to_frame().T
    if o_sents:
        sen_end = 6
        start = 2
    else:
        sen_end = 5
        start = 1
    while(str(vect_tags.iloc[0]['Verb1']) != "nan"):
        # One round of tense extraction
        vect_tenses_1round = row_tenses.get_tenses(vect_tags)
        
        # remove the verbs and their tags depending on the verb form extracted
        num_v_drop = 0
        split_v_form = vect_tenses_1round["VerbForm"].split(" ")
        if split_v_form != [""] and split_v_form != []:
            num_v_drop = len(split_v_form)
        len_vect_tags = vect_tags.shape[1]
        if num_v_drop == 0: # If no tense detected move to the second verb tag (only if other tags exist)
            # A length of tags less than 6 marks the end of the sentence
            if len_vect_tags < sen_end:
                break
            else:
                # shifting all columns to the left to account for the columns already processed
                if o_sents:
                    vect_tags = vect_tags.iloc[:,[0,1]+list(range(5,len_vect_tags))]
                else:
                    vect_tags = vect_tags.iloc[:,[0]+list(range(4,len_vect_tags))]
                vect_tags.rename(columns = shift_and_rename(vect_tags, 1, start), inplace = True)
        else:
            i += 1
            vect_tenses.update({"{}{}".format(key, i) : value for (key, value) in vect_tenses_1round.items()})
            # A length of tags less than (3*num_v_drop+3) marks the end of the sentence
            # as the resulting dataframe would not have the necessary fields of

            # Sentence, o_Sentence, VerbX, TagX and PositionX
            if (len_vect_tags < (3*num_v_drop+3)):
                break
            # Sentence, VerbX, TagX and PositionX
            else:
                if o_sents:
                    vect_tags = vect_tags.iloc[:,[0,1]+list(range(3*num_v_drop+2,len_vect_tags))]
                else:
                    vect_tags = vect_tags.iloc[:,[0]+list(range(3*num_v_drop+1,len_vect_tags))]
                vect_tags.rename(columns = shift_and_rename(vect_tags, num_v_drop, start), inplace= True)
    return(vect_tenses)
