# -*- coding: utf-8 -*-

from ref05_hw4_util import *

class MLP:
    def __init__(self, input_size: int, hidden_size: int, output_size: int, learning_rate: float):
        # *** Do not modify here ***
        self.W1 = np.random.uniform(low = -0.01, high = 0.01, size = (hidden_size, input_size))
        self.B1 = np.random.uniform(low = -0.01, high = 0.01, size = (hidden_size, 1))
        self.W2 = np.random.uniform(low = -0.01, high = 0.01, size = (output_size, hidden_size))
        self.B2 = np.random.uniform(low = -0.01, high = 0.01, size = (output_size, 1))
        
        self.grad_W1 = np.zeros(self.W1.shape)
        self.grad_B1 = np.zeros(self.B1.shape)
        self.grad_W2 = np.zeros(self.W2.shape)
        self.grad_B2 = np.zeros(self.B2.shape)

        self.inputs = None
        self.hidden = None
        self.output = None
        self.label = None
        self.ReLU_mask = None

        self.lr = learning_rate


    def forward(self, x):
        # matric operation is needed (Wx+b)
        ### EDIT FROM HERE ###

        # 1 * input_size matrix -> input_size * 1
        self.inputs = np.transpose(x)
        
        # hidden_size * 1 matrix
        self.hidden = np.matmul(self.W1, self.inputs)
        self.hidden = np.add(self.hidden, np.transpose(self.B1))
        self.hidden = self.ReLU(self.hidden)
        self.hidden = np.transpose(self.hidden)
        
        # output_size * 1 matrix
        self.output = np.matmul(self.W2, self.hidden)
        self.output = np.add(self.output, self.B2)
        # output_size * 1 matrix -> ! * output_size
        self.output = self.softmax(np.transpose(self.output))
        # sotfmax is activation function of output function
        self.inputs = np.transpose(x)

        ### EDIT UNTIL HERE ###
        return self.output


    def backward(self):
        ### EDIT FROM HERE ###

        # initialize
        self.grad_W1 = np.zeros(self.W1.shape)
        self.grad_B1 = np.zeros(self.B1.shape)
        self.grad_W2 = np.zeros(self.W2.shape)
        self.grad_B2 = np.zeros(self.B2.shape)

        # factor
        t_probability = np.matmul(self.output, self.label) - 1

        ## get gradient
        # W2 and B2
        for k in range(len(self.B2)):
          if self.label[k]:
            temp = t_probability
          else:
            temp = self.output[0][k]
          # W2
          for j in range(len(self.W2[0])):
            if self.hidden[j] <= 0: continue; # if hidden value negative, no active
            self.grad_W2[k][j] = temp * self.hidden[j][0]
          # B2
          self.grad_B2[k] = temp
            
        # W1 and B1        
        for j in range(len(self.W2[0])):
          if self.hidden[j] <= 0: continue;   # if hidden value negative, no active
          temp_W2s = [ self.W2[k][j] for k in range(len(self.B2)) ]  # W2_jk, j is fixed
          W2_jt = np.matmul(temp_W2s, self.label)
          for k in range(len(self.B2)): temp_W2s[k] -= W2_jt         # W2_jk - W2_jt
          temp_W2s = np.multiply(temp_W2s, self.output)              # P(Z_k) * (W2_jk - W2_jt)
          temp_sum = np.sum(temp_W2s)
          # W1
          self.grad_W1[j] = np.multiply(self.inputs, temp_sum)
          # B1
          self.grad_B1[j] = temp_sum

        ### EDIT UNTIL HERE ###


    def step(self):
        # *** Do not modify here ***
        self.W1 -= self.lr * self.grad_W1
        self.W2 -= self.lr * self.grad_W2
        self.B1 -= self.lr * self.grad_B1
        self.B2 -= self.lr * self.grad_B2

    def loss(self, label, logits):
        # make label(int) to numpy array which shape is (num_label, 1)
        # numpy array is one-hot vector
        # return Cross Entropy Loss value
        ### EDIT FROM HERE ###

        self.label = np.zeros(len(self.B2))
        self.label[label - 1] = 1
        # logits : array of P
        return -(math.log(np.dot(logits, self.label)))

        ### EDIT UNTIL HERE ###

    def softmax(self, x):
        # return sofmax value        
        ### EDIT FROM HERE ###
        
        x = np.exp(x)
        Sum = np.sum(x)
        return np.divide(x, Sum)

        ### EDIT UNTIL HERE ###

    def ReLU(self, x):
        self.ReLU_mask = np.zeros(x.shape)
        self.ReLU_mask[x >= 0] = 1.0

        return np.multiply(self.ReLU_mask, x)
        
