# -*- coding: utf-8 -*-
 # *** Do not modify the code ***
import argparse
import json
import nltk
import numpy as np
import math
import random

from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from pathlib import Path
from tqdm import tqdm, trange
from typing import Union, List, Dict, Tuple, Optional

from sklearn.feature_extraction.text import TfidfVectorizer

nltk.download('punkt')                      
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')

def calculate_tf_idf(trpath, tepath):
    label2idx = {label: idx for idx, label in enumerate(['beauty', 'celebrity', 'movies', 'style'])}
    
    # file settings
    with open(trpath, 'r', encoding='utf-8') as f:
        trdata = json.load(f)
    with open(tepath, 'r', encoding='utf-8') as f:
        tedata = json.load(f)
    
    # 
    tr_data = list()
    te_data = list()
    
    # training data
    trp = list()
    for d in tqdm(trdata, desc='Reading train data : '):
        paragraph = d['paragraph']
        trp.append(paragraph)

    # test data
    tep = list()
    for d in tqdm(tedata, desc='Reading test data : '):
        paragraph = d['paragraph']
        tep.append(paragraph)

    vectorizer = TfidfVectorizer()

    trainX = vectorizer.fit_transform(trp)
    testX = vectorizer.transform(tep)
    trainX = trainX.todense().tolist()
    testX = testX.todense().tolist()

    for i, value in enumerate(trainX):
        tr_data.append((trdata[i]['id'], value, label2idx[trdata[i]['label']]))
    for i, value in enumerate(testX):
        te_data.append((tedata[i]['id'], value, label2idx[tedata[i]['label']]))

    return tr_data, te_data



def save_result(result: Dict[str, Dict[str, Union[Tuple[float, float, float, int], Tuple[float, int]]]], 
                std_name: Optional[str] = None, 
                std_id: Optional[str] = None):
    output_path = Path('./{}_{}.txt'.format(std_name, std_id))
    with open(output_path, mode='w', encoding="utf-8") as f:
        for inp_type in ['TF-IDF']:
            tmp = result[inp_type]
            label_name = ['beauty', 'celebrity', 'movies', 'style']
            
            headers = ["precision", "recall", "f1-score", "# docs"]
            name_width = max(len(cn) for cn in label_name)
            width = max(name_width, len('micro avg'))
            head_fmt = '{:>{width}s} ' + ' {:>9}' * len(headers)
            report = head_fmt.format('', *headers, width=width) + '\n\n'
            row_fmt = '{:>{width}s} ' + ' {:>9.2f}' * 3 + ' {:>9}\n'
            for label in label_name:
                report += row_fmt.format(
                    label, 
                    tmp[label][0], 
                    tmp[label][1], 
                    tmp[label][2], 
                    tmp[label][3], 
                    width=width
                )
            row_fmt_accuracy = '{:>{width}s} ' + \
                                ' {:>9.2}' * 2 + ' {:>9.2f}' + \
                                ' {:>9}\n'
            report += '\n' + row_fmt.format(
                'micro avg',
                tmp['micro avg'][0], 
                tmp['micro avg'][1], 
                tmp['micro avg'][2], 
                tmp['micro avg'][3], 
                width=width
            )
            report += row_fmt_accuracy.format(
                'accuracy', 
                '', 
                '', 
                tmp['accuracy'][0], 
                tmp['accuracy'][1], 
                width=width
            )

            f.write('Input Type : {}\n'.format(inp_type))
            f.write(report + '\n')
