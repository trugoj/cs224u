import nltk
from sklearn.metrics import classification_report, r2_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_validate
from sklearn.model_selection import GridSearchCV
import torch
import torch.nn as nn

#from torch_model_base import TorchModelBase
#from torch_shallow_neural_classifier import TorchShallowNeuralClassifier
from torch_rnn_classifier import TorchRNNDataset, TorchRNNClassifier, TorchRNNModel
import utils

import pandas as pd
from collections import Counter
import json

PATH="/home/martin/dev/cs224u/base_data/martin/"

def load_annotations():
    with open(PATH + 'annotations2.jsonl') as jsonl_file:
    # note: after running data-preprocessing.ipynb this file already has token-level labels
        lines = jsonl_file.readlines()
    annot = [json.loads(line) for line in lines]

    return annot

def get_data(annot):
    # now get data into format that TorchRNN expects:
    X=[] 
    y=[]
    for j in range(0,len(annot)):
        a = annot[j]['tokens']
        auxX = []
        auxy = []
        if annot[j]['spans']!=[]: # are there annot for this example?
            for i in range(0,len(a)):
                #token_element = (a[i]['text'],a[i]['label'])
                auxX.append(a[i]['text'])
                auxy.append(a[i]['label'])
            X.append(auxX)
            y.append(auxy)
    #X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    X_train, X_test, y_train, y_test = X[:120], X[120:], y[:120], y[120:]
    vocab = sorted({w for seq in X_train for w in seq}) + ["$UNK"]

    return X_train, X_test, y_train, y_test, vocab

def run():
    annot = load_annotations()
    X_train, X_test, y_train, y_test, vobac = get_data(annot)

if __name__ == '__main__':
    run()