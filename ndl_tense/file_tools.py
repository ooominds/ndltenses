from os import path, mkdir, sep
import pandas as pd




############################
## FILE AND FOLDER CREATION
############################

def check_folder_exist(filepath):
    if path.isdir(filepath):
        return
    else:
        mkdir(filepath)

def create_directories(dir_path, sep_file_path, folder_depth):
    for i in range(folder_depth):
        dir_path = sep.join([dir_path, sep_file_path[i + 1]])
        check_folder_exist(dir_path)

def manage_directories(dir_list, FILE_DIREC):
    for filepath in dir_list:
        sep_file_path = filepath.split(sep)
        dir_path = sep_file_path[0]
        if FILE_DIREC:  
            create_directories(dir_path, sep_file_path, (len(sep_file_path) - 2))
        else:
            create_directories(dir_path, sep_file_path, (len(sep_file_path) - 1))

def create_file(files_list, ext):
    for filepath in files_list:
        if path.isfile(filepath):
            return
        else:
            mkdir(filepath)


############################
## SENTENCE EXTRACTION
############################


'''

    Parameters
    ----------
    data_gen: generator | should be of BNC
         a generator object - this is each line read from the input file

    n: int
        number of sentences to process
    Returns
    ----------

    sentences: list of (list of str) | size(length) = n
         each str is a pair consisting of a token and its tag, e.g. "('the', 'DT')"
         each list of str is a sentence
'''
def extract_n(data_gen, n):
    sen_count = 0
    sentences, sen_so_far = [], []
    while sen_count < n:
        line = next(data_gen)
        #split the line into tags and tokens
        token, tag  = line.strip('\n').split('\t')
        sen_so_far.append('("%s", "%s"),'%(token, tag))
        #marks a complete sentence
        if token.strip() in ['.','?','!']:
            sen_count += 1
            sentences.append(sen_so_far)
            sen_so_far = []
    return sentences

def extract_all(data_gen, n):
    sen_count = 0
    sentences, sen_so_far = [], []
    for line in data_gen:
        #split the line into tags and tokens
        token, tag  = line.strip('\n').split('\t')
        sen_so_far.append('("%s", "%s"),'%(token, tag))
        #marks a complete sentence
        if token.strip() in ['.','?','!']:
            sen_count += 1
            sentences.append(sen_so_far)
            sen_so_far = []
    return sentences

def extract_sentences(input_file, output_file, extract_all, length=20000):
    data_read = (line for line in open(input_file, 'r'))
    if extract_all:
        first_n = extract_all(data_read, length)
    else:
        first_n = extract_n(data_read, length)

    #My python version did not support the "encoding" parameter for the open() function
    #with open("500_tagged_sentences.txt", 'w', encoding= 'utf-8) as f:
    with open(output_file, 'w') as f:
        for line in first_n:
            f.writelines(" ".join(line) + "\n")


############################
## FIND TAG
############################



def find_article(line, word):    
    """
        Find an article relevant to a given word

        Variables
        ------------------------------------------

        line: list of str
            A list of words that make up a sentence
        word: str
            A word (noun), this is the word the article should apply to
        ------------------------------------------
        return:
            Either an article or None (if no article could be found)
    """
    i = line.index(word) - 1
    while i >= 0:
        if line[i] in ['The', 'the', 'a', 'an', 'An', 'A', 'no']:
            return line[i]
        else:
            i -= 1
    return None

def create_dict(nouns_list, articles_list, lookup_sentences_file):        
    """
        Create a dictionary where each key is a word and each key's value is
        an article that preceds the word
        
        ------------------------------------------------
        PARAMETERS
        ------------------------------------------------

        nouns_list: list of str
            a list of all the nouns with articles to be found
        articles_list: list of None
            a list that will store all the articles found for each word in nouns_list,
            this starts as a list of Nones
        lookup_sentences_file: path/str
            a file of sentences from which articles and words are found.
            A file like this can be created using create_sentence_file.py from ndl-tense's data_preparation
        ------------------------------------------------
        RETURN
        ------------------------------------------------
            a dictionary where each key is a word and each key's value is an article
    """
    n_article = dict(zip(nouns_list, articles_list))
    data_read = (line for line in open("%s.txt"%(lookup_sentences_file), 'r', encoding='utf-8'))

    for line in data_read:
        for word in n_article:
            strip_line = line.strip('\n').split()
            if word in strip_line:
                if n_article[word] == None:
                    n_article[word] = find_article(strip_line, word)
    return n_article

#return a string with its first char in uppercase
# e.g. "hello" ---> "Hello"
def upper_first_char(word_str):
    return(word_str[0].upper() + word_str[1:])

def find_tag(list_of_nouns_file,lookup_sentences_file,output_file="tagged_noun_articles"):
    """
        Create a file that associates nouns from a list with the article that immediately preceds it
        from a sentences file
        
        ------------------------------------------------
        PARAMETERS
        ------------------------------------------------
        
        list_of_nouns_file: str/path
            an .xlsx file containing a column of nouns
        lookup_sentences_file: str/path
            a .txt file that contains sentences from a corpus. The nouns in the list_of_nouns_file file should
            be found in these sentences
        output_file: str/path
            an .xlsx file that contains a column of nouns and a column of articles that precede the noun
            within the sentences
        ------------------------------------------------
        RETURN
        ------------------------------------------------
            creates output_file which is an .xlsx file that contains
            a column of nouns and a column of articles that precede the noun within the sentences

    """
    n_file = pd.read_excel(list_of_nouns_file, encoding='utf-8')
    nouns_list = n_file.iloc[:,0].to_list()
    nouns_list = [n for n in nouns_list if isinstance(n, str)]
    nones_list = [None]*len(nouns_list)
    nouns_dic = create_dict(nouns_list, nones_list,lookup_sentences_file)
    
    #find article for words that had the first letter in uppercase
    ucfc_nouns = [upper_first_char(k) for k in nouns_dic if nouns_dic[k] == None]
    ucfc_nones = [None]*len(ucfc_nouns)
    ucfc_dic = create_dict(ucfc_nouns, ucfc_nones,lookup_sentences_file)

    #find article for words that had to be capitalised
    uc_nouns = [key.upper() for key in ucfc_dic if ucfc_dic[key] == None]
    uc_nones = [None]*len(uc_nouns)
    uc_dic = create_dict(uc_nouns, uc_nones,lookup_sentences_file)

    #get rid of any "None" keys in ucfc_nouns and nouns_dic
    nouns_dic = {k:v for k, v in nouns_dic.items() if v != None}
    ucfc_dic = {k:v for k, v in ucfc_dic.items() if v != None}

    #put it all back together
    n_article = dict(nouns_dic)
    n_article.update(ucfc_dic)
    n_article.update(uc_dic)

    (words, articles) = zip(*n_article.items())
    to_save = {"nouns": list(words), "articles": list(articles)}
    pd.DataFrame(to_save).to_excel("%s.xlsx"%(output_file))


        