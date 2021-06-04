####################
# Preliminary steps
####################

### Import necessary packages
import pandas as pd
import time
import sys

def extract_infinitives(TENSES_GZ, COOC_FREQ_CSV, INFINITIVES_CSV):
    ### Set the max width of a column
    pd.set_option('display.max_colwidth', 200)
    pd.set_option('display.max_columns', 10)

    ####################
    # Data preparation
    ####################

    ### Load the data
    start = time.time()
    tenses = pd.read_csv(TENSES_GZ, compression='gzip', usecols = ['Infinitive', 'Tense'])
    _ = sys.stdout.write('Loading the data took %ds' %((time.time()-start)))

    print(f'Number of examples: {len(tenses)}')
    # Number of examples: 7041928

    tenses['Tense'].value_counts()
    # present.simple       3245123
    # past.simple          2639396
    # present.perf          339566
    # future.simple         272308
    # past.perf             253212
    # present.prog          148123
    # past.prog             114803
    # present.perf.prog      11308
    # future.prog             8059
    # past.perf.prog          7038
    # future.perf             2962
    # future.perf.prog          30

    tenses.columns
    # Index(['Tense', 'Infinitive'], dtype='object')

    ### Calculate the frequency and proportion of co-occurence between each infinitive and tense
    cooc_freqs = tenses.groupby(["Infinitive", "Tense"]).size().reset_index(name="Freq")  
    cooc_freqs.shape 
    # (41849, 3)

    cooc_freqs = pd.crosstab(tenses["Infinitive"], tenses["Tense"])
    cooc_freqs.shape 
    # (14723, 12)

    # Rename the columns
    tense_col_names = list(map(lambda s: "_".join([s.replace('.', '_'),"freq"]), cooc_freqs.columns))
    cooc_freqs.columns = tense_col_names
    cooc_freqs.head()
    #                          future_perf_freq  future_perf_prog_freq  ...  present_prog_freq  present_simple_freq
    # a2                                      0                      0  ...                  0                    1
    # aaaagh                                  0                      0  ...                  0                    1
    # aaahed                                  0                      0  ...                  0                    0
    # aaargh                                  0                      0  ...                  0                    2
    # aaatgctgactaaggaacaaggt                 0                      0  ...                  0                    1

    # Add a column that gives the sum of the frequencies
    cooc_freqs['total_freq'] = cooc_freqs.sum(axis = 1)

    ### Transform the frequencies into proportions
    # Add the columns (empty)
    columns_prop = list(map(lambda s: s.replace('_freq', '_prop'), tense_col_names))
    cooc_freqs = cooc_freqs.reindex(columns = cooc_freqs.columns.tolist() + columns_prop)

    for col_name in columns_prop: 
        cooc_freqs[col_name] = cooc_freqs[col_name.replace('_prop', '_freq')]/cooc_freqs['total_freq']

    ### Filter out the verbs that appear less than 10 times
    cooc_freqs = cooc_freqs[cooc_freqs['total_freq']>=10] # 4676 verbs remaining
    infinitives = cooc_freqs.index.to_frame()

    ### Export the co-occurence and infinitives datasets
    cooc_freqs.to_csv(COOC_FREQ_CSV, sep = ',')
    infinitives.to_csv(INFINITIVES_CSV, sep = ',', header = False, index = False)
