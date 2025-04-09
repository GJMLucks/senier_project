# -*- coding: utf-8 -*-

from ref05_hw2_util import *

class Preprocessing(AI_util):
    def Calculate_TF_IDF_Normalization(self, data: List[Tuple[str, List[str], str]])  -> List[Tuple[str, List[str], str]]:    
        """
        (input) 'data' type : ('list')
        (input) 'data' format :   [(id, tokenized text, category)]
        -> Result of 'load_data' function in 'hw2_util' file (tokenized_data [List])

        (output) return type : ('list')
        (output) return format : [(article id, normalized tf-idf, category)]           
        """
        ### *** ↓ YOU SHOULD WRITE CODES FOR CALCULATING NORMALIZED TF-IDF ↓ *** #
        normalized_tf_idf = list()
        ### *** ↑ YOU SHOULD WRITE CODES FOR CALCULATING NORMALIZED TF-IDF ↑ *** #

        return normalized_tf_idf[:]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--document_id",
                        default=864,
                        type=int)
    args = parser.parse_args()

    ### Please write your own name and student ID. ###
    NAME = ""
    ID = ""
    
    Preprocessing = Preprocessing()
    train_data = Preprocessing.load_data(data_path='./train.json', data_type='train')
    Preprocessing.train_tfidf = Preprocessing.Calculate_TF_IDF_Normalization(data=train_data)
    test_data = Preprocessing.load_data(data_path='./test.json', data_type='test')
    Preprocessing.test_tfidf = Preprocessing.Calculate_TF_IDF_Normalization(data=test_data)

    Preprocessing.save_result(std_name=NAME, std_id =ID, document_id=args.document_id)