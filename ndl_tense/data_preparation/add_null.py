#import sys
from numpy import array, savetxt, transpose
from nltk import RegexpParser, tree

# Creates a parse tree (nltk.Tree) from a given tagged sentence
def apply_grammar(grammar, line):
    cp = RegexpParser(grammar)
    return cp.parse(line)

def run(infile, outfile, nphrase_file_path, noun_phrase_file = False):
    """
    add null tags to an input file (infile)

    ----
    PARAMETERS
    ----
    infile: file/str
        the file path to a .txt file with tags and tokens delimited by a tab space
    outfile: file/str
        the file path to a .txt file that is the same as the infile except
        with the addition of null tokens and tags in appropriate places (according to the grammar rules)
    nphrase_file_path: file/str
        the file path of a file (to be created) that stores the noun phrase chunks labelled by the grammar
    noun_phrase_file: bool
        whether to create the noun_phrase file or not
    ----
    RETURN
    ----
        creates two files, outfile and nphrase_file_path
    """
    # Grammar rules were arrived at from the noun-phrase finding,
    # Strictly speaking: not all of them are necessary for the naive null-tagger
    grammar = r"""
            GEN: {<POS|DPS|DT0><NN.*|VVB-NN.*>+}
            NPR1: {<AT0.*|DT0><|AJ.*>*<AJ0.*><NN.*><PRP.*><AT0.*><NN.*>}
            NullNPR1: {<AJ0.*><NN.*><PRP.*><AT0.*><NN.*>+}
            NPR2: {<AT.*|DT0><ORD><CRD>*<NN.*|VVB-NN.*>+}
            NullNPR2: {<ORD><CRD>*<NN.*|VVB-NN.*>+}
            NPR3: {<AT.*|DT0><ORD>*<CRD><NN.*|VVB-NN.*>+}
            NullNPR3: {<ORD>*<CRD><NN.*|VVB-NN.*>+}
            NPR4: {<AT.*|DT0><AJ.*|PP\$|DP.*|AV.*|>*<NN.*|VVB-NN.*|NP0-NN.*>+}
            NullNPR4: {<AJ.*>*<NN.*|VVB-NN.*|NP0-NN.*>+}
            """
    data_read = (line for line in open(infile, 'r', encoding="utf-8"))
    with open("%s.txt"%(outfile), 'w', encoding="utf-8") as f:
        if noun_phrase_file:
            nf = open("%s.txt"%(nphrase_file_path), 'w', encoding="utf-8")
        for line in data_read:
            #the line is a string in the form of tuples that represent a word and tag pair
            if '\\' in line:
                line = line.replace('\\', '#')
            eval_line = list(eval(line))
            #to store a sentence
            sen, tagged_words = [], []
            noun_chunk = apply_grammar(grammar, eval_line)
            #noun_chunk is a nltk Tree
            for n in noun_chunk:
                n_phrase = str(n)
                sen.append(n_phrase)

                #tags that had a rule applied have to be treated slightly differently
                if isinstance(n, tree.Tree):
                    if n_phrase.find("NullNPR") > 0:
                        #add a null tag to the beginning of the noun-phrase
                        tagged_words += [('ø', 'AT0')] + [w for w in n.leaves()]
                    else:
                        tagged_words += [w for w in n.leaves()]
                else:
                    tagged_words.append(n)
            for pair in tagged_words:
                f.write("%s\t%s\n"%(pair[0], pair[1]))
            if noun_phrase_file:
                nf.writelines(' '.join(sen))

        output_arr = transpose(array([array([w for w,t in tagged_words]), array([t for w,t in tagged_words])]))
        savetxt("%s.txt"%(outfile), output_arr, delimiter = "\t", encoding="utf-8", fmt='%s')
        #f.writelines(' '.join([tw[0] for tw in tagged_words]) + "\n")
        if noun_phrase_file:
            nf.close()