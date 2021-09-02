from nltk import RegexpParser, tree
import pandas as pd

# Creates a parse tree (nltk.Tree) from a given tagged sentence
def apply_grammar(grammar, line):
    cp = RegexpParser(grammar)
    return cp.parse(line)

def run(input_file, output_file, nphrase_file):
    data_read = (line for line in open(input_file, 'r'))
    sents_df = pd.DataFrame({"sentence": [],"comments": [], "chunk": [], "target_chunk": []})
    chunk_df = pd.DataFrame({"chunk":[]})

    #My python version did not support the "encoding" parameter for the open() function
    #with open("500_tagged_sentences.txt", 'w', encoding= 'utf-8) as f:
    grammar = r"""
                NPR1: {<AT0.*><AJ0.*><NN1.*><PRP.*><AT0.*><NN1.*>}
                NPR2: {<AT0.*><NN1.*><PRP.*><AT0.*><AJ0.*><NN1.*>}
                NPR3: {<NN1.*><PRF.*><AT0.*><NN1.*>}
                NPR4: {<AT.*><ORD><CRD>?<NN.*|VVB-NN.*>}
                NPR5: {<AT.*|CRD><NN.*|VVB-NN.*>}
                NPR6: {<AT.*|PP\$|DP.*|DT.*|AV.*|NP.*>+<AJ.*>*<CJC>*<AJ.*>*<NN.*>+}
                NPR8: {<NN.*|VVB-NN.*>+}
                NPR9: {<NPR.*><CJC><NPR.*>}
                NPR10: {<NPR.*>+<PRF|CJC|PRP>+<AJ.*|NN.>*<NPR.*>}
              """
    grammar = r"""
                NPR1: {<AT0.*|AJ.*><AJ0.*><NN.*><PRP.*><AT0.*><NN.*>}
                NPR2: {<AT0.*|AJ.*><NN.*><PRP.*><AT0.*><AJ0.*><NN.*>}
                NPR3: {<AT0.*|AJ.*|AT.*|PP\$|DP.*|DT.*|AV.*|>+<NN.*><PRF.*><AT0.*><AJ0.*>*<NN.*>}
                NPR4: {<AT.*><ORD><CRD>?<NN.*|VVB-NN.*>}
                NPR5: {<AT.*|CRD><NN.*|VVB-NN.*>}
                NPR6: {<AT.*|PP\$|DP.*|DT.*|NP.*|AV0.*>+<AJ.*>*<CJC>*<AJ.*>*<NN.*>+}
                NPR8: {<NN.*|VVB-NN.*|NP0-NN.*>+}
                NPR7: {<AT.*|DT.*>?<NN.*|VVB-NN.*|NP0-NN.*><VVN-NND>}
                NPR9: {<AT0.*|AJ.*|AT.*|PP\$|DP.*|DT.*|AV.*|>?<PRP|PRF>?<NPR.*><CJC><NPR.*>}
                NPR10: {<AT0.*|AJ.*|AT.*|PP\$|DP.*|DT.*|AV.*|>?<PRP|PRF>?<NPR.*>+<PRF|CJC|PRP>+<AJ.*|NN.>*<NPR.*>}
               """
    grammar = r"""
                NPR1: {<AT0.*|AJ.*><AJ0.*><NN.*><PRP.*><AT0.*><NN.*>}
                NPR2: {<AT0.*|AJ.*><NN.*><PRP.*><AT0.*><AJ0.*><NN.*>}
                NPR3: {<AT0.*|AJ.*|AT.*|PP\$|DP.*|DT.*|AV.*|>+<NN.*><PRF.*><AT0.*><AJ0.*>*<NN.*>}
                NPR4: {<AT.*><ORD><CRD>?<NN.*|VVB-NN.*>}
                NPR5: {<AT.*|CRD><NN.*|VVB-NN.*>}
                NPR6: {<AT.*|PP\$|DP.*|DT.*|NP.*|AV0.*>+<AJ.*>*<CJC>*<AJ.*>*<NN.*>+}
                NPR8: {<NN.*|VVB-NN.*|NP0-NN.*>+}
                NPR7: {<AT.*|DT.*>?<NN.*|VVB-NN.*|NP0-NN.*><VVN-NND>}
                NPR9: {<AT0.*|AJ.*|PP\$|DP.*|DT.*|AV.*|>?<PRP|PRF>?<NPR.*><CJC><NPR.*>}
                NPR10: {<NPR.*>+<PRF|CJC|PRP>+<AJ.*|NN.>*<NPR.*>}
               """
    with open("%s.txt"%(output_file), 'w') as f:
        nf = open(nphrase_file, 'w')
        for line in data_read:
            line = list(eval(line))
            sentence = []
            n_phrase_list = []                 
            noun_chunk = apply_grammar(grammar, line)
            for n in noun_chunk:
                if isinstance(n, tree.Tree):
                    # adding the noun-phrase to create the sentence
                    n_phrase = str(n)
                    n_phrase_list.append(n_phrase)
                    sentence.append(n_phrase)
                    chunk_df = chunk_df.append(pd.DataFrame([n_phrase,""], columns = chunk_df.columns))
                else:
                    sentence.append(str(n))
            nf.writelines(" ".join(n_phrase_list) + "\n")
            f.writelines(" ".join(sentence) + "\n")
            sents_df = sents_df.append({"sentence": " ".join(sentence),"comments": '', "chunk": n_phrase_list, "target_chunk": ''}, ignore_index=True)
        nf.close()
    sents_df.to_excel("%s.xlsx"%(output_file), index=False)
    chunk_df.to_excel("%s_chunks.xlsx"%(output_file), index=False)