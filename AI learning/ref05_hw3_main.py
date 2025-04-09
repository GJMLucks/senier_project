#   *** Do not import any library except already imported libraries ***

import argparse
import logging
# logging : logging is a standard library module that provides a flexible framework for emitting log messages from Python programs.
# reference : https://docs.python.org/ko/3/howto/logging.html

import os
# os : This module provides a way of using operating system dependent functionality.
# it use for file path
# reference : https://docs.python.org/ko/3/library/os.path.html#module-os.path

from pathlib import Path
import json
import math
import numpy as np
# numpy : NumPy is the fundamental package for scientific computing with Python.
# reference : https://numpy.org/doc/stable/user/whatisnumpy.html

from tqdm import tqdm, trange
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
# sklearn.metrics : Simple and efficient tools for predictive data analysis, metrics used in results
# Score functions, performance metrics, pairwise metrics and distance computations.
# reference : https://scikit-learn.org/stable/api/sklearn.metrics.html

from ref05_hw3_util import AI_util


class Naive_Bayes(AI_util):
    def __init__(self, data_path):
        super(Naive_Bayes, self).__init__()

    def predict(self, test_data: list):
        """
        In this function, you have to predict the labels of test dataset.
        Also, save article ids and values of predicted labels.
        Do not use labels in test_data. It's not for the predict function.
        """
        # declare variables
        ids = list()        # article ids
        preds = list()      # predicted labels
        values = list()     # log probabilities of predicted labels

        # processing predictions
        for data in test_data:
            # initailize
            labels_values = [0 for idx in range(len(self.label2idx))]
            # ids
            ids.append(data[0])
            # get value
            for word in data[1]:
                if word[0] in self.word2idx:
                    for idx in range(len(labels_values)):
                        labels_values[idx] += self.cond_prob[idx][self.word2idx[word[0]]]

            temp_max = max(labels_values)
            # value and pred
            for idx in range(len(labels_values)):
                if temp_max == labels_values[idx]:
                    values.append(temp_max)
                    preds.append(idx)
                    break

        return ids, preds, values
    
    
    def calc_prior(self, train_data: list):
        """
        In this function, you have to calculate prior probabilities p(category) with training dataset.
        You have to save each probability in each suitable value of 'self.prior'
        Then, you can use 'self.prior' in predict function.
        """
        
        self.prior = {'beauty':0.0, 'celebrity':0.0, 'movies':0.0, 'style':0.0}

        ### EDIT FROM HERE ###

        item_label  = self.label2idx.items()
        num_labels  = [0, 0, 0, 0]
        num_doc     = 0

        for data in train_data:
            num_doc += 1
            for label, idx in item_label:
                if data[2] == label:
                    num_labels[idx] += 1
                    break
            
        for label, idx in item_label:
            self.prior[label] = num_labels[idx] / num_doc

        return self.prior
        ### EDIT UNTIL HERE ###

    
    def calc_conditional_prob(self, train_data: list):
        """
        In this function, you have to calculate conditional probabilities(likelihood) with training dataset.
        You can choose data structure of 'self.cond_prob' as whatever you want to use.
        Then, you can use it in predict function.

        You should remember that you use '0.5' for additive smoothing.
        """
        self.cond_prob = None

        ran_lable = range(len(self.label2idx))
        ran_word  = range(len(self.word2idx))

        # initialize
        cond_prob = [ [ 0.5 for word in ran_word ] for label in ran_lable ]

        # tf # (d['id'], tokenized_paragraph, d['label'])
        for data in train_data:
            for word in data[1]:
                if word[0] in self.word2idx:
                    cond_prob[self.label2idx[data[2]]][self.word2idx[word[0]]] += 1

        # sum of tf
        sum_log2tf = [0, 0, 0, 0]

        for label in ran_lable:
            for word in ran_word:
                sum_log2tf[label] += cond_prob[label][word]

        # take logerithm
        for label in ran_lable:
            sum_log2tf[label] = math.log2(sum_log2tf[label])
            for word in ran_word:
                cond_prob[label][word] = math.log2(cond_prob[label][word]) - sum_log2tf[label]
        
        self.cond_prob = cond_prob

        return cond_prob
        ### EDIT UNTIL HERE ###


def main(args, logger):
    data_path = os.path.join('./')

    nb_classifier = Naive_Bayes(data_path)
    logger.info("Classifier is initialized!")

    train_data = nb_classifier.load_data(data_path, 'train')
    logger.info("# of train data: {}".format(len(train_data)))
    test_data = nb_classifier.load_data(data_path, 'test')
    logger.info("# of test data: {}".format(len(test_data)))

    prior = nb_classifier.calc_prior(train_data)
    cond_prob = nb_classifier.calc_conditional_prob(train_data)
    labels = [nb_classifier.label2idx[y] for _, _, y in test_data]
    ids, preds, values = nb_classifier.predict(test_data)

    accuracy = round(accuracy_score(labels, preds), 2)

    logger.info("Accuracy: {}%".format(accuracy * 100))

    nlabel = nb_classifier.label2idx[args.selected_label]
    with open(args.output_dir/'{}_{}.txt'.format(args.std_name, args.std_id), 'w', encoding='utf-8') as f:
        f.write("Accuracy: {}%\n".format(str(accuracy * 100)))
        f.write("Prior of movies: {}\n".format(str(prior[args.selected_label])))
        f.write("Likelihood of movies: {}\n".format(str(cond_prob[nlabel][:10])))
        for i, val, pred in zip(ids, values, preds):
            if pred == nlabel:
                f.write("{}\t{}\t{}\n".format(i, args.selected_label, round(val, 2)))
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--std_name',
                        type=str,
                        default='유상범',
                        help='Student name.')
    parser.add_argument('--std_id',
                        type=str,
                        default="2017313144",
                        help='Student ID')

    parser.add_argument('--selected_label',
                        type=str,
                        default='movies',
                        help="Label to write its scores down to output text file.")
    parser.add_argument('--output_dir',
                        type=Path,
                        default=Path('./'),
                        help="Path where output will be saved.")
    args = parser.parse_args()

    logging.basicConfig(format = '%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt = '%m/%d/%Y %H:%M:%S',
                    level = logging.INFO)
    logger = logging.getLogger(__name__)

    main(args, logger)