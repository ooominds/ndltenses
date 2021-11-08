import pandas as pd
import numpy as np
from os import path, chdir
import matplotlib.pyplot as plt
plt.style.use('ggplot')

####################
# Preliminaty steps
####################

### Set WD
WD_PATH = path.join("/home","tek", "work","OoOM","ndl","ndl_tense","data_analysis")

# Results file - this file is too large to be on GitHub so must be created post-processing
RESULTS = path.join(".","model_results","Results_all_testset_ngrams_multiverbs.csv")

OVERALL_ACCURACY = path.join(".","results", "Accuracy_per_tense.png")
ACCURACY_PER_COMP = path.join(".","results", "Accuracy_per_tense_compact.png")

ACCURACY_SECOND_TENSE = path.join(".","results", "Accuracy2_per_tense.png.png")
ACCURACY2_TENSE_COMP = path.join(".","results", "Accuracy2_per_tense_compact.png")

ACCURACY_THIRD_TENSE = path.join(".","results", "Accuracy3_per_tense.png")
ACCURACY3_TENSE_COMP = path.join(".","results", "Accuracy3_per_tense_compact.png")

ACCURACY_TOP_THREE = path.join(".","results", "Accuracy_top3_per_tense.png")
ACCURACY_T3_COMP = path.join(".","results", "Accuracy_top3_per_tense_compact.png")

#WD_PATH  = 'F:English_tense","Data_analysis","Model_results","'
chdir(WD_PATH)


###########################################
# Data preparation
###########################################

### Loading the data 
#data = read.csv(file = "./Data/Results_all_testset_ngrams_multiverbs.csv")
df = pd.read_csv(RESULTS)
#data = read.csv(file = ".","results_29_09_2021","new_sample_thing.csv")
#data = read.csv(file = "F:English_tense","Data_analysis","Model_results","Data","Results_all_testset_ngrams_multiverbs_new.csv")
df = df.drop(["Sentence", "FilteredCues", "VerbForm", "MainVerb"], axis=1,)

######################
# Plots 
######################

############# Accuracy overall ###############
def accuracy(df, groupby_cols=['Accuracy', 'Tense']):
    acc_tense = df.groupby(groupby_cols[1]).agg({groupby_cols[0]: ['mean']})
    acc_tense.columns = ["Accuracy"]  # change column names
    acc_tense.sort_values(by=['Accuracy'], ascending=False, inplace=True)
    print(acc_tense)
    return(acc_tense)

def plots(df, col1, col2, file_path):
    plt.figure(figsize=[12, 11])
    plt.axhline(1/11, linestyle='--', color="black")
    plt.bar(col1, col2)
    plt.xticks(rotation=30, ha='right')
    plt.xlabel('Tense', fontsize=12)
    plt.ylabel('Accuracy', fontsize=12)
    #png('./results/Accuracy_per_tense.png', he=6, wi=9, units='in', res=300)
    plt.savefig(file_path)


    # Increase the size of the figure (chart)
    

### overall accuracy ##
overall_accuracy = accuracy(df.copy(), ['Accuracy', 'Tense']).head(10)
plots(overall_accuracy, overall_accuracy.index.values.tolist(), overall_accuracy["Accuracy"].values.tolist(), OVERALL_ACCURACY)
accuracy_per_comp = accuracy(df.copy(), ['Accuracy1', 'Tense_compact']).head(4)
plots(accuracy_per_comp, accuracy_per_comp.index.values.tolist(), accuracy_per_comp["Accuracy"].values.tolist(), ACCURACY_PER_COMP)

accuracy_second_tense = accuracy(df.copy(), ['Accuracy2', 'Tense']).head(10)
plots(accuracy_second_tense, accuracy_second_tense.index.values.tolist(), accuracy_second_tense["Accuracy"].values.tolist(), ACCURACY_SECOND_TENSE)
accuracy2_tense_comp = accuracy(df.copy(), ['Accuracy2', 'Tense_compact']).head(4)
plots(accuracy2_tense_comp, accuracy2_tense_comp.index.values.tolist(), accuracy2_tense_comp["Accuracy"].values.tolist(), ACCURACY2_TENSE_COMP)

accuracy_third_tense = accuracy(df.copy(), ['Accuracy3', 'Tense']).head(10)
plots(accuracy_third_tense, accuracy_third_tense.index.values.tolist(), accuracy_third_tense["Accuracy"].values.tolist(), ACCURACY_THIRD_TENSE)
accuracy3_tense_comp = accuracy(df.copy(), ['Accuracy3', 'Tense_compact']).head(4)
plots(accuracy3_tense_comp, accuracy3_tense_comp.index.values.tolist(), accuracy3_tense_comp["Accuracy"].values.tolist(), ACCURACY3_TENSE_COMP)

accuracy_top_three = accuracy(df.copy(), ['AccuracyTopThree', 'Tense']).head(11)
plots(accuracy_top_three, accuracy_top_three.index.values.tolist(), accuracy_top_three["Accuracy"].values.tolist(), ACCURACY_TOP_THREE)
accuracy_t3_comp = accuracy(df.copy(), ['AccuracyTopThree', 'Tense_compact']).head(11)
plots(accuracy_t3_comp, accuracy_t3_comp.index.values.tolist(), accuracy_t3_comp["Accuracy"].values.tolist(), ACCURACY_T3_COMP)