def main(data, label2idx):
    # *** Do not modify outside of the designated area***
    result = dict()
    for inp_type, tr, te in tqdm(data, desc='training & evaluating...'):
        train_inp = list()
        train_label = list()
        for d in tr:
            train_inp.append(d[-2])
            train_label.append(d[-1])

        test_inp = list()
        test_label = list()
        for d in te:
            test_inp.append(d[-2])
            test_label.append(d[-1])

        mlp = MLP(
            input_size=len(train_inp[0]), 
            hidden_size=400,
            output_size=len(label2idx),
            learning_rate=0.05
        )

        d = list(zip(train_inp, train_label))  

        # train data have to be shuffled
        # training epoch : 50
        ### EDIT FROM HERE ###

        # data = [ ('TF-IDF', tr_tfidf, te_tfidf) ]

        Sum = 0
        average = 0
        up_limit = 1.8
        down_limit = 0.2
        num_label = len(d)

        for epoch in range(50):
          print("\nepoch :", epoch + 1, "\n")
          for tfidf, t_label in d:
            logits = mlp.forward(tfidf)
            print(logits)
            loss_value = mlp.loss(t_label, logits)
            print(loss_value)
            Sum += loss_value
            if loss_value < down_limit:  continue
            mlp.backward()
            mlp.step()
            if loss_value < up_limit:  continue
            while( 1 ):
              loss_value = mlp.loss(t_label, mlp.forward(tfidf))
              if loss_value < up_limit:  break
              mlp.backward()
              mlp.step()
            print(loss_value, "\n")
          average = Sum/num_label
          if ( up_limit > average*2 ) and ( average > 0.1 ):    up_limit = average*1.5
          if ( down_limit > average*0.2 ) and ( average > 0.002 ):down_limit = average*0.5
          Sum = 0

        # (remove) result : Dict[ str, Dict[  str, Union[   Tuple[float, float, float, int], Tuple[float, int]   ]  ] ]
        
        ### EDIT UNTIL HERE ###

        correct = 0
        preds = list()
        label_correct = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
        for tfidf, label in zip(test_inp, test_label):
            logits = mlp.forward(tfidf)
            max_label = np.argmax(logits)
            preds.append(max_label)

            if max_label == label:
                correct += 1
                label_correct[label] += 1

        tmp_result = {
            'accuracy': ((correct / len(test_label)) * 100, len(test_label)),
        }
        for k, v in label2idx.items():
            precision = (label_correct[v] / preds.count(v)) if preds.count(v) != 0 else 0.0
            recall = (label_correct[v] / test_label.count(v)) if test_label.count(v) != 0 else 0.0
            f1 = (2 * (precision * recall) / (recall + precision)) if recall + precision != 0 else 0.0
            tmp_result[k] = (precision * 100, recall * 100, f1 * 100, test_label.count(v))

        micro_avg_pre = (sum(list(label_correct.values())) / len(test_label)) if len(test_label) != 0 else 0.0
        micro_avg_rec = (sum(list(label_correct.values())) / len(test_label)) if len(test_label) != 0 else 0.0
        micro_avg_f1 = 2 * (micro_avg_pre * micro_avg_rec) / (micro_avg_rec + micro_avg_pre) if micro_avg_rec + micro_avg_pre != 0 else 0.0
        tmp_result['micro avg'] = (micro_avg_pre * 100, micro_avg_rec * 100, micro_avg_f1 * 100, len(test_label))
        result[inp_type] = tmp_result

    save_result(result, std_name='test', std_id='test') 

if __name__ == "__main__":
    #   *** Do not modify the code below ***
    random.seed(42)
    np.random.seed(42)

    tr_tfidf, te_tfidf = calculate_tf_idf('./train.json','./test.json')

    data = [
        ('TF-IDF', tr_tfidf, te_tfidf)
        ]
    label2idx = {label: idx for idx, label in enumerate(['beauty', 'celebrity', 'movies', 'style'])}
    main(data,label2idx)
    #   *** Do not modify the code above ***