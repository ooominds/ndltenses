import pandas as pd
import pickle
import numpy as np
from sklearn.preprocessing import LabelEncoder
import re


CORPUS = 'Data/qualtrics.csv'
ASSOCIATIONS = 'associates/strength_irene.SWOW-EN.R1.pkl'
CORPUS_WITH_ASSOCIATES = 'Results/qualtrics_with_associates.csv'
CORPUS_WITH_DICTIONARY = 'Results/qualtrics_with_dictionary.csv'
CORPUS_WITH_SET = 'Results/qualtrics_with_set.csv'


corpus = pd.read_csv(CORPUS)
associations_file = open(ASSOCIATIONS, 'rb')
associations = pickle.load(associations_file)
#print(isinstance(associations, dict))
#dict_items = associations.items()
#first_two = list(dict_items)[:2]
#print(first_two)
#print(type(first_two[0]))
#print(type(first_two[0][1]))


def make_set(lookup_dict):
    list_of_sets = list()
    for key in lookup_dict:
        list_of_sets.append(set(lookup_dict[key]))
    return list_of_sets
    
dict_sets = make_set(associations)
#print(dict_sets[0])


def dict_lookup(sentence, lookup_dict, noun):
    preceding, _ = sentence.split('<')
    words = preceding.split()
    hk = 0
    if noun in lookup_dict:
        for word in words:
            if word in lookup_dict[noun]:
                print(word)
                if lookup_dict[noun][word] > 1:
                    hk += 1
    else:
        hk = 'not found'
    return hk

#print(corpus.head())
#corpus['associated_hk'] = corpus.apply(lambda x: dict_lookup(x.loc['Sentence'], associations, x.loc['noun']), axis=1)


def set_lookup(sentence, lookup_set, noun):
    preceding, _ = sentence.split('<')
    words = preceding.split()
    hk = 0
    found = 0
    for item_set in lookup_set:
        if noun in item_set:
            found += 1
            for word in words:
                if word in item_set:
                    hk += 1
    if hk > 1:
        hk = 1
    if found == 0:
        hk = 'not found'
    return hk
    
def set_lookup_qualtrics(words, lookup_set, noun):
    hk = 0
    found = 0
    for item_set in lookup_set:
        if noun in item_set:
            found += 1
            for word in words:
                if word in item_set:
                    hk += 1
    if hk > 1:
        hk = 1
    if found == 0:
        hk = 'not found'
    return hk
    
def dict_lookup_qualtrics(words, lookup_dict, noun):
    hk = 0
    if noun in lookup_dict:
        for word in words:
            if word in lookup_dict[noun]:
                print(word)
                if lookup_dict[noun][word] > 1:
                    hk += 1
    else:
        hk = 'not found'
    return hk
    
    
    
#corpus['indirect_association_simple'] = corpus.apply(lambda x: set_lookup(x.loc['Sentence'], dict_sets, x.loc['noun']), axis=1)
#corpus.to_csv(CORPUS_WITH_ASSOCIATES, index=False)

def encode(hk):
    encoded_hk = 0
    if hk == 'known':
        encoded_hk += 1
    return encoded_hk

corpus['hk_encoded'] = corpus.apply(lambda x : encode(x.loc['hk']), axis=1)
labelencoder = LabelEncoder()
corpus['TextID'] = labelencoder.fit_transform(corpus['Text ID'])
corpus.sort_values(by=['TextID', 'Sentence ID'], inplace=True)
corpus.to_csv(CORPUS, index=False)

def associate(sents, lookup_dict, lookup_set):
    hk_direct_list = list()
    hk_indirect_list = list()
    prev_id = 0
    text_by_id = list()
    for i, row in sents.iterrows():
        s = row['Sentence']
        s = s.lower()
        s = re.sub(r'[^\w\s]','',s)
        print(s)
        noun = row['noun']
        noun = noun.lower()
        noun = noun.strip()
        print(noun)
        text_id = row['TextID']
        sent = s.split()
        index = sent.index(noun)
        preceding = sent[:index]
        #words = preceding.split()
        if text_id != prev_id:
            text_by_id = []
        text_by_id.extend(preceding)
        hk_direct = dict_lookup_qualtrics(preceding, lookup_dict, noun)
        hk_indirect = set_lookup_qualtrics(preceding, lookup_set, noun)
        hk_direct_list.append(hk_direct)
        hk_indirect_list.append(hk_indirect)
        prev_id = text_id
        #text_by_id.append(noun)
        more_words = sent[index:]
        text_by_id.extend(more_words)
    return hk_direct_list, hk_indirect_list
    
hk_direct, hk_indirect = associate(corpus, associations, dict_sets)
corpus['direct_hk'] = hk_direct
corpus['indirect_hk'] = hk_indirect
    

corpus1 = corpus[corpus['direct_hk']!='not found']
#print(corpus1[:5]['hk_encoded'])
dictionary_accuracy = (np.abs(sum(corpus1['hk_encoded'])-sum(corpus1['direct_hk'])))/len(corpus1)
print('Original length was ', len(corpus))
print('Significant length for dictionary associations is', len(corpus1))
print('Dictionary Accuracy is ', dictionary_accuracy)
corpus1.to_csv(CORPUS_WITH_DICTIONARY, index=False)
corpus2 = corpus[corpus['indirect_hk']!='not found']
set_accuracy = (np.abs(sum(corpus2['hk_encoded'])-sum(corpus2['indirect_hk'])))/len(corpus2)
print('Significant length for set associations is', len(corpus2))
print('Set Accuracy is ', set_accuracy)
corpus2.to_csv(CORPUS_WITH_SET, index=False)

    
    
        
    