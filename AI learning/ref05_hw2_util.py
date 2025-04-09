# -*- coding: utf-8 -*-
# reference: university lecture, AI basic, HW2

import argparse

# arg[uments]parse : command line arguments parser
# https://docs.python.org/ko/3/library/argparse.html

import json

# json : JavaScript Object Notation, built-in JSON encoder and decoder
# reference: https://docs.python.org/ko/3/library/json.html

import nltk

# nltk : Natural Language Toolkit, platform for building Python programs to work with human language data
# reference: https://www.nltk.org/

import math

# math : mathematical functions, defined by the C standard
# reference: https://docs.python.org/ko/3/library/math.html


from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
from pathlib import Path

from tqdm import tqdm, trange
# Arabic word taqaddum means "progress", it show progress bar
# https://docs.python.org/ko/3/library/math.html

from typing import *

nltk.download('punkt')                      
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')


class AI_util:
    def __init__(self):
        # We will only calculate tf-idf for Noun and Verb Pos tags.
        self.extract_specific_tags = ['NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
        # You should extract stop words when calculating tf idf. Stop words consist of common words like 'the'
        self.stop_words = set(stopwords.words('english'))
        # Word to Index : Each word should have its index.
        self.word2idx: Dict[str, int]

        self.train_tfidf: List[Tuple[str, List[float], str]]
        self.test_tfidf: List[Tuple[str, List[float], str]]


    def load_data(self, data_path: Path, data_type: str = 'train') -> List[Tuple[str, List[str], str]]:        
        """ 
        *** Instruction for Text Preprocessing ***
        
        1. You have to use 'word_tokenize' function to tokenize each text. ('word_tokenize' function is already imported from nltk.tokenize.)
        2. You must lower the cases of all the texts. (ex. 'Word' -> 'word')
        3. Be aware that we are only going to use specific pos tags (Noun and Verb). Check 'self.extract_specific_tags'.
           If tokenized word is neither of noun or verb, you do not have to care about the word.
        4. Please use 'nltk.pos_tag' function for pos tagging.
        5. For stop words, check 'self.stop_words'.
        
        
        You should save your preprocessed results in this two variables, or you might get error codes.
        It is not mandatory to use these variables, but in that case, you need to change all the variables and make sure it does not make any errors.
        
        1. tokenized_data [List] : Tokenized Data [List] is for saving preprocessed texts.(RETURN VALUE of this 'load_data' function)
        2. tokenized_paragraph [List] : Tokenized Paragraph [List] is a temporary list. Preprocess each paragraph and save it in the list.
                                        This list will be appended to 'tokenized_data' list in line 81.
        
        +) tokenized_tokens [Set] : Tokenized Tokens [Set] is for making the word2idx. The word2idx has all the unique words from the train dataset. 
                                    You do not have to implement anything about this list.
        """

        # create a data file
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # declare the data
        tokenized_data = list()
        tokenized_tokens = set()
        
        # tokenize the data
        for d in tqdm(data, desc='Tokenizing... : '):
            paragraph = d['paragraph']
            ### *** ↓ YOU SHOULD WRITE CODES FOR PARAGRAPH TEXT PREPROCESSING ↓ *** #
            tokenized_paragraph = word_tokenize(paragraph)
            ### *** ↑ YOU SHOULD WRITE CODES FOR PARAGRAPH TEXT PREPROCESSING ↑ *** #

            if data_type == 'train':
                tokenized_tokens.update(tokenized_paragraph)
            
            tokenized_data.append((d['id'], tokenized_paragraph, d['label']))
        
        # Word to Index Dictionary is composed of words from the train dataset.
        if data_type == 'train':
            self.word2idx = {word: idx for idx, word, in enumerate(sorted(tokenized_tokens))}

        return tokenized_data[:]


    def Calculate_TF_IDF_Normalization(self):
        return


    def save_result(self, std_name: Optional[str] = None, std_id: Optional[str] = None, document_id: Optional[int] = None) -> None:
        output_path = Path('./hw2_{}_{}.txt'.format(std_name, std_id))
        with open(output_path, mode='w', encoding="utf-8") as f:
            f.write('Train Data Length : {} | TF-IDF Length : {}\n'.format(len(self.train_tfidf), len(self.train_tfidf[0][1])))
            f.write('Test Data Length : {} | TF-IDF Length : {}\n'.format(len(self.test_tfidf), len(self.test_tfidf[0][1])))
            if document_id is not None:
                if document_id < 801:
                    data = self.train_tfidf[document_id-1]
                else:
                    data = self.test_tfidf[document_id-len(self.train_tfidf)-1]
                normalized_tf_idf = [str(value) for value in data[1] if not value == 0]
                f.write("{}\t{}\t{}\n".format(data[0], '\t'.join(normalized_tf_idf), data[2]))