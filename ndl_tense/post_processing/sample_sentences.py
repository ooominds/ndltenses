import pandas as pd        
from math import gcd, ceil
from functools import reduce
import logging
logger.setLevel(level=logging.INFO)

def sample_sens(sen_df, sample_sizes):
    new_frame = pd.DataFrame()
    for tense_aspect, sample_size in sample_sizes.items():
        try:
            new_frame = new_frame.append(sen_df[sen_df['Tense'] == tense_aspect].sample(sample_size, random_state=1))
        except:
            next
    return(new_frame)

def simple_band_sample(ratios, sample_size):
    while(sum(ratios) > sample_size):
        ratios = [ceil(i/2) for i in ratios]
        denom = reduce(gcd,ratios)
        ratios = [ceil(i/denom) for i in ratios]
    print(ratios)
    return(ratios)

# BNC full

# present.simple       655438
# past.simple          610475
# present.perf         100503
# future.simple         67433
# present.prog          46884
# past.perf             45191
# past.prog             26264
# present.perf.prog      3398
# future.prog            2336
# past.perf.prog         1288
# future.perf             660
# future.perf.prog          9

# present.simple       3229514
# past.simple          2636030
# present.perf          338791
# future.simple         271345
# past.perf             253110
# present.prog          139878
# past.prog             108682
# present.perf.prog      11278
# future.prog             8021
# past.perf.prog          7032
# future.perf             2955
# future.perf.prog          30

# Spoken

# present.simple       1410
# past.simple           441
# present.prog          133
# present.perf          132
# future.simple          91
# past.prog              30
# present.perf.prog       5
# future.prog             5
# past.perf               5

def run(file_path, keys, ratios, sample_size, VERBOSE):
    sen_df = pd.read_csv(file_path)
    ratios = simple_band_sample(ratios, sample_size)
    ta_sample_sizes = dict(zip(keys,ratios))
    sample_sentences_df = sample_sens(sen_df, ta_sample_sizes)
    if VERBOSE:
        logger.info("sentence sampling complete")
    return(sample_sentences_df)
