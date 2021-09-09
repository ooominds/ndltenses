import pandas as pd        
from math import gcd, ceil
from functools import reduce
import logging
logging.basicConfig(level=logging.INFO)

def sample_sens(sen_df, sample_sizes):
    new_frame = pd.DataFrame()
    for tense_aspect, sample_size in sample_sizes.items():
        try:
            new_frame = new_frame.append(sen_df[sen_df['Tense'] == tense_aspect].sample(sample_size))
        except:
            next
    return(new_frame)

def simple_band_sample(ratios, sample_size):
    while(sum(ratios) > 2*sample_size):
        ratios = [ceil(i/2) for i in ratios]
        denom = reduce(gcd,ratios)
        ratios = [ceil(i/denom) for i in ratios]
    return(ratios)


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


def run(file_path, keys, ratios, sample_size, VERBOSE):
    sen_df = pd.read_csv(file_path)
    ratios = simple_band_sample(ratios,sample_size)
    ta_sample_sizes = dict(zip(keys,ratios))
    sample_sens(sen_df, ta_sample_sizes)
    if VERBOSE:
        logging.info("sentence sampling complete")
