import pandas as pd
import numpy as np
from os import chdir, join

#WD = '/rds/projects/d/divjakd-ooo-machines/Users/tekevwe/ndl_tense_package/ndl_tense/data_analysis/Model_results'
#ACTIVATION_TEST = WD + "/results_29_09_2021/Activations_testset_ngrams_multiverbs.csv"

WD = 'D:\\work\\OoOM\\ndl\\ndl_tense\\data_analysis\\Model_results'
#ACTIVATION_TEST = WD + "\\results_29_09_2021\\Activations_testset_ngrams_multiverbs.csv"
ACTIVATION_TEST = WD + "\\results_29_09_2021\\cues_weights_w_rows.csv"
#ACTIVATION_TEST = WD + "\\results_29_09_2021\\NDL_model_ngrams_multiverbs.h5"
chdir(WD)

activations_df = pd.read_csv(ACTIVATION_TEST, index_col=0)
#model = md.import_model("%s.h5"%(ACTIVATION_TEST))

def calculate_activation_support(activations_df, activ_cols):
    for j in range(len(activ_cols)):
        name = activ_cols[j]
        new_col = []
        for x in range(activations_df.shape[0]):
            sub = activations_df.iloc[x, [y for y in range(len(activ_cols)) if y > j or y < j]]
            new_col.append(min([activations_df.iloc[x,j] - s for s in sub]))
        activations_df[name] = new_col
    activations_df.to_csv("cues_with_activation.csv")
     

### Prepare the predictions from the activations dataframe 
activ_cols = activations_df.columns.tolist()
print(activations_df)
calculate_activation_support(activations_df, activ_cols)