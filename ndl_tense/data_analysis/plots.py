import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('ggplot')

####################
# Preliminaty steps
####################


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

def create_plots(df, col1, col2, file_path):
    plt.figure(figsize=[12, 11])
    plt.axhline(1/11, linestyle='--', color="black")
    plt.bar(col1, col2)
    plt.xticks(rotation=30, ha='right')
    plt.xlabel('Tense', fontsize=12)
    plt.ylabel('Accuracy', fontsize=12)
    #png('./results/Accuracy_per_tense.png', he=6, wi=9, units='in', res=300)
    plt.savefig(file_path)


def plot_vars(df, N, cols, FILE_PATH):
    plot_df = accuracy(df.copy(), cols).head(N)
    create_plots(plots_df, plot_df.index.values.tolist(), plots_df["Accuracy"].values.tolist(), FILE_PATH)

def run(DATA_ANALYSIS_PLOTS_FILES, FULL=True, VERBOSE=True):

    OVERALL_ACCURACY = DATA_ANALYSIS_PLOTS_FILES[0]
    ACCURACY_PER_COMP = DATA_ANALYSIS_PLOTS_FILES[1]
    ACCURACY_SECOND_TENSE = DATA_ANALYSIS_PLOTS_FILES[2]
    ACCURACY2_TENSE_COMP = DATA_ANALYSIS_PLOTS_FILES[3]
    ACCURACY_THIRD_TENSE = DATA_ANALYSIS_PLOTS_FILES[4]
    ACCURACY3_TENSE_COMP = DATA_ANALYSIS_PLOTS_FILES[5]
    ACCURACY_TOP_THREE = DATA_ANALYSIS_PLOTS_FILES[6]
    ACCURACY_T3_COMP = DATA_ANALYSIS_PLOTS_FILES[7]
    
    ### Loading the data 
    df = pd.read_csv(RESULTS)
    df = df.drop(["Sentence", "FilteredCues", "VerbForm", "MainVerb"], axis=1)
    if FULL:
        plot_vars(df, 10, ['Accuracy', 'Tense'], OVERALL_ACCURACY)
        plot_vars(df, 4, ['Accuracy1', 'Tense_compact'], ACCURACY_PER_COMP)

        plot_vars(df, 10, ['Accuracy2', 'Tense'], ACCURACY_SECOND_TENSE)
        plot_vars(df, 4, ['Accuracy2', 'Tense_compact'], ACCURACY2_TENSE_COMP)

        plot_vars(df, 10, ['Accuracy3', 'Tense'], ACCURACY_THIRD_TENSE)
        plot_vars(df, 4, ['Accuracy3', 'Tense_compact'], ACCURACY3_TENSE_COMP)

        plot_vars(df, 10, ['AccuracyTopThree', 'Tense'], ACCURACY_TOP_THREE)
        plot_vars(df, 4, ['AccuracyTopThree', 'Tense_compact'], ACCURACY_T3_COMP)
    else:
        plot_vars(df, N, cols, path)









