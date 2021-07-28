from numpy import transpose
from pandas import DataFrame
from ndl_tense.data_preparation import row_tenses
import re

def get_vect_tenses(vect_tags):
    # Function that accepts a row vector containing verbs, tags, and positions then convert it
    # to a row vector that includes the same variables as well as verb form, main verb and tense   

    ############ Generating the tenses ##############

    ### Define tense of the first verb 
    vect_tenses = {"Sentence": vect_tags['Sentence']}
    i = 0 # Counter for the number of tenses extracted so far
    vect_tags = vect_tags.to_frame().T
    while(vect_tags.iloc[0]['Verb1'] != ""):
        # One round of tense extraction
        vect_tenses_1round = row_tenses.get_tenses(vect_tags)

        # remove the verbs and their tags depending on the verb form extracted
        #num_v_drop = length(unlist(strsplit(vect_tenses_1round['VerbForm'], split = ' ')))
        num_v_drop = len(vect_tenses_1round["VerbForm"].split(" "))
        len_vect_tags = len(vect_tags)
        if num_v_drop == 0: # If no tense detected move to the second verb tag (only if other tags exist)
            if len_vect_tags < 5:
                break
            else:
                #vect_tags = t(as.matrix(vect_tags[, c(1, 5:length(vect_tags))]))
                vect_tags = transpose(vect_tags.iloc[:,5:len_vect_tags+1])
                # Change verb indices
                for j in range(1, len_vect_tags):
                    name_j = vect_tags.columns[j]
                    ind_old = int(re.sub("[^0-9]", "",(name_j)))
                    ind_new = ind_old - 1
                    name_j[:-len(ind_old)] = ind_new
                    vect_tags.columns[j] = name_j
        else:
            i = i+1
            vect_tenses.update({"%s%s"%(key, i) : value for (key, value) in vect_tenses_1round.items()})
            if (len_vect_tags < (3*num_v_drop+2)):
                break
            else:
                vect_tags = transpose(vect_tags[:,(1,3*num_v_drop+2):len_vect_tags+1])
                for j in range(1, len_vect_tags):
                    name_j = vect_tags.columns[j]
                    ind_old = int(re.sub("[^0-9]", "",(name_j)))
                    ind_new = ind_old - num_v_drop
                    name_j[:-len(ind_old)] = ind_new
                    vect_tags.columns[j] = name_j
    return(vect_tenses)

