from os import path
import pandas as pd
import numpy as np
import xarray as xr


### Function to load the weight matrix from an .nc file
def load_weights(LOCATION_OF_WEIGHTS):
    
    ds = xr.open_dataset(LOCATION_OF_WEIGHTS)
    weights = pd.DataFrame(ds.variables['__xarray_dataarray_variable__'].values).T
    weights.columns = ds.variables['outcomes']
    weights['cues'] = ds.variables['cues']
    return(weights)

### Function that finds the n strongest and weakest cue for each cluster based on positive and negative values
def find_strongest_cues(weights, n_strong_cues = 100, negative=False):
    
    new_cols, new_col_names = [], []
    for col in tense_columns[:-1]:
        sorted_col = weights.loc[:, [col, 'cues']].sort_values(by=col, ascending=negative).head(n_strong_cues)
        new_cols += [sorted_col['cues'].values.tolist()]
        new_cols += [sorted_col[col].values.tolist()]
        new_col_names += [col, "{}.weight".format(col)]

    return(pd.DataFrame(new_cols, columns = new_col_names)

def run(PARAMS, n_strong_cues = 200, negative=False):

    TOP = path.join("/home", "tek", "work", "OoOM", "ndl", "ndl_tense", "data_analysis")
    WD = path.join(TOP, "top_cues")
    MATRIX_MULTIVERBS = path.join(TOP, "model_results/NDL_weights_ngrams_multiverbs.nc")
    SAVE_PATH = path.join(WD, "top_cues_results", "Strong_100_pos_cues_fromweights_multiverbs.csv")
    # set WD
    setwd(WD)
    weights = load_weights(MATRIX_MULTIVERBS)
    positive_results_df = find_strongest_cues(weights, n_strong_cues, negative)
    positive_results_df.to_csv(SAVE_PATH)

