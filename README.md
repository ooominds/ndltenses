# ndltenses

A package for training an NDL model to learn tenses using pyndl; can also be used to annotate text for tense

## installation

This should be installable from PyPi so this means it requires pip. 
You can install the latest pip by typing "pip install pip".
From a terminal, type "pip install ndl=tense".
":$ pip install ndl-tense"

## parameter file

This file is what's used to tailor the execution of the processing to your needs. In the future I hope to create a GUI interface to avoid this.
In the GitHub repository there is an already created parameter file with example values set and default parameter file that you should use.

There are some necessary files (NF) that need to be created by yourself and stored in a directory referenced by the NF variable. 


## pipeline
---------------------------------------------------
The pipeline.py file (found in the GitHub repository) acts as a step-by-step guide to run the code from preparing the data (including annotation) of the English tense project to training an NDL model on this data.


#### Step I: Create sentences file from corpus file with verb tags 

- Folder variable: WD_EXTRACT
- Main file: create_sentence_file.py - this is in data_preparation, see pipeline.py as an example

#### Step II: Convert verb tags into tenses (tense annotation) 

- Folder variable: WD_ANNOTATE
- Main file: annotate_tenses.py (quite a long process, use the corresponding run function)
- Adds null articles and tags to sentences
- A function "Check_lengthy_sentences.R" used to find the 99% quantile of sentence lengths, to define sentence lengths will be added.
- Removed sentences with num words either < 3 or > 60 (1% and 99% quantiles)
 
#### Step III: Prepare event files 

- Folder variable: WD_PREPDAT
- File 1 (main): prepare_ndl_events.py (use corresponding run function)
   1)  Added the infinitives using the nltk toolkit
   2)  Removed sentences with no verb/tense
   3)  From the full set, created one row per tense/verb in each sentence. IMPORTANT NOTE: Some modals appear at 
       the end of a sentence (e.g. certainly they should). In such cases, the VerbForm, MainVerb and infinitive 
       are all empty, but that doesn't matter since these will not be considered as main events
   4)  Converted words in American English to British English using http://www.tysto.com/uk-us-spelling-list.html
   5)  Corrected the infinitives using Laurence list and some manual corrections + http://www.tysto.com/uk-us-spelling-list.html (for converting AE to BE)  
   6)  From the new full set, removed modals and imperatives
   7)  Added a column "VerbOrder" to check the order of the verb (e.g. 1st, 3rd).
   8)  Created contexts by removing the verb form and replacing it with the infinitive (words seperated with underscores)
   9)  Generated word cues from the context columns (cues with or without infinitives) - Added 2 columns
   10) Generated n-gram cues (from 1 to 4) from the context columns (cues with or without infinitives) - Added 2 columns 
   11) Shuffled the sentences while keeping the order of events within each sentence

- Folder variable 2: 
- File 2: Prepare_train_valid_test.py (use corresponding run function to use)
   -> Splited the data into training (90%), validation (5%) and test (5%) sets. The split was done 
      at the level of sentences NOT events.

- File 3: prepare_ndl_events.py (use corresponding run function to use)
   -> This prepare .gz event files ready to be used with NDL

- Note: I prepared two dataset types: 'multiverbs' contains complex sentences with more than one verb 
        while 'oneverb' contains only sentences that have a single verb. The "one verb" version is currently not in use.

#### Step IV: Prepare the infinitive cues to use

- Folder variable: WD_EXTRACT_INF
- File 1 (main): extract_infinitive.py  (use corresponding run function to use)
- File 2: Extract_infinitive_freqs_oneverb.py (for the dataset containing only sentences with a single verb)

-> Created a list of all possible infinitives with their co-occurence frequencies with each tense
-> Extracted the list of all infinitives that have a freq > 10 to be used as lexical cues

#### Step V: Prepare the n-gram cues to use 

- Folder variable:  WD_EXTRACT_NGRAM
- File 2: prepare_ngrams.py (there is also code for the 'oneverb' data set but this is not currently in use)
-> Extracted a list of n-grams to include in the training (10k most frequent from each level n + all have freq>10)

#### Step VI: Prepare the n-gram cues to use 

- Folder variable: WD_CUES
- File 1 : prepare_cues.py (There is also code for the 'oneverb' data set but this is not currently in use)
-> Created a separate list of all n-grams for each level n (1 to 4) with their frequency in the dataset  

#### Step VII: Prepare the n-gram cues to use 

- Folder variable: WD_SIM
- File 1: ndl_model
-> Train an NDL model

## null tagger
---------------------------------------------------
A naive null tagger for .txt input files formatted with one column representing tags and the other representing tokens.
The tags are reduced BNC tags.

Grammar used for the null tagger {
            GEN: {<POS|DPS|DT0><NN.*|VVB-NN.*>+}
            NPR1: {<AT0.*|DT0><|AJ.*>*<AJ0.*><NN.*><PRP.*><AT0.*><NN.*>}
            NullNPR1: {<AJ0.*><NN.*><PRP.*><AT0.*><NN.*>+}
            NPR2: {<AT.*|DT0><ORD><CRD>*<NN.*|VVB-NN.*>+}
            NullNPR2: {<ORD><CRD>*<NN.*|VVB-NN.*>+}
            NPR3: {<AT.*|DT0><ORD>*<CRD><NN.*|VVB-NN.*>+}
            NullNPR3: {<ORD>*<CRD><NN.*|VVB-NN.*>+}
            NPR4: {<AT.*|DT0><AJ.*|PP\$|DP.*|AV.*|>*<NN.*|VVB-NN.*|NP0-NN.*>+}
            NullNPR4: {<AJ.*>*<NN.*|VVB-NN.*|NP0-NN.*>+}
 }


## contributors
---------------------------------------------------
This packages is based on code written for R by Adnane Ez-zizi - date of last change 06/08/2020. This code was corrected, updated and adapted as a Python package by Tekevwe Kwakpovwe, completed August 2021. Changes are listed in the ![changes file](changes.txt)

The tense-aspect annotation heuristics were provided by Dagmar Hanzlikova, Laurence Romain and Dagmar Divjak.

Work by all contributors was funded by Leverhulme Trust Leadership Award RL-2016-001 to Dagmar Divjak.
