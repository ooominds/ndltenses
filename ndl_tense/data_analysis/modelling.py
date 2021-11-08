### Import necessary packages
import itertools
import csv
import gc
import sys
import numpy as np
import xarray as xr
import pandas as pd
import random
import json
import os
import time
import h5py
import shutil
import ntpath

import keras
from keras.models import Sequential, load_model
from keras.layers import Dropout, Dense, LSTM, Embedding, Flatten
from keras.preprocessing.sequence import pad_sequences
from keras import optimizers
from keras import activations
from keras import losses
from keras import metrics
from keras import backend as K

#import pyndl
from pyndl.preprocess import filter_event_file
from pyndl.count import cues_outcomes
from pyndl.ndl import ndl
from pyndl.activation import activation

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

### Import local packages
from evaluation import recall, precision, f1score
from preprocessing import df_to_gz, IndexedFile, prepare_embedding_matrix, extract_embedding_dim

###############
# Tokenisation
###############

def seq_to_integers_1darray(seq, index_system, N_tokens, max_len = None):

    """Convert a text sequence to a 1d array of integers (used for training with embedding)

    Parameters
    ----------
    seq: str
        string to convert
    index_system: dict
        index system giving the mapping from tokens to indices
    N_tokens: int
        number of allowed tokens (cues or outcomes). This determines the length of the one-hot array
    max_len: int
        Consider only 'max_len' first tokens to in a sequence

    Returns
    -------
    numpy array
        unidimensional array with words replaced by their indices in the input index system
    """

    # List of words in the sentence 
    targets = seq.split('_')

    if max_len: # pad sequences if max_len is given
        target_indices = [[index_system[w] for w in targets if w in index_system]]
        # pad the list of indices
        target_indices = pad_sequences(target_indices, maxlen = max_len, padding = 'post', truncating= 'post')[0]
    else:
        target_indices = np.array([index_system[w] for w in targets if w in index_system])

    return target_indices

def seq_to_onehot_1darray(seq, index_system, N_tokens, max_len = None):

    """Convert a text sequence to a one-hot 1d array (used by FNN)

    Parameters
    ----------
    seq: str
        string to convert
    index_system: dict
        index system giving the mapping from tokens to indices
    N_tokens: int
        number of allowed tokens (cues or outcomes). This determines the length of the one-hot array
    max_len: int
        Consider only 'max_len' first tokens to in a sequence

    Returns
    -------
    numpy array
        one-hot unidimensional array with 0s everywhere except for the indices corresponding to the tokens that appear in the sequence 
    """

    # Initialise the array
    onehot_list = np.zeros(N_tokens + 1)

    # List of words in the sentence 
    targets = seq.split('_')

    if max_len: # pad sequences if max_len is given
        target_indices = [[index_system[w] for w in targets if w in index_system]]
        # pad the list of indices
        target_indices = pad_sequences(target_indices, maxlen = max_len, padding = 'post', truncating= 'post')[0]
    else:
        target_indices = [index_system[w] for w in targets if w in index_system]
    
    onehot_list[target_indices] = 1
    onehot_list = onehot_list[1:]

    return onehot_list

def seq_to_onehot_2darray(seq, index_system, N_tokens, max_len):

    """Convert a text sequence to a one-hot 2d array (used by LSTM)

    Parameters
    ----------
    seq: str
        string to convert (e.g. sequence of cues)
    index_system: dict
        index system giving the mapping from tokens to indices
    N_tokens: int
        number of allowed tokens. This determines the number of columns of the one-hot array
    max_len: int
        Consider only 'max_len' first tokens to in a sequence

    Returns
    -------
    numpy array
        one-hot two-dimensional array with the i-th row giving the one-hot encoding of the i-th token (0s everywhere except for the indices corresponding to the token) 
    """

    # Initialise the array
    onehot_array = np.zeros((max_len, (N_tokens+1)))

    # List of words in the sentence 
    targets = seq.split('_')
    target_indices = [index_system[w] for w in targets if w in index_system]

    # First define the maximum index of word from the current sentence i to be considered
    max_len_cur = min(max_len, len(target_indices)) # Current max_len
    for j in range(max_len_cur):
        onehot_array[j, target_indices[j]] = 1 
    
    # Trim the first column (empty)
    onehot_array = onehot_array[:, 1:]

    return onehot_array
                                         
###############################
# Feedforward neural networks
###############################

class generator_textfile_FNN(keras.utils.Sequence):

    """ Class that generates batches of data ready for training a FNN model. The data is expected to  
    come from an indexed text file and to follow event style (cue and ouctomes seperated by underscores)

    Attributes
    ----------
    data: class
        indexed text file (no heading)
    batch_size: int
        number of examples in each batch 
    num_cues: int
        number of allowed cues
    num_outcomes: int
        number of allowed outcomes
    cue_index: dict
        mapping from cues to indices
    outcome_index: dict
        mapping from outcomes to indices
    max_len: int
        Consider only 'max_len' first tokens in a sequence
    vector_encoding: str
        Whether to use one-hot encoding (='onehot') or embedding (='embedding'). Default: 'onehot'
    shuffle_epoch: Boolean
        whether to shuffle the data after every epoch

    Returns
    -------
    class object
        generator for keras. It inherites from keras.utils.Sequence  
    """

    def __init__(self, data, batch_size, num_cues, num_outcomes, 
                 cue_index, outcome_index, max_len, 
                 vector_encoding = 'onehot', shuffle_epoch = False):
        'Initialization'
        self.data =  data
        self.batch_size = batch_size    
        self.num_cues = num_cues
        self.num_outcomes = num_outcomes
        self.cue_index = cue_index
        self.outcome_index = outcome_index
        self.max_len = max_len
        self.vector_encoding = vector_encoding
        self.shuffle_epoch = shuffle_epoch
        self.on_epoch_end()

    def __len__(self):
        'Denotes the number of batches per epoch'
        return int(np.floor(len(self.data) / self.batch_size))

    def __getitem__(self, index):
        'Generate one batch of data'
        # Generate indices of the batch
        indexes_batch = self.indexes[index*self.batch_size:(index+1)*self.batch_size]
        # Generate data
        X, Y = self.__data_generation(indexes_batch)
        return X, Y

    def on_epoch_end(self):
        'Updates indexes after each epoch'
        self.indexes = np.arange(len(self.data))
        if self.shuffle_epoch == True:
            np.random.shuffle(self.indexes)

    def __data_generation(self, indexes_batch):
        'Generates data containing batch_size samples'

        if self.vector_encoding == 'onehot': # One-hot encoding
            seq_to_vec = seq_to_onehot_1darray
        else: # Embedding
            seq_to_vec = seq_to_integers_1darray

        X_arrays = []
        Y_arrays = []
        for raw_event in self.data[indexes_batch]:
            # extract the cues and outcomes sequences
            cue_seq, outcome_seq = raw_event.strip().split('\t')
            cues_onehot = seq_to_vec(cue_seq, self.cue_index, self.num_cues)
            outcomes_onehot = seq_to_onehot_1darray(outcome_seq, self.outcome_index, self.num_outcomes)
            X_arrays.append(cues_onehot)
            Y_arrays.append(outcomes_onehot)
        X =  np.stack(X_arrays, axis = 0)
        Y =  np.stack(Y_arrays, axis = 0)

        # Generate data
        return X, Y

class generator_df_FNN(keras.utils.Sequence):

    """ Class that generates batches of data ready for training a FNN model. The data is expected to  
    come from a dataframe and to follow event style (cue and ouctomes seperated by underscores)

    Attributes
    ----------
    data: dataframe
        dataframe with the first column containing the cues and second colum containing the outcomes
    batch_size: int
        number of examples in each batch 
    num_cues: int
        number of allowed cues
    num_outcomes: int
        number of allowed outcomes
    cue_index: dict
        mapping from cues to indices
    outcome_index: dict
        mapping from outcomes to indices
    max_len: int
        Consider only 'max_len' first tokens in a sequence
    vector_encoding: str
        Whether to use one-hot encoding (='onehot') or embedding (='embedding'). Default: 'onehot'
    shuffle_epoch: Boolean
        whether to shuffle the data after every epoch. Default: False

    Returns
    -------
    class object
        generator for keras. It inherites from keras.utils.Sequence  
    """

    def __init__(self, data, batch_size, num_cues, num_outcomes, 
                 cue_index, outcome_index, max_len, 
                 vector_encoding = 'onehot', shuffle_epoch = False):
        'Initialization'
        self.data =  data
        self.batch_size = batch_size    
        self.num_cues = num_cues
        self.num_outcomes = num_outcomes
        self.cue_index = cue_index
        self.outcome_index = outcome_index
        self.max_len = max_len
        self.vector_encoding = vector_encoding
        self.shuffle_epoch = shuffle_epoch
        self.on_epoch_end()
        
    def __len__(self):
        'Denotes the number of batches per epoch'
        return int(np.floor(len(self.data) / self.batch_size))

    def __getitem__(self, index):
        'Generate one batch of data'
        # Generate indices of the batch
        indexes_batch = self.indexes[index*self.batch_size:(index+1)*self.batch_size]
        # Generate data
        X, Y = self.__data_generation(indexes_batch)
        return X, Y

    def on_epoch_end(self):
        'Updates indexes after each epoch'
        self.indexes = np.arange(len(self.data))
        if self.shuffle_epoch == True:
            np.random.shuffle(self.indexes)

    def __data_generation(self, indexes_batch):
        'Generates data containing batch_size samples' 
        if self.vector_encoding == 'onehot': # One-hot encoding
            seq_to_vec = seq_to_onehot_1darray
        else: # Embedding
            seq_to_vec = seq_to_integers_1darray
        X_arrays = [seq_to_vec(cue_seq, self.cue_index, self.num_cues, self.max_len) for cue_seq in self.data.loc[self.data.index[indexes_batch], 'cues']]
        Y_arrays = [seq_to_onehot_1darray(outcome_seq, self.outcome_index, self.num_outcomes) for outcome_seq in self.data.loc[self.data.index[indexes_batch], 'outcomes']]
        X =  np.stack(X_arrays, axis=0)
        Y =  np.stack(Y_arrays, axis=0)

        # Generate data
        return X, Y

