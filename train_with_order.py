from pyndl import ndl, activation
from os.path import dirname
import numpy as np
import xarray
import pandas as pd
import csv
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix


def extract_data(cues_list, index):
    name = cues_list[index]
    train_set_name = 'Data/train_' + name + '.csv.gz'
    matrix_name = 'Data/weights_' + name + '.nc'
    return train_set_name, matrix_name


def train(events, matrix):
    # uses pyndl.ndl.ndl to learn weights from events file
    read_events = pd.read_csv(events, sep='\t')
    read_events['cues'] = read_events['cues'].str.strip()
    read_events['outcomes'] = read_events['outcomes'].str.strip()
    read_events.to_csv(events, index=False, sep='\t')
    weights = ndl.ndl(events=events,
                      alpha=0.01, betas=(1, 1),
                      number_of_threads=16,
                      method='openmp',
                      remove_duplicates=True)
    # stores learned weights in NetCDF format
    weights.to_netcdf(matrix)


def retrieve_weights(filename):
    with xarray.open_dataarray(filename) as weights_read:
        weights = weights_read
    return weights





def stack_matrices(m1, m2, m3, m4, m5, m6, final_matrix_name):
    final_matrix = np.concatenate((m1, m2, m3, m4, m5, m6), axis=1)
    final_matrix.to_netcdf(final_matrix_name)


def activations_to_predictions(activations):
    # Predicted tenses from the activations
    y_pred = []
    for j in range(activations.shape[1]):
        activation_col = activations[:, j]
        try:  # If there is a single max
            argmax_j = activation_col.where(activation_col == activation_col.max(), drop=True).squeeze().coords[
                'outcomes'].values.item()
        except:  # If there are multiple maxes
            maxes = activation_col.where(activation_col == activation_col.max(), drop=True).values
            argmax_j = np.random.choice(maxes, 1, replace=False).squeeze()
        y_pred.append(argmax_j)
    return y_pred


def import_index_system(index_system_path, N_tokens=None):
    # Load the index system
    with open(index_system_path, 'r', encoding='utf-8') as file:
        index_system_df = csv.reader(file)
        index_system_dict = {}
        # Import all indices if N_tokens is not given
        if N_tokens == None:
            for line in index_system_df:
                k, v = line
                index_system_dict[k] = int(v)
        # Limit the index system to the 'N_tokens' first enteries
        else:
            for i in range(N_tokens):
                k, v = next(index_system_df)
                index_system_dict[k] = int(v)

    return index_system_dict


def reverse_dictionary(dict_var):
    return {v: k for k, v in dict_var.items()}


def predict(test_events, test_set, matrix, outcome, results):
    read_events = pd.read_csv(test_events, sep='\t')
    read_events['cues'] = read_events['cues'].str.strip()
    read_events['outcomes'] = read_events['outcomes'].str.strip()
    read_events.to_csv(test_events, index=False, sep='\t')
    weights = retrieve_weights(matrix)
    test_weights = activation.activation(test_events, weights, number_of_threads=16, remove_duplicates=False,
                                         ignore_missing_cues=False)
    events = pd.read_csv(test_events, sep='\t', na_filter=False, encoding='utf-8')
    test_set = pd.read_csv(test_set, sep=',', na_filter=False, encoding='utf8')
    y_test = events['outcomes'].tolist()
    y_pred = activations_to_predictions(test_weights)
    test_accuracy = accuracy_score(y_test, y_pred)
    print(test_accuracy)
    outcome_to_index = import_index_system(outcome)
    index_to_outcome = reverse_dictionary(outcome_to_index)
    cmat = confusion_matrix(y_test, y_pred, labels=list(outcome_to_index.keys()))  # Confusion matrix
    pmat = cmat.diagonal() / cmat.sum(axis=1)  # Confusion matrix in terms of proportions
    print({index_to_outcome[j + 1]: round(pmat[j], 4) for j in range(len(pmat))})
    results_test = test_set[
        ['Text ID', 'Sentence ID', 'Sentence', 'article', 'noun', 'count', 'number', 'phrase', 'elaboration', 'sr', 'hk']].copy()
    results_test['PredictedArticle'] = y_pred
    results_test['Accuracy'] = results_test.apply(lambda x: int(x.loc['article'] == x.loc['PredictedArticle']), axis=1)
    results_test = results_test.loc[:,
                   ['Text ID', 'Sentence ID', 'Sentence', 'article', 'noun', 'count', 'number', 'phrase', 'elaboration', 'sr',
                    'hk', 'PredictedArticle',
                    'Accuracy']]
    results_null = results_test[results_test.article == '0']
    print('Accuracy for null', (sum(results_null['Accuracy'])/len(results_null)*100))
    results_test.to_csv(results, sep=',', index=False)

