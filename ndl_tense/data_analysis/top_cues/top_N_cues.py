import pandas as pd
import numpy as np
import xarray as xr


# location of wieghts obtained from training
LOCATION_OF_WEIGHTS = "/weights_skipgrams_no_lemmas.nc"

# Where to save the weights opened and converted to a csv format
#SAVE_WEIGHTS_CSV = "work/OoOM/Marta/weights_skipgrams_no_lemmas.csv"

#  Path to where the results are saved
TOP_10_CUES = "work/OoOM/Marta/top_10_cues_skipgrams_no_lemmas.csv"

# How many rows to saves
N = 10


ds = xr.open_dataset(LOCATION_OF_WEIGHTS)
weights = pd.DataFrame(ds.variables['__xarray_dataarray_variable__'].values).T
weights.columns = ds.variables['outcomes']
weights['cues'] = ds.variables['cues']


#weights = pd.read_csv("weights_skipgrams_no_lemmas.csv")
top_imperfect = weights.sort_values('imperfective',ascending=False)[['cues', 'imperfective']]
top_perfect = weights.sort_values('perfective', ascending=False)[['cues', 'perfective']]

top_imperfect.rename(columns= {'cues': 'TopImperfectiveCues'}, inplace=True)
top_perfect.rename(columns= {'cues': 'TopPerfectiveCues'}, inplace=True)
top_perfect.reset_index(drop=True, inplace=True)
top_imperfect.reset_index(drop=True, inplace=True)

new_frame = pd.concat([top_imperfect, top_perfect], axis=1)
print(new_frame.head(N))
new_frame.head(N).to_csv(TOP_10_CUES, index=False)