def train_FNN(data_train, data_valid, cue_index, outcome_index, 
              shuffle_epoch = False, num_threads = 1, verbose = 1,
              metrics = ['accuracy', 'precision', 'recall', 'f1score'],
              params = {'max_len': None,
                        'embedding_input': None,
                        'embedding_dim': None,
                        'epochs': 1, # number of iterations on the full set 
                        'batch_size': 128, 
                        'hidden_layers': 0, # number of hidden layers 
                        'hidden_neuron':64, # number of neurons in the input layer 
                        'lr': 0.0001, # learning rate       
                        'dropout': 0, 
                        'optimizer': optimizers.Adam, 
                        'losses': losses.binary_crossentropy, 
                        'activation': activations.relu, 
                        'last_activation': 'sigmoid'}):

    """ Train a feedforward neural network

    Parameters
    ----------
    data_train: dataframe or class
        dataframe, path to a '.gz' event file or indexed text file containing training data
    data_valid: class or dataframe
        dataframe, path to a '.gz' event file or indexed text file containing validation data
    cue_index: dict
        mapping from cues to indices. The dictionary should include only the cues to keep in the data
    outcome_index: dict
        mapping from outcomes to indices. The dictionary should include only the outcomes to keep in the data
    shuffle_epoch: Boolean
        whether to shuffle the data after every epoch
    num_threads: int
        maximum number of processes to use - it should be >= 1. Default: 1
    verbose: int (0, 1, or 2)
        verbosity mode. 0 = silent, 1 = one line per epoch, 2 = detailed. Default: 1
    metrics: list
    params: dict
        model parameters:
        'max_len': int or None
            Consider only 'max_len' first tokens in a cue sequence. If None then all cues are taken into account, 
            but None can only be chosen if trained with one-hot encoding. Default: None   
        'embedding_input': str, numpy matrix or None
            There are 4 possible choices: (1) if embedding_input = 'learn', learn embedding vectors from scratch while 
            training the model. An embedding layer will be added to the network; (2) if embedding_input = 'path', 
            extract embedding vectors from an embedding text file given in 'path' (it is imporant that it is a 
            text file); (3) Use an already prepared embedding matrix for training - use 
            prepare_embedding_matrix() from the preprocessing module to prepare one. (4) embedding_input = None, 
            one-hot encoding is used. Default: None
        'embedding_dim': int or None
            Length of the cue embedding vectors. Default: None
        'epochs': int
            Number of passes through the entire training dataset that has to be completed. Default: 1
        'batch_size': int
            Number of training examples to use for each update
        'hidden_layers': int
            Number of hidden layers
        'hidden_neuron': int
            Number of neurons in the LSTM layer
        'lr': float
            Learning rate
        'dropout': float
            Dropout in the LSTM layer
        'optimizer': class
            Keras optimizer function
        'losses': func
            Keras loss function
        'activation': func
            Keras activation in each layer
        'last_activation': str
            Keras activation in the output layer

    Returns
    -------
    tuple
        keras fit history and model objects  
    """  
    
    ### check verbose and convert to keras verbose
    if verbose == 0:
        verbose_k = 0
    elif verbose in (1, 2):
        verbose_k = 2
    else:
        raise ValueError("incorrect verbose value: choose an integer bewteen 0 and 2")

    if verbose == 2:
        _ = sys.stdout.write('\n*** Model compilation\n\n')  
        sys.stdout.flush()

    start_compile = time.time()

    ### Extract number of cues and outcomes from the index systems
    num_cues = len(cue_index)
    num_outcomes = len(outcome_index)

    ### Select the appropriate model generator based on the type of data
    # Training data
    if isinstance(data_train, pd.DataFrame):     
        generator_train = generator_df_FNN
    elif isinstance(data_train, IndexedFile):
        generator_train = generator_textfile_FNN
    elif isinstance(data_train, str):
        data_train = IndexedFile(data_train, 'gz')
        generator_train = generator_textfile_FNN
    else:
        raise ValueError("data_train should be either a path to an event file, a dataframe or an indexed text file")
    # Validation data
    if isinstance(data_valid, pd.DataFrame):     
        generator_valid = generator_df_FNN
    elif isinstance(data_valid, IndexedFile):
        generator_valid = generator_textfile_FNN
    elif isinstance(data_valid, str):
        data_valid = IndexedFile(data_valid, 'gz')
        generator_valid = generator_textfile_FNN
    else:
        raise ValueError("data_valid should be either a path to an event file, a dataframe or an indexed text file")

    # Convert the metric list to a list that can be understood by the FNN model
    for i, m in enumerate(metrics):
        if m == 'precision':
            metrics[i] = precision
        elif m == 'recall':
            metrics[i] = recall
        elif m == 'f1score':
            metrics[i] = f1score
    
    # Extract from the params dict the parameters that are used repeatedly to reduce run time
    max_len = params['max_len']
    batch_size = params['batch_size']

    ### Initialise the model
    model = Sequential()  

    ### Add embedding layer if requested + decide vector encoding type
    if not params['embedding_input']:
        vector_encoding_0 = 'onehot'
    else:
        if not max_len:
            raise ValueError("'max_len' cannot be None: 'max_len' has to be specified when training a model with embeddings")

        vector_encoding_0 = 'embedding'
        if params['embedding_input'] == 'learn':
            model.add(Embedding(num_cues+1, params['embedding_dim'], input_length = max_len))
        elif isinstance(params['embedding_input'], str) and not params['embedding_input'] == 'learn': # if pre-trained embedding provided
            params['embedding_dim'] = extract_embedding_dim(params['embedding_input']) # Extract embedding dimension
            embedding_mat = prepare_embedding_matrix(params['embedding_input'], cue_index)
            model.add(Embedding(num_cues+1, params['embedding_dim'], input_length = max_len, 
                                weights = [embedding_mat], trainable = False)) 
        elif isinstance(params['embedding_input'], np.ndarray):
            params['embedding_dim'] = extract_embedding_dim(params['embedding_input']) # Extract embedding dimension
            model.add(Embedding(num_cues+1, params['embedding_dim'], input_length = max_len, 
                                weights = [params['embedding_input']], trainable = False))
        model.add(Flatten())

    ### Add other layers depending on the parameter 'hidden_layers'

    # If there is no hidden layer add the output layer directly
    if params['hidden_layers'] == 0:
        # Output layer
        model.add(Dense(num_outcomes, 
                        input_dim = num_cues,
                        activation = params['last_activation']))
    # If there are hidden layers
    else:
        # First hidden layer   
        model.add(Dense(params['hidden_neuron'],
                        input_dim = num_cues,
                        activation = params['activation']))
        # Add drop out
        model.add(Dropout(params['dropout']))

        # Add more hidden layers if they were requested 
        if params['hidden_layers'] > 1:
            
            for j in range(2, (params['hidden_layers']+1)):
                # Add jth hidden layer
                model.add(Dense(params['hidden_neuron'],
                                activation = params['activation']))  
                # Add drop out
                model.add(Dropout(params['dropout']))
            
        # Add output layer
        model.add(Dense(num_outcomes, 
                        activation = params['last_activation'])) 
  
    ### Compile the model 
    model.compile(loss = params['losses'],
                  optimizer = params['optimizer'](lr = params['lr']),
                  metrics = metrics)

    if verbose == 2:
        _ = sys.stdout.write('Model compilation completed in %.1fs\n\n' \
                             % (time.time() - start_compile))

        _ = sys.stdout.write('*** Model fitting\n\n')    
        sys.stdout.flush()    

    start_fit = time.time()

    ### Initiate the generators for the train and valid data
    train_gen = generator_train(data = data_train, 
                                batch_size = batch_size,
                                num_cues = num_cues,
                                num_outcomes = num_outcomes,
                                cue_index = cue_index,
                                outcome_index = outcome_index,
                                max_len = max_len,
                                vector_encoding = vector_encoding_0,
                                shuffle_epoch = shuffle_epoch)
    valid_gen = generator_valid(data = data_valid, 
                                batch_size = batch_size,
                                num_cues = num_cues,
                                num_outcomes = num_outcomes,
                                cue_index = cue_index,
                                outcome_index = outcome_index,
                                max_len = max_len,
                                vector_encoding = vector_encoding_0,
                                shuffle_epoch = shuffle_epoch)
    
    # Fit the model
    # No parallel processing if the inputs are text files (still need to be sorted out)
    if isinstance(data_train, pd.DataFrame) and isinstance(data_valid, pd.DataFrame): 
        out = model.fit_generator(generator = train_gen,
                                  validation_data = valid_gen,
                                  epochs = params['epochs'],
                                  use_multiprocessing = True,
                                  verbose = verbose_k,
                                  workers = num_threads-1)
    else:
        out = model.fit_generator(generator = train_gen,
                                  validation_data = valid_gen,
                                  epochs = params['epochs'],
                                  use_multiprocessing = False,
                                  verbose = verbose_k,
                                  workers = 0)
    hist = out.history

    if verbose == 2:
        _ = sys.stdout.write('\nModel fitting completed in %.0fs\n' \
                             % (time.time() - start_fit))
        sys.stdout.flush()
    
    return hist, model

