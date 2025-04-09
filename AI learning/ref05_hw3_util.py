# -*- coding: utf-8 -*-
# *** Do not modify the code ***
import os
import nltk
import math
import json

from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
from pathlib import Path
from tqdm import tqdm, trange
from typing import *

nltk.download('punkt')                      
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')


class AI_util:
    def __init__(self):
        # Noun, Verb POS tags
        self.extract_specific_tags = ['NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
        self.stop_words = set(stopwords.words('english'))
        self.word2idx: Dict[str, int]
        self.label2idx: Dict[str, int]

    def load_data(self, data_path: Path, data_type: str) -> List[Tuple[str, List[str], str]]:
        # open data file
        with open(os.path.join(data_path + '{}.json'.format(data_type)), 'r', encoding='utf-8') as f:
            data = json.load(f)

        # declare variables
        t_data = list()
        t_token = set()
        labels = set()
        
        # process data
        for d in tqdm(data, desc='Tokenizing... : '):
            paragraph = d['paragraph']
            labels.add(d['label'])
            pos_tokens = nltk.pos_tag(word_tokenize(paragraph.lower()))
            tokenized_paragraph = [
                token[0] for token in pos_tokens
                if (token[1] in self.extract_specific_tags) and (not token[0] in self.stop_words)
            ]
            
            if data_type == 'train':
                t_token.update(tokenized_paragraph)
            
            t_data.append((d['id'], tokenized_paragraph, d['label']))
        
        if data_type == 'train':
            self.word2idx = {word: idx for idx, word, in enumerate(sorted(t_token))}
        
        self.label2idx = {label: idx for idx, label in enumerate(sorted(labels))}
        self.n_labels = len(self.label2idx)

        return t_data[:]