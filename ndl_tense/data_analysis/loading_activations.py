from ndl_tense.simulations import ndl_model
import ndl_tense.simulations.modelling as md
import pandas as pd

MODEL_PATH = "D:\\work\\OoOM\\ndl\\ndl_tense\\data_analysis\\Model_results\\model_results\\NDL_model_ngrams_multiverbs"
strong_cues = "D:\\work\\OoOM\\ndl\\ndl_tense\\data_analysis\\Top_cues\\top_cue_results\\Strong_500_pos_both_cues_multiverbs.csv"

cues = pd.read_csv(strong_cues).iloc[:,0]
model = md.import_model("%s.h5"%(MODEL_PATH))

all_cues = model.weights.coords["cues"].values.tolist()
print(all_cues)
cues = [cue for cue in cues if cue in all_cues]
print(len(cues))
cue0 = cues[0]
print(cue0)
print(model.weights.loc[{'cues':cue0}].values)
#activations = model.weights.loc[{'cues': cues}].values.sum(axis=1)
#print(activations)

#from ndl_tense.simulations import ndl_model
#import ndl_tense.simulations.modelling as md
#import pandas as pd
#import netCDF4 as nc

#MODEL_PATH = "D:\\work\\OoOM\\ndl\\ndl_tense\\data_analysis\\Model_results\\results_29_09_2021\\cues_weights.csv"
#MODEL_PATH = "D:\\work\\OoOM\\ndl\\ndl_tense\\data_analysis\\Model_results\\results_29_09_2021\\NDL_model_ngrams_multiverbs.h5"
#strong_cues = "D:\\work\\OoOM\\ndl\\ndl_tense\\data_analysis\\Top_cues\\top_cue_results\\Strong_500_pos_both_cues_multiverbs.csv"

#cues = pd.read_csv(strong_cues).iloc[:,0]
#model = pd.read_csv(MODEL_PATH)
#nc_model = nc.Dataset(MODEL_PATH)

#print(nc_model)
#all_cues = model.weights.coords["cues"].values.tolist()
#cues = [cue for cue in cues if cue in all_cues]

#activations = model.weights.loc[{'cues': cues}].values.sum(axis=1)
#print(activations)