def grid_search_FNN(data_train, data_valid, cue_index, outcome_index, 
                    params, prop_grid, tuning_output_file,         
                    shuffle_epoch = False, shuffle_grid = True, 
                    num_threads = 1, seed = None, verbose = 1):

    """ Grid search for feedforward neural networks

    Parameters
    ----------
    data_train: dataframe or class
        dataframe, path to a '.gz' event file or indexed text file containing training data
    data_valid: class or dataframe
        dataframe, path to a '.gz' event file or indexed text file containing validation data
    cue_index: dict
        mapping from cues to indices. The dictionary should include only the cues to keep in the data
    outcome_index: dict
        mapping from outcomes to indices. The dictionary should include only the outcomes to keep in the data
    params: dict
        model parameters:
        'max_len': int
            Consider only 'max_len' first tokens in a cue sequence. Default: 10   
        'embedding_input': str, numpy matrix or None
            There are 3 possible choices: (1) if embedding_input = 'learn', learn embedding vectors from scratch while 
            training the model. An embedding layer will be added to the network; (2) if embedding_input = 'path', 
            extract embedding vectors from an embedding text file given in 'path' (it is imporant that it is a 
            text file); (3) Use the already prepared embedding matrix for training. You can use 
            prepare_embedding_matrix() from the preprocessing module. Default: None
        'embedding_dim': int or None
            Length of the cue embedding vectors. Default:None
        'epochs': int
            Number of passes through the entire training dataset that has to be completed. Default: 1
        'batch_size': int
            Number of training examples to use for each update
        'hidden_layers': int
            Number of hidden layers
        'hidden_neuron': int
            Number of neurons in the LSTM layer
        'lr': float
            Learning rate
        'dropout': float
            Dropout in the LSTM layer
        'optimizer': class
            Keras optimizer function
        'losses': func
            Keras loss function
        'activation': func
            Keras activation in each layer
        'last_activation': str
            Keras activation in the output layer
    prop_grid: float
        proportion of the grid combinations to sample 
    tuning_output_file: str
        path of the csv file where the grid search results will be stored
    shuffle_epoch: Boolean
        whether to shuffle the data after every epoch. Default: False
    shuffle_grid: Boolean
        whether to shuffle the parameter grid or respect the same order of parameters. Default: True
        provided in `params'
    num_threads: int
        maximum number of processes to use - it should be >= 1. Default: 1
    seed : int or None
        random seed to initialise the pseudorandom number generator (for selecting the parameter 
        combinations to cover). Use it if you want to have replicable results. Default: None
    verbose: int (0, 1, or 2)
        verbosity mode. 0 = silent, 1 = one line per parameter combination, 2 = detailed. Default: 1

    Returns
    -------
    None
        save csv files
    """
    
    ### check verbose and convert to train()'s verbose
    if verbose in (0, 1):
        verbose_t = 0
    elif verbose == 2:
        verbose_t = 2
    else:
        raise ValueError("incorrect verbose value: choose an integer bewteen 0 and 2")
    
    ### Select the appropriate model generator based on the type of data
    # Training data
    if ((not isinstance(data_train, pd.DataFrame)) and 
        (not isinstance(data_train, IndexedFile)) and 
        (not isinstance(data_train, str))):
        raise ValueError("data_train should be either a path to an event file, a dataframe or an indexed text file")
    # Validation data
    if ((not isinstance(data_train, pd.DataFrame)) and 
        (not isinstance(data_train, IndexedFile)) and 
        (not isinstance(data_train, str))):
        raise ValueError("data_valid should be either a path to an event file, a dataframe or an indexed text file")

    # Extract the dimensions of the pretrained embeddings
    pretrain_embed_dim = {}
    embed_inputs = params['embedding_input']
    for i, e in enumerate(embed_inputs):
        if embed_inputs[i] and embed_inputs[i] != 'learn':
            pretrain_embed_dim.update({embed_inputs[i]:extract_embedding_dim(embed_inputs[i])})

    # Create a list of dictionaries giving all possible parameter combinations
    keys, values = zip(*params.items())
    grid_full = [dict(zip(keys, v)) for v in itertools.product(*values)]

    ### Remove impossible combinations
    ind_to_remove = []
    for i,d in enumerate(grid_full):
        # In the case of no hidden layer, no need to set the 'activation' parameter - only 'last_activation' is used
        if grid_full[i]['hidden_layers'] == 0:
            grid_full[i]['activation'] = None
        # In the case of hot encoding or pretrained embedding, no need to set embedding_dim, otherwise,
        # it is essential to set embedding_dim, so remove all cases where embedding_dim is not given with
        # embeddings to be learned from scratch
        if not grid_full[i]['embedding_input']:
            grid_full[i]['embedding_dim'] = None
        elif grid_full[i]['embedding_input'] == 'learn' and not grid_full[i]['embedding_dim']:
            ind_to_remove.append(i) 
        elif grid_full[i]['embedding_input'] and grid_full[i]['embedding_input'] != 'learn':
            grid_full[i]['embedding_dim'] = pretrain_embed_dim[grid_full[i]['embedding_input']]
        # In the case of embeddings, it is essential to set 'max_len' (max_len cannot be None),
        # so remove all cases where embeddings are used max_len is not given
        if grid_full[i]['embedding_input'] and not grid_full[i]['max_len']:
            ind_to_remove.append(i) 
            
    # First remove the detected impossible combinations (e.g. 'embedding_input = 'learn', embedding_dim = None') 
    for ii in sorted(ind_to_remove, reverse = True):
        del grid_full[ii]
    # Second remove the duplicated combinations 'embedding_input != 'learn', embedding_dim = None' 
    grid_full = [dict(t) for t in {tuple(d.items()) for d in grid_full}]   
    
    # shuffle the list of params
    if shuffle_grid:
        random.Random(seed).shuffle(grid_full)

    # Select the combinations to use 
    N_comb = round(prop_grid * len(grid_full)) 
    grid_select = grid_full[:N_comb]

    # Create a list of lists which stores all parameter combinations that are covered so far in the grid search 
    param_comb_sofar = []

    ### Write to the csv file that encodes the results
    with open(tuning_output_file, mode = 'w', newline = '\n') as o:
        csv_writer = csv.writer(o, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        heading = list(params.keys())
        heading.extend(['loss', 'acc', 'precision', 'recall', 'f1score', 
                        'val_loss', 'val_acc', 'val_precision', 'val_recall', 'val_f1score'])
        csv_writer.writerow(heading)

        ### Run the experiments
        for i, param_comb in enumerate(grid_select):

            start = time.time()

            # Message at the start of each iteration
            if verbose != 0:
                _ = sys.stdout.write('\n********************************** Iteration %d out of %d **********************************\n\n' % ((i+1), len(grid_select)))
                _ = sys.stdout.write('*** Parameter combination \n\n') 
                _ = sys.stdout.write('%s\n' % (param_comb))
                sys.stdout.flush()

            # this will contain the values that will be recorded in each row. 
            # We start by copying the parameter values
            row_values = list(param_comb.values())

            # Check if the current parameter combination has already been processed in the grid search
            if row_values in param_comb_sofar:
                if verbose != 0:
                    _ = sys.stdout.write('\nThis parameter combination was skipped because it has already been processed\n')
                    sys.stdout.flush()

            else:
                # Fit the model given the current param combination
                hist, model = train_FNN(data_train = data_train, 
                                        data_valid = data_valid, 
                                        cue_index = cue_index, 
                                        outcome_index = outcome_index, 
                                        shuffle_epoch = shuffle_epoch, 
                                        num_threads = num_threads, 
                                        verbose = verbose_t,
                                        metrics = ['accuracy', 'precision', 'recall', 'f1score'],
                                        params = param_comb)

                # Get index of epochs and extract embedding name from the 'param_comb' dictionary
                for ind, (k, v) in enumerate(param_comb.items()):
                    if k == 'epochs':
                        i_epochs = ind
                    elif (k == 'embedding_input') and isinstance(v, str) and (v != 'learn'):
                        # Extract the name of embedding from the path
                        row_values[ind] = ntpath.basename(v)[:-4]
                    elif (k == 'embedding_input') and not v:
                        row_values[ind] = 'onehot' 
                    elif (k == 'embedding_dim') and not v:
                        row_values[ind] = 0 
                    elif (k == 'activation') and not v:
                        row_values[ind] = 'none' 

                ### Export the results to a csv file
                for j in range(param_comb['epochs']):
                    
                    # Copy the parameter values to current param combination variables
                    row_values_j = row_values.copy()

                    # correct the epoch num
                    row_values_j[i_epochs] = j+1 

                    # Add the derived combination to the list of all parameter combinations
                    param_comb_sofar.append(row_values_j.copy()) 
                    
                    # Add the performance scores
                    # training
                    loss_j = hist['loss'][j]
                    acc_j = hist['accuracy'][j]
                    precision_j = hist['precision'][j]
                    recall_j = hist['recall'][j]            
                    f1score_j = hist['f1score'][j]
                    # validation
                    val_loss_j = hist['val_loss'][j]
                    val_acc_j = hist['val_accuracy'][j]
                    val_precision_j = hist['val_precision'][j]
                    val_recall_j = hist['val_recall'][j]            
                    val_f1score_j = hist['val_f1score'][j]
                    row_values_j.extend([loss_j, acc_j, precision_j, recall_j, f1score_j, 
                                         val_loss_j, val_acc_j, val_precision_j, val_recall_j, val_f1score_j])
                    # Write the row
                    csv_writer.writerow(row_values_j)
                    o.flush()

                if verbose == 1:
                    sys.stdout.write('\nIteration completed in %.0fs\n' % ((time.time() - start)))
                    sys.stdout.flush()

                # Clear memory           
                del model, hist
                gc.collect()
                K.clear_session()

        if verbose != 0:
            _ = sys.stdout.write('\n********************************************************************************************\n')
            sys.stdout.flush()

########
# LSTM
########

class generator_textfile_LSTM(keras.utils.Sequence):

    """ Class that generates batches of data ready for training an LSTM model. The data is expected to  
    be event style (cue and ouctomes seperated by underscores)

    Attributes
    ----------
    data: class
        indexed text file
    batch_size: int
        number of examples in each batch 
    num_cues: int
        number of allowed cues
    num_outcomes: int
        number of allowed outcomes
    cue_index: dict
        mapping from cues to indices
    outcome_index: dict
        mapping from outcomes to indices
    max_len: int
        Consider only 'max_len' first tokens in a sequence
    vector_encoding: str
        Whether to use one-hot encoding (='onehot') or embedding (='embedding'). Default: 'onehot'
    shuffle_epoch: Boolean
        whether to shuffle the data after every epoch

    Returns
    -------
    class object
        generator for keras. It inherites from keras.utils.Sequence  
    """

    def __init__(self, data, batch_size, num_cues, num_outcomes, 
                 cue_index, outcome_index, max_len, 
                 vector_encoding = 'onehot', shuffle_epoch = False):
        'Initialization'
        self.data =  data
        self.batch_size = batch_size    
        self.num_cues = num_cues
        self.num_outcomes = num_outcomes
        self.cue_index = cue_index
        self.outcome_index = outcome_index
        self.max_len = max_len
        self.vector_encoding = vector_encoding
        self.shuffle_epoch = shuffle_epoch
        self.on_epoch_end()

    def __len__(self):
        'Denotes the number of batches per epoch'
        return int(np.floor(len(self.data) / self.batch_size))

    def __getitem__(self, index):
        'Generate one batch of data'
        # Generate indices of the batch
        indexes_batch = self.indexes[index*self.batch_size:(index+1)*self.batch_size]
        # Generate data
        X, Y = self.__data_generation(indexes_batch)
        return X, Y

    def on_epoch_end(self):
        'Updates indexes after each epoch'
        self.indexes = np.arange(len(self.data))
        if self.shuffle_epoch == True:
            np.random.shuffle(self.indexes)

    def __data_generation(self, indexes_batch):
        'Generates data containing batch_size samples'

        if self.vector_encoding == 'onehot': # One-hot encoding
            seq_to_vec = seq_to_onehot_2darray
        else: # Embedding
            seq_to_vec = seq_to_integers_1darray

        X_arrays = []
        Y_arrays = []
        for raw_event in self.data[indexes_batch]:
            # extract the cues and outcomes sequences
            cue_seq, outcome_seq = raw_event.strip().split('\t')
            cues_onehot = seq_to_vec(cue_seq, self.cue_index, self.num_cues, self.max_len)
            outcomes_onehot = seq_to_onehot_1darray(outcome_seq, self.outcome_index, self.num_outcomes)
            X_arrays.append(cues_onehot)
            Y_arrays.append(outcomes_onehot)
        X =  np.stack(X_arrays, axis = 0)
        Y =  np.stack(Y_arrays, axis = 0)

        # Generate data
        return X, Y

class generator_df_LSTM(keras.utils.Sequence):

    """ Class that generates batches of data ready for training an LSTM model. The data is expected to  
    come from a dataframe and to follow event style (cue and ouctomes seperated by underscores)

    Attributes
    ----------
    data: dataframe
        dataframe with the first column containing the cues and second colum containing the outcomes
    batch_size: int
        number of examples in each batch 
    num_cues: int
        number of allowed cues
    num_outcomes: int
        number of allowed outcomes
    cue_index: dict
        mapping from cues to indices
    outcome_index: dict
        mapping from outcomes to indices
    max_len: int
        Consider only 'max_len' first tokens in a sequence
    vector_encoding: str
        Whether to use one-hot encoding (='onehot') or embedding (='embedding'). Default: 'onehot'
    shuffle_epoch: Boolean
        whether to shuffle the data after every epoch

    Returns
    -------
    class object
        generator for keras. It inherites from keras.utils.Sequence  
    """

    def __init__(self, data, batch_size, num_cues, num_outcomes, 
                 cue_index, outcome_index, max_len, 
                 vector_encoding = 'onehot', shuffle_epoch = False):
        'Initialization'
        self.data =  data
        self.batch_size = batch_size    
        self.num_cues = num_cues
        self.num_outcomes = num_outcomes
        self.cue_index = cue_index
        self.outcome_index = outcome_index
        self.max_len = max_len
        self.vector_encoding = vector_encoding
        self.shuffle_epoch = shuffle_epoch
        self.on_epoch_end()

    def __len__(self):
        'Denotes the number of batches per epoch'
        return int(np.floor(len(self.data) / self.batch_size))

    def __getitem__(self, index):
        'Generate one batch of data'
        # Generate indices of the batch
        indexes_batch = self.indexes[index*self.batch_size:(index+1)*self.batch_size]
        # Generate data
        X, Y = self.__data_generation(indexes_batch)
        return X, Y

    def on_epoch_end(self):
        'Updates indexes after each epoch'
        self.indexes = np.arange(len(self.data))
        if self.shuffle_epoch == True:
            np.random.shuffle(self.indexes)

    def __data_generation(self, indexes_batch):
        'Generates data containing batch_size samples' # X : (batch_size, *dim, n_channels)
        if self.vector_encoding == 'onehot': # One-hot encoding
            seq_to_vec = seq_to_onehot_2darray
        else: # Embedding
            seq_to_vec = seq_to_integers_1darray
        X_arrays = [seq_to_vec(cue_seq, self.cue_index, self.num_cues, self.max_len) for cue_seq in self.data.loc[self.data.index[indexes_batch], 'cues']]
        Y_arrays = [seq_to_onehot_1darray(outcome_seq, self.outcome_index, self.num_outcomes) for outcome_seq in self.data.loc[self.data.index[indexes_batch], 'outcomes']]
        Y =  np.stack(Y_arrays, axis=0)
        X =  np.stack(X_arrays, axis=0)

        # Generate data
        return X, Y

def train_LSTM(data_train, data_valid, cue_index, outcome_index,
               shuffle_epoch = False, num_threads = 1, verbose = 1,
               metrics = ['accuracy', 'precision', 'recall', 'f1score'],
               params = {'max_len': 10,
                         'embedding_input': None,
                         'embedding_dim': None,
                         'epochs': 1, # number of iterations on the full set 
                         'batch_size': 128, 
                         'hidden_neuron':64, # number of neurons in the input layer 
                         'lr': 0.0001, # learning rate       
                         'dropout': 0, 
                         'optimizer': optimizers.RMSprop, 
                         'losses': losses.binary_crossentropy, 
                         'last_activation': 'sigmoid'}):

    """ Train an LSTM

    Parameters
    ----------
    data_train: dataframe or class
        dataframe, path to a '.gz' event file or indexed text file containing training data
    data_valid: class or dataframe
        dataframe, path to a '.gz' event file or indexed text file containing validation data
    cue_index: dict
        mapping from cues to indices. The dictionary should include only the cues to keep in the data
    outcome_index: dict
        mapping from outcomes to indices. The dictionary should include only the outcomes to keep in the data
    shuffle_epoch: Boolean
        whether to shuffle the data after every epoch
    num_threads: int
        maximum number of processes to use - it should be >= 1. Default: 1
    verbose: int (0, 1, or 2)
        verbosity mode. 0 = silent, 1 = one line per epoch, 2 = detailed. Default: 1
    metrics: list
    params: dict
        model parameters:
        'max_len': int
            Consider only 'max_len' first tokens in a cue sequence. Default: 10 
        'embedding_input': str, numpy matrix or None
            There are 3 possible choices: (1) if embedding_input = 'learn', learn embedding vectors from scratch while 
            training the model. An embedding layer will be added to the network; (2) if embedding_input = 'path', 
            extract embedding vectors from an embedding text file given in 'path' (it is imporant that it is a 
            text file); (3) Use the already prepared embedding matrix for training. You can use 
            prepare_embedding_matrix() from the preprocessing module. Default: None
        'embedding_dim': int or None
            Length of the cue embedding vectors. Default: 50
        'epochs': int
            Number of passes through the entire training dataset that has to be completed. Default: 1
        'batch_size': int
            Number of training examples to use for each update
        'hidden_neuron': int
            Number of neurons in the LSTM layer
        'lr': float
            Learning rate
        'dropout': float
            Dropout in the LSTM layer
        'optimizer': class
            Keras optimizer function
        'losses': func
            Keras loss function
        'last_activation': str
            Keras activation in the output layer

    Returns
    -------
    tuple
        keras fit history and model objects  
    """

    ### check verbose and convert to keras verbose
    if verbose == 0:
        verbose_k = 0
    elif verbose in (1, 2):
        verbose_k = 2
    else:
        raise ValueError("incorrect verbose value: choose an integer bewteen 0 and 2")

    if verbose ==2:
        _ = sys.stdout.write('\n*** Model compilation\n\n')  
        sys.stdout.flush()

    start_compile = time.time()

    ### Extract number of cues and outcomes from the index systems
    num_cues = len(cue_index)
    num_outcomes = len(outcome_index)

    ### Select the appropriate model generator based on the type of data
    # Training data
    if isinstance(data_train, pd.DataFrame):     
        generator_train = generator_df_LSTM
    elif isinstance(data_train, IndexedFile):
        generator_train = generator_textfile_LSTM
    elif isinstance(data_train, str):
        data_train = IndexedFile(data_train, 'gz')
        generator_train = generator_textfile_LSTM
    else:
        raise ValueError("data_train should be either a path to an event file, a dataframe or an indexed text file")
    # Validation data
    if isinstance(data_valid, pd.DataFrame):     
        generator_valid = generator_df_LSTM
    elif isinstance(data_valid, IndexedFile):
        generator_valid = generator_textfile_LSTM
    elif isinstance(data_valid, str):
        data_valid = IndexedFile(data_valid, 'gz')
        generator_valid = generator_textfile_LSTM
    else:
        raise ValueError("data_valid should be either a path to an event file, a dataframe or an indexed text file")

    # Convert the metric list to a list that can be understood by the FNN model
    for i, m in enumerate(metrics):
        if m == 'precision':
            metrics[i] = precision
        elif m == 'recall':
            metrics[i] = recall
        elif m == 'f1score':
            metrics[i] = f1score

    # Extract from the params dict the parameters that are used repeatedly to reduce run time
    max_len = params['max_len']
    batch_size = params['batch_size']

    ### Initialise the model
    model = Sequential()  

    ### Add embedding layer if requested + decide vector encoding type
    if not params['embedding_input']:
        vector_encoding_0 = 'onehot'
    else:
        vector_encoding_0 = 'embedding'
        if params['embedding_input'] == 'learn':
            model.add(Embedding(num_cues+1, params['embedding_dim'], input_length = max_len))
        elif isinstance(params['embedding_input'], str) and not params['embedding_input'] == 'learn': # if pre-trained embedding provided
            params['embedding_dim'] = extract_embedding_dim(params['embedding_input']) # Extract embedding dimension
            embedding_mat = prepare_embedding_matrix(params['embedding_input'], cue_index)
            model.add(Embedding(num_cues+1, params['embedding_dim'], input_length = max_len, 
                                weights = [embedding_mat], trainable = False)) 
        elif isinstance(params['embedding_input'], np.ndarray):
            params['embedding_dim'] = extract_embedding_dim(params['embedding_input']) # Extract embedding dimension
            model.add(Embedding(num_cues+1, params['embedding_dim'], input_length = max_len, 
                                weights = [params['embedding_input']], trainable = False))

    # LSTM layer 
    model.add(LSTM(params['hidden_neuron'], return_sequences = False, input_shape = (max_len, num_cues))) 

    # Add drop out
    model.add(Dropout(params['dropout']))

    # Add output layer
    model.add(Dense(num_outcomes, 
                    activation = params['last_activation']))

    # Compile the model
    model.compile(loss = params['losses'],
                  optimizer = params['optimizer'](lr = params['lr']),
                  metrics = metrics)

    if verbose ==2:
        _ = sys.stdout.write('Model compilation completed in %.1fs\n\n' \
                             % (time.time() - start_compile))

        _ = sys.stdout.write('*** Model fitting\n\n')    
        sys.stdout.flush()    

    start_fit = time.time()

    ### Initiate the generators for the train, valid and test data
    train_gen = generator_train(data = data_train, 
                                batch_size = batch_size,
                                num_cues = num_cues,
                                num_outcomes = num_outcomes,
                                cue_index = cue_index,
                                outcome_index = outcome_index,
                                max_len = max_len,
                                vector_encoding = vector_encoding_0,
                                shuffle_epoch = shuffle_epoch)
    valid_gen = generator_valid(data = data_valid, 
                                batch_size = batch_size,
                                num_cues = num_cues,
                                num_outcomes = num_outcomes,
                                cue_index = cue_index,
                                outcome_index = outcome_index,
                                max_len = max_len,
                                vector_encoding = vector_encoding_0,
                                shuffle_epoch = shuffle_epoch)

    # Fit the model 
    # No parallel processing if the inputs are text files (still need to be sorted out)
    if isinstance(data_train, pd.DataFrame) and isinstance(data_valid, pd.DataFrame):
        out = model.fit_generator(generator = train_gen,
                                  validation_data = valid_gen,
                                  epochs = params['epochs'],
                                  use_multiprocessing = True,
                                  verbose = verbose_k,
                                  workers = num_threads-1)
    else:
        out = model.fit_generator(generator = train_gen,
                                  validation_data = valid_gen,
                                  epochs = params['epochs'],
                                  use_multiprocessing = False,
                                  verbose = verbose_k,
                                  workers = 0)
    hist = out.history   

    if verbose == 2:
        _ = sys.stdout.write('\nModel fitting completed in %.0fs\n' \
                             % (time.time() - start_fit))
        sys.stdout.flush() 

    return hist, model
 
def grid_search_LSTM(data_train, data_valid, cue_index, outcome_index,
                     params, prop_grid, tuning_output_file, shuffle_epoch = False, 
                     shuffle_grid = True, num_threads = 1, seed = None, verbose = 1):

    """ Grid search for LSTM

    Parameters
    ----------
    data_train: dataframe or class
        dataframe, path to a '.gz' event file or indexed text file containing training data
    data_valid: class or dataframe
        dataframe, path to a '.gz' event file or indexed text file containing validation data
    cue_index: dict
        mapping from cues to indices. The dictionary should include only the cues to keep in the data
    outcome_index: dict
        mapping from outcomes to indices. The dictionary should include only the outcomes to keep in the data
    params: dict
        model parameters:
        'max_len': int
            Consider only 'max_len' first tokens in a cue sequence. Default: 10 
        'embedding_input': str, numpy matrix or None
            There are 3 possible choices: (1) if embedding_input = 'learn', learn embedding vectors from scratch while 
            training the model. An embedding layer will be added to the network; (2) if embedding_input = 'path', 
            extract embedding vectors from an embedding text file given in 'path' (it is imporant that it is a 
            text file); (3) Use the already prepared embedding matrix for training. You can use 
            prepare_embedding_matrix() from the preprocessing module. Default: None
        'embedding_dim': int or None
            Length of the cue embedding vectors. Default: 50
        'epochs': int
            Number of passes through the entire training dataset that has to be completed. Default: 1
        'batch_size': int
            Number of training examples to use for each update
        'hidden_neuron': int
            Number of neurons in the LSTM layer
        'lr': float
            Learning rate
        'dropout': float
            Dropout in the LSTM layer
        'optimizer': class
            Keras optimizer function
        'losses': func
            Keras loss function
        'last_activation': str
            Keras activation in the output layer
    prop_grid: float
        proportion of the grid combinations to sample 
    tuning_output_file: str
        path of the csv file where the grid search results will be stored
    shuffle_epoch: Boolean
        whether to shuffle the data after every epoch. Default: False
    shuffle_grid: Boolean
        whether to shuffle the parameter grid or respect the same order of parameters. Default: True
        provided in `params'
    num_threads: int
        maximum number of processes to use - it should be >= 1. Default: 1
    seed : int or None
        random seed to initialise the pseudorandom number generator (for selecting the parameter 
        combinations to cover). Use it if you want to have replicable results. Default: None
    verbose: int (0, 1, or 2)
        verbosity mode. 0 = silent, 1 = one line per parameter combination, 2 = detailed. Default: 1

    Returns
    -------
    None
        save csv files
    """

    ### check verbose and convert to train()'s verbose
    if verbose in (0, 1):
        verbose_t = 0
    elif verbose == 2:
        verbose_t = 2
    else:
        raise ValueError("incorrect verbose value: choose an integer bewteen 0 and 2")

    ### Select the appropriate model generator based on the type of data
    # Training data
    if ((not isinstance(data_train, pd.DataFrame)) and 
        (not isinstance(data_train, IndexedFile)) and 
        (not isinstance(data_train, str))):
        raise ValueError("data_train should be either a path to an event file, a dataframe or an indexed text file")
    # Validation data
    if ((not isinstance(data_train, pd.DataFrame)) and 
        (not isinstance(data_train, IndexedFile)) and 
        (not isinstance(data_train, str))):
        raise ValueError("data_valid should be either a path to an event file, a dataframe or an indexed text file")

    # Extract the dimensions of the pretrained embeddings
    pretrain_embed_dim = {}
    embed_inputs = params['embedding_input']
    for i, e in enumerate(embed_inputs):
        if embed_inputs[i] and embed_inputs[i] != 'learn':
            pretrain_embed_dim.update({embed_inputs[i]:extract_embedding_dim(embed_inputs[i])})

    ### Create a list of dictionaries giving all possible parameter combinations
    keys, values = zip(*params.items())
    grid_full = [dict(zip(keys, v)) for v in itertools.product(*values)]

    # Remove impossible combinations
    ind_to_remove = []
    for i,d in enumerate(grid_full):
        # In the case of hot encoding or pretrained embedding, no need to set embedding_dim, otherwise,
        # it is essential to set embedding_dim, so remove all cases where embedding_dim is not given with
        # embeddings to be learned from scratch
        if not grid_full[i]['embedding_input']:
            grid_full[i]['embedding_dim'] = None
        elif grid_full[i]['embedding_input'] == 'learn' and not grid_full[i]['embedding_dim']:
            ind_to_remove.append(i) 
        elif grid_full[i]['embedding_input'] and grid_full[i]['embedding_input'] != 'learn':
            grid_full[i]['embedding_dim'] = pretrain_embed_dim[grid_full[i]['embedding_input']]
    # First remove the combinations 'embedding_input = 'learn', embedding_dim = None' 
    for ii in sorted(ind_to_remove, reverse = True):
        del grid_full[ii]
    # Second remove the duplicated combinations 'embedding_input != 'learn', embedding_dim = None' 
    grid_full = [dict(t) for t in {tuple(d.items()) for d in grid_full}]    

    # shuffle the list of params
    if shuffle_grid:
        random.Random(seed).shuffle(grid_full)

    ### Select the combinations to use 
    N_comb = round(prop_grid * len(grid_full)) 
    grid_select = grid_full[:N_comb]

    ### Create a list of lists which stores all parameter combinations that are covered so far in the grid search 
    param_comb_sofar = []

    ### Write to the csv file that encodes the results
    with open(tuning_output_file, mode = 'w', newline = '\n') as o:
        csv_writer = csv.writer(o, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        heading = list(params.keys())
        heading.extend(['loss', 'acc', 'precision', 'recall', 'f1score', 
                        'val_loss', 'val_acc', 'val_precision', 'val_recall', 'val_f1score'])
        csv_writer.writerow(heading)

        ### Run the experiments
        for i, param_comb in enumerate(grid_select):

            start = time.time()

            # Message at the start of each iteration
            if verbose != 0:
                _ = sys.stdout.write('\n********************************** Iteration %d out of %d **********************************\n\n' % ((i+1), len(grid_select)))
                _ = sys.stdout.write('*** Parameter combination \n\n') 
                _ = sys.stdout.write('%s\n' % (param_comb))
                sys.stdout.flush()

            # this will contain the values that will be recorded in each row. 
            # We start by copying the parameter values
            row_values = list(param_comb.values())

            # Check if the current parameter combination has already been processed in the grid search
            if row_values in param_comb_sofar:
                if verbose != 0:
                    _ = sys.stdout.write('\nThis parameter combination was skipped because it has already been processed\n')
                    sys.stdout.flush()

            else:
                # Fit the model given the current param combination
                hist, model = train_LSTM(data_train = data_train, 
                                         data_valid = data_valid, 
                                         cue_index = cue_index, 
                                         outcome_index = outcome_index, 
                                         shuffle_epoch = shuffle_epoch,  
                                         num_threads = num_threads, 
                                         verbose = verbose_t,
                                         metrics = ['accuracy', 'precision', 'recall', 'f1score'],
                                         params = param_comb)

                # Get index of epochs and extract embedding name from the 'param_comb' dictionary
                for ind, (k, v) in enumerate(param_comb.items()):
                    if k == 'epochs':
                        i_epochs = ind
                    elif (k == 'embedding_input') and isinstance(v, str) and (v != 'learn'):
                        # Extract the name of embedding fron the path
                        row_values[ind] = ntpath.basename(v)[:-4]
                    elif (k == 'embedding_input') and not v:
                        row_values[ind] = 'onehot' 
                    elif (k == 'embedding_dim') and not v:
                        row_values[ind] = 0 
                    elif (k == 'activation') and not v:
                        row_values[ind] = 'none' 

                ### Export the results to a csv file
                for j in range(param_comb['epochs']):

                    # Copy the parameter values to current param combination variables
                    row_values_j = row_values.copy()

                    # correct the epoch num
                    row_values_j[i_epochs] = j+1 

                    # Add the derived combination to the list of all parameter combinations
                    param_comb_sofar.append(row_values_j.copy()) 
                    
                    # Add the performance scores
                    # training
                    loss_j = hist['loss'][j]
                    acc_j = hist['accuracy'][j]
                    precision_j = hist['precision'][j]
                    recall_j = hist['recall'][j]            
                    f1score_j = hist['f1score'][j]
                    # validation
                    val_loss_j = hist['val_loss'][j]
                    val_acc_j = hist['val_accuracy'][j]
                    val_precision_j = hist['val_precision'][j]
                    val_recall_j = hist['val_recall'][j]            
                    val_f1score_j = hist['val_f1score'][j]
                    row_values_j.extend([loss_j, acc_j, precision_j, recall_j, f1score_j, 
                                         val_loss_j, val_acc_j, val_precision_j, val_recall_j, val_f1score_j])
                    # Write the row
                    csv_writer.writerow(row_values_j)
                    o.flush()

                if verbose == 1:
                    sys.stdout.write('\nIteration completed in %.0fs\n' % ((time.time() - start)))
                    sys.stdout.flush()

                # Clear memory           
                del model, hist
                gc.collect()
                K.clear_session()

        if verbose != 0:
            _ = sys.stdout.write('\n********************************************************************************************\n')
            sys.stdout.flush()

#####################################
# Naive discriminative learning model
#####################################

class NDLmodel():

    """ Class that contains the training results after ndl training (weights, activations and performance measures)

    Attributes
    ----------
    weights: xarray.DataArray
        matrix of association weights
    activations_train: xarray.DataArray
        matrix of activations for the training data
    activations_valid: xarray.DataArray
        matrix of activations for the validation data

    Returns
    -------
    class object

    """

    # performance_hist: dict
    #     dictionary containing the performance scores in all epochs depending on the metrics that were used during training

    #def __init__(self, weights, activations_train, activations_valid):
    def __init__(self, weights):
        'Initialization'
        self.weights = weights
        # self.activations_train = activations_train
        # self.activations_valid = activations_valid
        #self.performance_hist = performance_hist

def train_NDL(data_train, data_valid, cue_index = None, outcome_index = None,
              shuffle_epoch = False, num_threads = 1, chunksize = None, verbose = 1, 
              temp_dir = None, remove_temp_dir = True,
              metrics = ['accuracy', 'precision', 'recall', 'f1score'], 
              metric_average = 'macro',
              params = {'epochs': 1, # number of iterations over the full set 
                        'lr': 0.0001}):

    """ Train a native discriminative learning model

    Parameters
    ----------
    data_train: dataframe or str
        dataframe or path to the file containing training data
    data_valid: class or dataframe
        dataframe or path to the file containing validation data
    cue_index: dict or None
        If None, all cues in the event file are used. Otherwise a dictionary that maps cues to indices should 
        be given. The dictionary should include only the cues to keep in the data. Default: None
    outcome_index: dict or None
        If None, all outcomes in the event file are used. Otherwise a dictionary that maps outcomes to indices should 
        be given. The dictionary should include only the outcomes to keep in the data. Default: None
    shuffle_epoch: Boolean
        whether to shuffle the data after every epoch (not supported for now). Defult: False
    num_threads: int
        maximum number of processes to use - it should be >= 1. Default: 1
    chunksize : int or None
        number of lines to use for computing the accuracy (set if the data is very large and/or there is a huge number 
        of outcomes - e.g. chunksize = 10000). This is done through the computation of the activation matrix for these 
        lines. If None, all lines will be used. Default: None
    verbose: int (0, 1, or 2)
        verbosity mode. 0 = silent, 1 = one line per epoch, 2 = detailed. Default: 1
    temp_dir: str
        directory where to store temporary files while training NDL. Default: None (will create a folder 
        'TEMP_TRAIN_DIRECTORY' in the current working directory    
    remove_temp_dir: Boolean
        whether or not to remove the temporary directory if one was automatically created. Default: True
    metrics: list
        for now only ['accuracy', 'precision', 'recall', 'f1score'] is accepted
    metric_average: str
        offer almost the same options as the 'average' parameter in sklearn's precision_score, 
        recall_score and f1_score functions ('binary' not considered), that is: 
        'micro': calculate metrics globally by counting the total true positives, 
                 false negatives and false positives
        'macro': calculate metrics for each label, and find their unweighted mean. 
                 This does not take label imbalance into account
        'weighted': calculate metrics for each label, and find their average weighted 
                    by support (the number of true instances for each label).
        'samples': calculate metrics for each instance, and find their average (differs 
                   from accuracy_score only in multilabel classification)
    params: dict
        model parameters:
        'epochs'
        'lr'

    Returns
    -------
    tuple
        fit history and NDL_model class object (stores the weight and activation matrices) 
    """

    from evaluation import activations_to_predictions, predict_outcomes_NDL
    from preprocessing import df_to_gz

    ### check verbose and convert to NDL verbose
    if verbose in (0,1):
        verbose_n = False
    elif verbose == 2:
        verbose_n = True
    else:
        raise ValueError("incorrect verbose value: choose an integer bewteen 0 and 2")

    # If the operating system is a macOS, use method = 'threading' otherwise use 'openmp'
    if sys.platform == 'darwin': # if a Mac user
        method_n = 'threading'
    else:
        method_n = 'openmp'

    # Create a temporary directory if not provided
    if not temp_dir:
        temp_dir0 = os.path.join(os.getcwd(), 'TEMP_TRAIN_DIRECTORY')
        # Add warning if the creation of a temporary directory fails 
        # (e.g. folder with the same name already existing)
        try:
            os.mkdir(temp_dir0) 
        except OSError:
            print("Creation of a temporary directory %s failed. This could be because ", 
                  "a folder with the same name already exists or you don't have the ", 
                  "required admin rights on the computer)." % temp_dir0)
    else:
        temp_dir0 = temp_dir

    ### Path to the train event file
    if isinstance(data_train, str):     
        events_train_path = data_train
    elif isinstance(data_train, pd.DataFrame):
        if verbose ==2:
            _ = sys.stdout.write('\n*** Conversion of the training event-file into .gz\n\n')  
            sys.stdout.flush()
        start_conv_train = time.time()
        events_train_path = os.path.join(temp_dir0, 'unfiltered_events_train.gz')
        df_to_gz(data = data_train, gz_outfile = events_train_path)
        if verbose ==2:
            _ = sys.stdout.write('Conversion completed in %.0fs\n\n' \
                                % (time.time() - start_conv_train))
            sys.stdout.flush()  
    else:
        raise ValueError("data_train should be either a path to an event file or a dataframe")

    ### Path to the validation event file
    if isinstance(data_valid, str):     
        events_valid_path = data_valid
    elif isinstance(data_valid, pd.DataFrame):
        if verbose ==2:
            _ = sys.stdout.write('*** Conversion of the validation event-file into .gz\n\n')  
            sys.stdout.flush()
        start_conv_valid = time.time()
        events_valid_path = os.path.join(temp_dir0, 'unfiltered_events_valid.gz')
        df_to_gz(data = data_valid, gz_outfile = events_valid_path)
        if verbose ==2:
            _ = sys.stdout.write('Conversion completed in %.0fs\n\n' \
                                % (time.time() - start_conv_valid))
            sys.stdout.flush()  
    else:
        raise ValueError("data_valid should be either a path to an event file or a dataframe") 

    ### Filter the event files by retaining only the cues and outcomes that are in the index system (e.g. most frequent tokens) 
    ### if these index systems are provided by the user. Otherwise, use all cues and/or outcomes
    if cue_index or outcome_index: # Filtering only if an index file is provided

        # Paths to the filtered files
        filtered_events_train_path = os.path.join(temp_dir0, 'filtered_events_train.gz')  
        filtered_events_valid_path = os.path.join(temp_dir0, 'filtered_events_valid.gz')  

        # Cues
        if cue_index:
            cues_to_keep = [cue for cue in cue_index.keys()]
        else:
            cues_to_keep = 'all'
        # Outcomes
        if outcome_index:
            outcomes_to_keep = [outcome for outcome in outcome_index.keys()]
        else:
            outcomes_to_keep = 'all'

        # Train set 
        if verbose == 2:
            _ = sys.stdout.write('*** Creation of the filtered training event file\n\n')  
            _ = sys.stdout.write('Progress (each dot represents 100k events): ')
            sys.stdout.flush()
            start_filt_train = time.time()
        filter_event_file(events_train_path,
                          filtered_events_train_path,
                          number_of_processes = num_threads,
                          keep_cues = cues_to_keep,
                          keep_outcomes = outcomes_to_keep,
                          verbose = verbose_n)  
        if verbose == 2:
            _ = sys.stdout.write('\n\nFiltering completed in %.0fs\n\n' \
                                % (time.time() - start_filt_train))
            sys.stdout.flush()

        # Validation set 
        if verbose == 2:
            _ = sys.stdout.write('*** Creation of the filtered validation event file\n\n') 
            _ = sys.stdout.write('Progress (each dot represents 100k events): ') 
            sys.stdout.flush()
            start_filt_valid = time.time() 
        filter_event_file(events_valid_path,
                          filtered_events_valid_path,
                          number_of_processes = num_threads,
                          keep_cues = cues_to_keep,
                          keep_outcomes = outcomes_to_keep,
                          verbose = verbose_n) 
        if verbose == 2:
            _ = sys.stdout.write('\n\nFiltering completed in %.0fs\n\n' \
                                % (time.time() - start_filt_valid))
            sys.stdout.flush()

    else:
        # Paths to the filtered files
        filtered_events_train_path = events_train_path  
        filtered_events_valid_path = events_valid_path 

    if verbose == 2:
        _ = sys.stdout.write('*** Training\n\n')  
        sys.stdout.flush()
    
    start_learn = time.time() 

    # Initialise the weight matrix
    weights = None

    # Initialise the lists where we will store the performance scores in each epoch for the different metrics
    # # train
    # acc_hist = []
    # precision_hist = []
    # recall_hist = []
    # f1score_hist = []

    # # valid
    # val_acc_hist = []
    # val_precision_hist = []
    # val_recall_hist = []
    # val_f1score_hist = []

    ### True outcomes 
    # if not shuffle_epoch: # Extract the train y-values once here only if no shuffling is needed
    #     # tain set 
    #     events_train_df = pd.read_csv(filtered_events_train_path, header = 0, sep='\t', quotechar='"', usecols = ['outcomes'])
    #     y_train_true = events_train_df['outcomes'].tolist()    
    #     del events_train_df
    # validation set 
    # events_valid_df = pd.read_csv(filtered_events_valid_path, header = 0, sep='\t', quotechar='"', usecols = ['outcomes'])
    # y_valid_true = events_valid_df['outcomes'].tolist()
    # del events_valid_df
    
    # Train NDL for the chosen number of epochs. Each time save and print the metric scores
    for j in range(1, (1+params['epochs'])):

        if ((j == 1) or (not np.isnan(weights).any())): # if no nan values in the weight matrix (i.e. no divergence problem):

            if verbose != 0:
                sys.stdout.write('Epoch %d/%d\n' % (j, params['epochs']))
                sys.stdout.flush()

            epoch_no_diverg = j # Keep track of the last epoch without a divergence problem

            # Train ndl to get the weight matrix 
            start_weight = time.time()
            weights = ndl(events = filtered_events_train_path,
                          alpha = params['lr'], 
                          betas = (1, 1),
                          method = method_n,
                          weights = weights,
                          number_of_threads = num_threads,
                          remove_duplicates = True,
                          temporary_directory = temp_dir0,
                          verbose = False)
            if verbose == 2:
                sys.stdout.write(' - weight mat in %.0fs\n' % ((time.time() - start_weight)))
                sys.stdout.flush()

            # Predicted outcomes from the activations
            # start_pred_train = time.time()
            # y_train_pred = predict_outcomes_NDL(model = NDLmodel(weights),  
            #                                     data_test = filtered_events_train_path,
            #                                     temp_dir = temp_dir0,
            #                                     remove_temp_dir = False,
            #                                     chunksize = chunksize, 
            #                                     num_threads = 1) # faster to use 1 for computing the activations
            # if verbose == 2:
            #     sys.stdout.write(' - train pred in %.0fs\n' % ((time.time() - start_pred_train)))
            #     sys.stdout.flush()
            # start_pred_valid = time.time()
            # y_valid_pred = predict_outcomes_NDL(model = NDLmodel(weights), 
            #                                     data_test = filtered_events_valid_path, 
            #                                     temp_dir = temp_dir0,
            #                                     remove_temp_dir = False,
            #                                     chunksize = chunksize, 
            #                                     num_threads = 1) # faster to use 1 for computing the activations
            # if verbose == 2:
            #     sys.stdout.write(' - valid pred in %.0fs\n' % ((time.time() - start_pred_valid)))
            #     sys.stdout.flush()

            ### True outcomes 
            # if shuffle_epoch: # Extract the true y-values each time if the train data is shuffled 
            #     # tain set 
            #     events_train_df = pd.read_csv(filtered_events_train_path, header = 0, sep='\t', quotechar='"', usecols = ['outcomes'])
            #     y_train_true = events_train_df['outcomes'].tolist()    
            #     del events_train_df
            
            # Compute performance scores for the different metrics
            # accuracy
            # acc_j = accuracy_score(y_train_true, y_train_pred)
            # acc_hist.append(acc_j)
            # val_acc_j = accuracy_score(y_valid_true, y_valid_pred)
            # val_acc_hist.append(val_acc_j)

            # precision
            # precision_j = precision_score(y_train_true, y_train_pred, average = metric_average)
            # precision_hist.append(precision_j)
            # val_precision_j = precision_score(y_valid_true, y_valid_pred, average = metric_average)
            # val_precision_hist.append(val_precision_j)

            # recall
            # recall_j = recall_score(y_train_true, y_train_pred, average = metric_average)
            # recall_hist.append(recall_j)
            # val_recall_j = recall_score(y_valid_true, y_valid_pred, average = metric_average)
            # val_recall_hist.append(val_recall_j)

            # F1-score
            # f1score_j = f1_score(y_train_true, y_train_pred, average = metric_average)
            # f1score_hist.append(f1score_j)
            # val_f1score_j = f1_score(y_valid_true, y_valid_pred, average = metric_average)
            # val_f1score_hist.append(val_f1score_j)  

        # else: # Measures will be set to np.nan if learning has diverged and weights won't be updated

            # accuracy
            # acc_j = np.nan
            # acc_hist.append(acc_j)
            # val_acc_j = np.nan
            # val_acc_hist.append(val_acc_j)

            # precision
            # precision_j = np.nan
            # precision_hist.append(precision_j)
            # val_precision_j = np.nan
            # val_precision_hist.append(val_precision_j)

            # recall
            # recall_j = np.nan
            # recall_hist.append(recall_j)
            # val_recall_j = np.nan
            # val_recall_hist.append(val_recall_j)

            # F1-score
            # f1score_j = np.nan
            # f1score_hist.append(f1score_j)
            # val_f1score_j = np.nan
            # val_f1score_hist.append(val_f1score_j)  

        # Display progress message  
        if verbose != 0:
            #sys.stdout.write(' - %.0fs - acc: %.4f - val_acc: %.4f\n' % ((time.time() - start_weight), acc_j, val_acc_j))
            #sys.stdout.write(' - %.0fs - val_acc: %.4f\n' % ((time.time() - start_weight), val_acc_j))
            sys.stdout.write(' - %.0fs\n' % (time.time() - start_weight))
            sys.stdout.flush()

        # Garbage collection after each iteration
        gc.collect()

    if verbose == 2:
        _ = sys.stdout.write('\nTraining completed in %.0fs\n' \
                            % (time.time() - start_learn))
        sys.stdout.flush()
                      
    ### Model object
    model = NDLmodel(weights)

    if (j>1 and np.isnan(weights).any()): # display a message to notify about a divergence problem:
        sys.stdout.write('Warning: learning diverged in epoch %d!!!\n\n' % ((epoch_no_diverg+1)))
        sys.stdout.flush()

    ### Fit history object
    # hist = {#'accuracy': acc_hist,
    #         #'precision': precision_hist,
    #         #'recall': recall_hist,
    #         #'f1score': f1score_hist,
    #         'val_accuracy': val_acc_hist,
    #         'val_precision': val_precision_hist,
    #         'val_recall': val_recall_hist,
    #         'val_f1score': val_f1score_hist
    #         }

    ### Remove temporary directory if it was automatically created and the option was selected by the user
    if remove_temp_dir and not temp_dir:
        try:
            shutil.rmtree(temp_dir0)
        except OSError as e:
            print("Error: %s : %s" % (temp_dir0, e.strerror))
   
    #return hist, model
    return model

def grid_search_NDL(data_train, data_valid, params, prop_grid, 
                    tuning_output_file, cue_index = None, outcome_index = None, 
                    temp_dir = None, remove_temp_dir = True,   
                    metrics = ['accuracy', 'precision', 'recall', 'f1score'], 
                    metric_average = 'macro', shuffle_epoch = False, 
                    shuffle_grid = True, num_threads = 1, chunksize = 10000, 
                    seed = None, verbose = 1):

    """ Grid search for the naive discriminative learning model

    Parameters
    ----------
    data_train: dataframe or str
        dataframe or path to the file containing training data
    data_valid: class or dataframe
        dataframe or indexed text file containing validation data
    params: dict of lists
        model parameters:
        'epochs'
        'lr'
    prop_grid: float
        proportion of the grid combinations to sample 
    tuning_output_file: str
        path of the csv file where the grid search results will be stored
    cue_index: dict or None
        If None, all cues in the event file are used. Otherwise a dictionary that maps cues to indices should 
        be given. The dictionary should include only the cues to keep in the data. Default: None
    outcome_index: dict or None
        If None, all outcomes in the event file are used. Otherwise a dictionary that maps outcomes to indices should 
        be given. The dictionary should include only the outcomes to keep in the data. Default: None
    temp_dir: str
        directory where to store temporary files while training NDL. Default: a folder 'TEMP_TRAIN_DIRECTORY' 
        is created in the current working directory    
    remove_temp_dir: Boolean
        whether or not to remove the temporary directory if one was automatically created. Default: True
    metrics: list
        for now only ['accuracy', 'precision', 'recall', 'f1score'] is accepted
    metric_average: str
        offer almost the same options as the 'average' parameter in sklearn's precision_score, 
        recall_score and f1_score functions ('binary' not considered), that is: 
        'micro': calculate metrics globally by counting the total true positives, 
                 false negatives and false positives
        'macro': calculate metrics for each label, and find their unweighted mean. 
                 This does not take label imbalance into account
        'weighted': calculate metrics for each label, and find their average weighted 
                    by support (the number of true instances for each label).
        'samples': calculate metrics for each instance, and find their average (differs 
                   from accuracy_score only in multilabel classification)
    shuffle_epoch: Boolean
        whether to shuffle the data after every epoch. Default: False
    shuffle_grid: Boolean
        whether to shuffle the parameter grid or respect the same order of parameters. Default: True
        provided in `params'
    use_multiprocessing: Boolean
        whether to generate batches in parallel. Default: False
    num_threads: int
        maximum number of processes to spin up when using generating the batches. Default: 0
    chunksize : int
        number of lines to use for computing the accuracy. This is done through 
        the computation of the activation matrix for these lines. Default: 10000
    seed : int or None
        random seed to initialise the pseudorandom number generator (for selecting the parameter 
        combinations to cover). Use it if you want to have replicable results. Default: None
    verbose: int (0, 1, or 2)
        verbosity mode. 0 = silent, 1 = one line per parameter combination, 2 = detailed. Default: 1

    Returns
    -------
    None
        save csv files
    """

    ### check verbose and convert to NDL and train() verbose
    if verbose in (0, 1):
        verbose_t = 0
        verbose_n = False
    elif verbose == 2:
        verbose_t = 2
        verbose_n = True
    else:
        raise ValueError("incorrect verbose value: choose an integer bewteen 0 and 2")

    # Create a temporary directory if not provided
    if not temp_dir:
        temp_dir0 = os.path.join(os.getcwd(), 'TEMP_TRAIN_DIRECTORY')
        # Add warning if the creation of a temporary directory fails 
        # (e.g. folder with the same name already existing)
        try:
            os.mkdir(temp_dir0) 
        except OSError:
            print("Creation of a temporary directory %s failed. This could be because ", 
                  "a folder with the same name already exists or you don't have the ", 
                  "required admin rights on the computer)." % temp_dir0)
    else:
        temp_dir0 = temp_dir

    ### Path to the train event file
    if isinstance(data_train, str):     
        events_train_path = data_train
    elif isinstance(data_train, pd.DataFrame):
        if verbose ==2:
            _ = sys.stdout.write('\n******************** Conversion of the training event-file into .gz ********************\n\n')  
            sys.stdout.flush()
        start_conv_train = time.time()
        events_train_path = os.path.join(temp_dir0, 'unfiltered_events_train.gz')
        df_to_gz(data = data_train, gz_outfile = events_train_path)
        if verbose ==2:
            _ = sys.stdout.write('Conversion completed in %.0fs\n\n' \
                                % (time.time() - start_conv_train))
            sys.stdout.flush()  
    else:
        raise ValueError("data_train should be either a path to an event file or a dataframe")

    ### Path to the validation event file
    if isinstance(data_valid, str):     
        events_valid_path = data_valid
    elif isinstance(data_valid, pd.DataFrame):
        if verbose ==2:
            _ = sys.stdout.write('******************* Conversion of the validation event-file into .gz *******************\n\n')  
            sys.stdout.flush()
        start_conv_valid = time.time()
        events_valid_path = os.path.join(temp_dir0, 'unfiltered_events_valid.gz')
        df_to_gz(data = data_valid, gz_outfile = events_valid_path)
        if verbose ==2:
            _ = sys.stdout.write('Conversion completed in %.0fs\n\n' \
                                % (time.time() - start_conv_valid))
            sys.stdout.flush()  
    else:
        raise ValueError("data_valid should be either a path to an event file or a dataframe")  

    ### Filter the event files by retaining only the cues and outcomes that are in the index system (e.g. most frequent tokens) 
    ### if these index systems are provided by the user. Otherwise, use all cues and/or outcomes
    if cue_index or outcome_index: # Filtering only if an index file is provided

        # Paths to the filtered files
        filtered_events_train_path = os.path.join(temp_dir0, 'filtered_events_train_grid.gz')  
        filtered_events_valid_path = os.path.join(temp_dir0, 'filtered_events_valid_grid.gz')

        # Cues
        if cue_index:
            cues_to_keep = [cue for cue in cue_index.keys()]
        else:
            cues_to_keep = 'all'
        # Outcomes
        if outcome_index:
            outcomes_to_keep = [outcome for outcome in outcome_index.keys()]
        else:
            outcomes_to_keep = 'all'

        # Train set 
        if verbose == 2:
            _ = sys.stdout.write('********************* Creation of the filtered training event file *********************\n\n')  
            _ = sys.stdout.write('Progress (each dot represents 100k events): ')
            sys.stdout.flush()
            start_filt_train = time.time()
        filter_event_file(events_train_path,
                          filtered_events_train_path,
                          number_of_processes = num_threads,
                          keep_cues = cues_to_keep,
                          keep_outcomes = outcomes_to_keep,
                          verbose = verbose_n)  
        if verbose == 2:
            _ = sys.stdout.write('\n\nFiltering completed in %.0fs\n\n' \
                                % (time.time() - start_filt_train))
            sys.stdout.flush()

        # Validation set 
        if verbose == 2:
            _ = sys.stdout.write('******************** Creation of the filtered validation event file ********************\n\n') 
            _ = sys.stdout.write('Progress (each dot represents 100k events): ') 
            sys.stdout.flush()
            start_filt_valid = time.time() 
        filter_event_file(events_valid_path,
                          filtered_events_valid_path,
                          number_of_processes = num_threads,
                          keep_cues = cues_to_keep,
                          keep_outcomes = outcomes_to_keep,
                          verbose = verbose_n) 
        if verbose == 2:
            _ = sys.stdout.write('\n\nFiltering completed in %.0fs\n\n' \
                                % (time.time() - start_filt_valid))
            sys.stdout.flush()

    else:
        # Paths to the filtered files
        filtered_events_train_path = events_train_path  
        filtered_events_valid_path = events_valid_path

    ### Create a list of dictionaries giving all possible parameter combinations
    keys, values = zip(*params.items())
    grid_full = [dict(zip(keys, v)) for v in itertools.product(*values)]

    # shuffle the list of params
    if shuffle_grid:
        random.Random(seed).shuffle(grid_full)

    ### Select the combinations to use 
    N_comb = round(prop_grid * len(grid_full)) 
    grid_select = grid_full[:N_comb]

    ### Create a list of lists which stores all parameter combinations that are covered so far in the grid search 
    param_comb_sofar = []

    ### Write to the csv file that encodes the results
    with open(tuning_output_file, mode = 'w', newline = '\n') as o:
        csv_writer = csv.writer(o, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        heading = list(params.keys())
        heading.extend(['val_acc', 'val_precision', 'val_recall', 'val_f1score'])
        # heading.extend(['acc', 'precision', 'recall', 'f1score', 
        #                 'val_acc', 'val_precision', 'val_recall', 'val_f1score'])
        csv_writer.writerow(heading)

        ### Run the experiments
        for i, param_comb in enumerate(grid_select):

            start = time.time()

            # Message at the start of each iteration
            if verbose != 0:
                _ = sys.stdout.write('\n******************************** Iteration %d out of %d *********************************\n\n' % ((i+1), len(grid_select)))
                _ = sys.stdout.write('*** Parameter combination \n\n') 
                _ = sys.stdout.write('%s\n\n' % (param_comb))
                sys.stdout.flush()

            # this will contain the values that will be recorded in each row. 
            # We start by copying the parameter values
            row_values = list(param_comb.values())

            # Get index of epochs in the 'param_comb' dictionary
            for ind, (k, v) in enumerate(param_comb.items()):
                if k == 'epochs':
                    i_epochs = ind

            # Check if the current parameter combination has already been processed in the grid search
            if row_values in param_comb_sofar:
                if verbose != 0:
                    _ = sys.stdout.write('This parameter combination was skipped because it has already been processed\n')
                    sys.stdout.flush()
                    #print(f' - This parameter combination was skipped because it has already been processed: {param_comb}\n')

            else:
                hist, model = train_NDL(data_train = filtered_events_train_path, 
                                        data_valid = filtered_events_valid_path,  
                                        shuffle_epoch = shuffle_epoch, 
                                        num_threads = num_threads,
                                        chunksize = chunksize, 
                                        verbose = verbose_t,
                                        temp_dir = temp_dir0,
                                        remove_temp_dir = False,
                                        metrics = metrics, 
                                        metric_average = metric_average,
                                        params = param_comb)

                ### Export the results to a csv file
                for j in range(param_comb['epochs']):

                    # Copy the parameter values to current param combination variables
                    row_values_j = row_values.copy()

                    # correct the epoch num
                    row_values_j[i_epochs] = j+1 

                    # Add the derived combination to the list of all parameter combinations
                    param_comb_sofar.append(row_values_j.copy()) 
                    
                    # Add the performance scores
                    # # training
                    # acc_j = hist['accuracy'][j]
                    # precision_j = hist['precision'][j]
                    # recall_j = hist['recall'][j]            
                    # f1score_j = hist['f1score'][j]
                    # validation
                    val_acc_j = hist['val_accuracy'][j]
                    val_precision_j = hist['val_precision'][j]
                    val_recall_j = hist['val_recall'][j]            
                    val_f1score_j = hist['val_f1score'][j]
                    row_values_j.extend([val_acc_j, val_precision_j, val_recall_j, val_f1score_j])
                    # row_values_j.extend([acc_j, precision_j, recall_j, f1score_j, 
                    #                 val_acc_j, val_precision_j, val_recall_j, val_f1score_j])
                    # Write the row
                    csv_writer.writerow(row_values_j)
                    o.flush()

                if verbose == 1:
                    sys.stdout.write('Iteration completed in %.0fs\n' % ((time.time() - start)))
                    sys.stdout.flush()

    if verbose != 0:
        _ = sys.stdout.write('\n****************************************************************************************\n')
        sys.stdout.flush()

    ### Remove temporary directory if it was automatically created and the option was selected by the user
    if remove_temp_dir and not temp_dir:
        try:
            shutil.rmtree(temp_dir0)
        except OSError as e:
            print("Error: %s : %s" % (temp_dir0, e.strerror))


###################################
# One function to train all models
###################################

def train(model, data_train, data_valid, cue_index, outcome_index, 
          params, shuffle_epoch = False, num_threads = 1, 
          verbose = 1, metrics = ['accuracy', 'precision', 'recall', 'f1score'], 
          metric_average = 'macro', chunksize = 10000,
          temp_dir = None, remove_temp_dir = True):

    """ Train a language learning model

    Parameters
    ----------
    model: str
        name of the model to train. The function currently supports feedforward neural networks (model = 'FNN'),
        long-short term memory (model = 'LSTM') and naive discriminative learning (model = 'NDL') also commonly known as 
        Rescorla-Wagner model.
    data_train: dataframe or class
        dataframe, path to a '.gz' event file or indexed text file containing training data
    data_valid: class or dataframe
        dataframe, path to a '.gz' event file or indexed text file containing validation data  
    cue_index: dict
        mapping from cues to indices. The dictionary should include only the cues to keep in the data
    outcome_index: dict
        mapping from outcomes to indices. The dictionary should include only the outcomes to keep in the data 
    params: dict
        parameter values to be used to train the model  
    shuffle_epoch: Boolean
        whether to shuffle the data after every epoch
    num_threads: int
        maximum number of processes to use - it should be >= 1. Default: 1
    verbose: int (0, 1, or 2)
        verbosity mode. 0 = silent, 1 = one line per epoch, 2 = detailed. Default: 1
    metrics: list
        for now only ['accuracy', 'precision', 'recall', 'f1score'] is accepted
    metric_average: str
        offer almost the same options as the 'average' parameter in sklearn's precision_score, 
        recall_score and f1_score functions ('binary' not considered), that is: 
        'micro': calculate metrics globally by counting the total true positives, 
                 false negatives and false positives
        'macro': calculate metrics for each label, and find their unweighted mean. 
                 This does not take label imbalance into account
        'weighted': calculate metrics for each label, and find their average weighted 
                    by support (the number of true instances for each label).
        'samples': calculate metrics for each instance, and find their average (differs 
                   from accuracy_score only in multilabel classification) 
    chunksize : int
        Can be used only when training NDL. It controls the number of lines to use for computing the accuracy in 
        NDL training. This is done through the computation of the activation matrix for these lines. Default: 10000 
    temp_dir: str
        Can be used only when training NDL. It indicates the directory where to store temporary files while training NDL. Default: a folder 'TEMP_TRAIN_DIRECTORY' 
        is created in the current working directory    
    remove_temp_dir: Boolean
        Can be used only when training NDL. It indicates whether or not to remove the temporary directory. Default: True

    Returns
    -------
    tuple
        keras fit history and model objects  
    """

    ### FNN model
    if model == 'FNN':
        hist, model = train_FNN(data_train = data_train, 
                                data_valid = data_valid, 
                                cue_index = cue_index, 
                                outcome_index = outcome_index, 
                                shuffle_epoch = shuffle_epoch, 
                                num_threads = num_threads, 
                                verbose = verbose,
                                metrics = metrics,
                                params = params)

    ### LSTM model
    elif model == 'LSTM':
        hist, model = train_LSTM(data_train = data_train, 
                                 data_valid = data_valid, 
                                 cue_index = cue_index, 
                                 outcome_index = outcome_index, 
                                 shuffle_epoch = shuffle_epoch, 
                                 num_threads = num_threads, 
                                 verbose = verbose,
                                 metrics = metrics,
                                 params = params)

    ### NDL model
    elif model == 'NDL':
        hist, model = train_NDL(data_train = data_train, 
                                data_valid = data_valid,  
                                cue_index = cue_index, 
                                outcome_index = outcome_index,
                                shuffle_epoch = shuffle_epoch, 
                                num_threads = num_threads,
                                chunksize = chunksize, 
                                verbose = verbose,
                                temp_dir = temp_dir,
                                remove_temp_dir = remove_temp_dir,
                                metrics = ['accuracy', 'precision', 'recall', 'f1score'], # Needs to be corrected later
                                metric_average = metric_average,
                                params = params)
    # Raise an error if a non-supported model is entered 
    else:
        raise ValueError(f'The entered model "{model}" is not supported')

  
    return hist, model

def grid_search(model, data_train, data_valid, cue_index, 
                outcome_index, params, prop_grid, tuning_output_file, 
                shuffle_epoch = False, shuffle_grid = True, metric_average = 'macro', 
                num_threads = 1, seed = None, verbose = 1, chunksize = 10000, 
                temp_dir = None, remove_temp_dir = True):

    """ Grid search for the language learning model

    Parameters
    ----------
    model: str
        name of the model to train. The function currently supports feedforward neural networks (model = 'FNN'),
        long-short term memory (model = 'LSTM') and naive discriminative learning (model = 'NDL') also commonly known as 
        Rescorla-Wagner model.
    data_train: dataframe or class
        dataframe, path to a '.gz' event file or indexed text file containing training data
    data_valid: class or dataframe
        dataframe, path to a '.gz' event file or indexed text file containing validation data  
    cue_index: dict
        mapping from cues to indices. The dictionary should include only the cues to keep in the data
    outcome_index: dict
        mapping from outcomes to indices. The dictionary should include only the outcomes to keep in the data 
    params: dict
        parameter values to be used to train the model 
    prop_grid: float
        proportion of the grid combinations to sample 
    tuning_output_file: str
        path of the csv file where the grid search results will be stored
    shuffle_epoch: Boolean
        whether to shuffle the data after every epoch. Default: False
    shuffle_grid: Boolean
        whether to shuffle the parameter grid or respect the same order of parameters. Default: True
        provided in `params'
    num_threads: int
        maximum number of processes to use - it should be >= 1. Default: 1
    seed : int or None
        random seed to initialise the pseudorandom number generator (for selecting the parameter 
        combinations to cover). Use it if you want to have replicable results. Default: None
    verbose: int (0, 1, or 2)
        verbosity mode. 0 = silent, 1 = one line per parameter combination, 2 = detailed. Default: 1
    chunksize : int
        Can be used only when training NDL. It controls the number of lines to use for computing the accuracy in 
        NDL training. This is done through the computation of the activation matrix for these lines. Default: 10000 
    temp_dir: str
        Can be used only when training NDL. It indicates the directory where to store temporary files while training NDL. Default: a folder 'TEMP_TRAIN_DIRECTORY' 
        is created in the current working directory    
    remove_temp_dir: Boolean
        Can be used only when training NDL. It indicates whether or not to remove the temporary directory. Default: True

    Returns
    -------
    None
        save csv files
    """

    ### FNN model
    if model == 'FNN':
        grid_search_FNN(data_train = data_train, 
                        data_valid = data_valid, 
                        cue_index = cue_index, 
                        outcome_index = outcome_index, 
                        params = params, 
                        prop_grid = prop_grid, 
                        tuning_output_file = tuning_output_file,         
                        shuffle_epoch = shuffle_epoch, 
                        shuffle_grid = shuffle_grid, 
                        num_threads = num_threads, 
                        seed = seed,
                        verbose = verbose)

    ### LSTM model
    elif model == 'LSTM':
        grid_search_LSTM(data_train = data_train, 
                         data_valid = data_valid, 
                         cue_index = cue_index, 
                         outcome_index = outcome_index,
                         params = params, 
                         prop_grid = prop_grid, 
                         tuning_output_file = tuning_output_file,         
                         shuffle_epoch = shuffle_epoch, 
                         shuffle_grid = shuffle_grid,  
                         num_threads = num_threads, 
                         seed = seed,
                         verbose = verbose)
 
    ### NDL model
    elif model == 'NDL':
        grid_search_NDL(data_train = data_train, 
                        data_valid = data_valid,
                        params = params, 
                        prop_grid = prop_grid, 
                        tuning_output_file = tuning_output_file,          
                        cue_index = cue_index, 
                        outcome_index = outcome_index, 
                        temp_dir = temp_dir,
                        remove_temp_dir = remove_temp_dir,
                        metrics = ['accuracy', 'precision', 'recall', 'f1score'], # Needs to be corrected later
                        metric_average = metric_average,
                        shuffle_epoch = shuffle_epoch, 
                        shuffle_grid = shuffle_grid, 
                        num_threads = num_threads,
                        chunksize = chunksize, 
                        seed = seed,
                        verbose = verbose)

    # Raise an error if a non-supported model is entered 
    else:
        raise ValueError(f'The entered model "{model}" is not supported')
    

##################################
# Saving and loading model objects
##################################

def export_model(model, path):

    """ Save a model object to disk

    Parameters
    ----------
    model: class
        model class object (e.g. keras or NDL)
    path: str
        path where to save the file (use .h5 file format)

    Returns
    -------
    None
        export the class as an hdf5 file
    """

    # Save model as an hdf5 file
    if isinstance(model, Sequential):
        model.save(path)
    elif isinstance(model, NDLmodel):  
        model.weights.to_netcdf(path) # Only the weight matrix is saved 
    else: 
        raise ValueError("model should be a keras (Sequential class) or ndl (NDLmodel class) model")

def import_model(path, custom_measures = None):

    """ Load a model object from disk. The model should be saved in an hdf5 file

    Parameters
    ----------
    path: str
        path where the file is saved
    custom_measures: 
        optional dictionary that maps names (strings) to custom performance measures like precision and recall.

    Returns
    -------
    class object
        either a keras or NDL model object
    """

    with h5py.File(path, 'r') as f:
        if 'model_weights' in f.keys(): # => keras object
            model = load_model(path, custom_objects = custom_measures)
        elif '__xarray_dataarray_variable__' in f.keys(): # => NDLmodel object
            with xr.open_dataarray(path) as weights_read:  
                model = NDLmodel(weights = weights_read)
        else:
            raise ValueError("Stored model should be a keras (Sequential class) or ndl (NDLmodel class) model")
    return model

def export_history(history_dict, path):

    """ Save an NDL or keras training history 

    Parameters
    ----------
    history_dict: dict
        training history stored as a dictionary, and which contains the performance scores (loss and other metrics) for each epoch
    path: str
        path where to save the file

    Returns
    -------
    None
        export a dictionary as a json file
    """

    # Convert float numbers in the lists to str
    for k, v in history_dict.items(): 
        history_dict[k] = list(map(str, v))
    # Save it as a json file  
    json.dump(history_dict, open(path, 'w'))

def import_history(path):

    """ Load an NDL or keras training history as a dictionary 

    Parameters
    ----------
    path: str
        path where the file is saved

    Returns
    -------
    dict
        history dictionary containing the performance scores (loss and other metrics) for each epoch
    """

    # Load the disctionary from the json file  
    history_dict = json.load(open(path, 'r'))
    # Convert the lists of str into lists of floats
    for k, v in history_dict.items(): 
        history_dict[k] = list(map(float, v))

    return history_dict

################
# Useful tools
#################

def estimate_gridsearch_size(model, params):

    """ Compute the total number of parameter combinations in a grid search 

    Parameters
    ----------
    model: str
        name of the model to train. The function currently supports feedforward neural networks (model = 'FNN'),
        long-short term memory (model = 'LSTM') and naive discriminative learning (model = 'NDL') also commonly known as 
        Rescorla-Wagner model.
    params: dict of lists
        parameter set of the grid search:

    Returns
    -------
    int
        number of param combinations
    """
    
    ### FNN model
    if model == 'FNN':

        # Extract the dimensions of the pretrained embeddings
        pretrain_embed_dim = {}
        embed_inputs = params['embedding_input']
        for i, e in enumerate(embed_inputs):
            if embed_inputs[i] and embed_inputs[i] != 'learn':
                pretrain_embed_dim.update({embed_inputs[i]:extract_embedding_dim(embed_inputs[i])})

        # Create a list of dictionaries giving all possible parameter combinations
        keys, values = zip(*params.items())
        grid_full = [dict(zip(keys, v)) for v in itertools.product(*values)]

        ### Remove impossible combinations
        ind_to_remove = []
        for i,d in enumerate(grid_full):
            # In the case of no hidden layer, no need to set the 'activation' parameter - only 'last_activation' is used
            if grid_full[i]['hidden_layers'] == 0:
                grid_full[i]['activation'] = None
            # In the case of hot encoding or pretrained embedding, no need to set embedding_dim, otherwise,
            # it is essential to set embedding_dim, so remove all cases where embedding_dim is not given with
            # embeddings to be learned from scratch
            if not grid_full[i]['embedding_input']:
                grid_full[i]['embedding_dim'] = None
            elif grid_full[i]['embedding_input'] == 'learn' and not grid_full[i]['embedding_dim']:
                ind_to_remove.append(i) 
            elif grid_full[i]['embedding_input'] and grid_full[i]['embedding_input'] != 'learn':
                grid_full[i]['embedding_dim'] = pretrain_embed_dim[grid_full[i]['embedding_input']]
            # In the case of embeddings, it is essential to set 'max_len' (max_len cannot be None),
            # so remove all cases where embeddings are used max_len is not given
            if grid_full[i]['embedding_input'] and not grid_full[i]['max_len']:
                ind_to_remove.append(i) 
                
        # First remove the detected impossible combinations (e.g. 'embedding_input = 'learn', embedding_dim = None') 
        for ii in sorted(ind_to_remove, reverse = True):
            del grid_full[ii]
        # Second remove the duplicated combinations 'embedding_input != 'learn', embedding_dim = None' 
        grid_full = [dict(t) for t in {tuple(d.items()) for d in grid_full}]    

    ### LSTM model
    elif model == 'LSTM':

        # Extract the dimensions of the pretrained embeddings
        pretrain_embed_dim = {}
        embed_inputs = params['embedding_input']
        for i, e in enumerate(embed_inputs):
            if embed_inputs[i] and embed_inputs[i] != 'learn':
                pretrain_embed_dim.update({embed_inputs[i]:extract_embedding_dim(embed_inputs[i])})

        ### Create a list of dictionaries giving all possible parameter combinations
        keys, values = zip(*params.items())
        grid_full = [dict(zip(keys, v)) for v in itertools.product(*values)]

        ### Remove impossible combinations
        ind_to_remove = []
        for i,d in enumerate(grid_full):
            # In the case of hot encoding or pretrained embedding, no need to set embedding_dim, otherwise,
            # it is essential to set embedding_dim, so remove all cases where embedding_dim is not given with
            # embeddings to be learned from scratch
            if not grid_full[i]['embedding_input']:
                grid_full[i]['embedding_dim'] = None
            elif grid_full[i]['embedding_input'] == 'learn' and not grid_full[i]['embedding_dim']:
                ind_to_remove.append(i) 
            elif grid_full[i]['embedding_input'] and grid_full[i]['embedding_input'] != 'learn':
                grid_full[i]['embedding_dim'] = pretrain_embed_dim[grid_full[i]['embedding_input']]
        
        # First remove the combinations 'embedding_input = 'learn', embedding_dim = None' 
        for ii in sorted(ind_to_remove, reverse = True):
            del grid_full[ii]
        # Second remove the duplicated combinations 'embedding_input != 'learn', embedding_dim = None' 
        grid_full = [dict(t) for t in {tuple(d.items()) for d in grid_full}]  

    ### NDL model
    elif model == 'NDL': 

        ### Create a list of dictionaries giving all possible parameter combinations
        keys, values = zip(*params.items())
        grid_full = [dict(zip(keys, v)) for v in itertools.product(*values)]

    # Raise an error if a non-supported model is entered 
    else:
        raise ValueError(f'The entered model "{model}" is not supported')

    return len(grid_full)
