__author__ = "Christopher Potts"
__version__ = "CS224u, Stanford, Spring 2021"

import nltk
from sklearn.datasets import load_iris, load_boston
from sklearn.metrics import classification_report, r2_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_validate
from sklearn.model_selection import GridSearchCV
import torch
import torch.nn as nn

from torch_model_base import TorchModelBase
#from torch_shallow_neural_classifier import TorchShallowNeuralClassifier
from torch_rnn_classifier import TorchRNNDataset, TorchRNNClassifier, TorchRNNModel
import utils

# Ensure that the CoNLL dataset is present. If this function call
# raises errors, you might need to go through the steps of
# installing the NLTK data: https://www.nltk.org/data.html

nltk.download("conll2002")

def sequence_dataset():
    train_seq = nltk.corpus.conll2002.iob_sents('esp.train')
    X = [[x[0] for x in seq] for seq in train_seq]
    y = [[x[2] for x in seq] for seq in train_seq]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.33, random_state=42)
    vocab = sorted({w for seq in X_train for w in seq}) + ["$UNK"]
    return X_train, X_test, y_train, y_test, vocab

X_seq_train, X_seq_test, y_seq_train, y_seq_test, seq_vocab = sequence_dataset()

print("train example X: ", X_seq_train[0][: 8])
print("train example y: ", y_seq_train[0][: 8])

class TorchSequenceLabeler(nn.Module):
    def __init__(self, rnn, output_dim):
        super().__init__()
        self.rnn = rnn
        self.output_dim = output_dim
        if self.rnn.bidirectional:
            self.classifier_dim = self.rnn.hidden_dim * 2
        else:
            self.classifier_dim = self.rnn.hidden_dim
        self.classifier_layer = nn.Linear(
            self.classifier_dim, self.output_dim)

    def forward(self, X, seq_lengths):
        outputs, state = self.rnn(X, seq_lengths)
        outputs, seq_length = torch.nn.utils.rnn.pad_packed_sequence(
            outputs, batch_first=True)
        logits = self.classifier_layer(outputs)
        # During training, we need to swap the dimensions of logits
        # to accommodate `nn.CrossEntropyLoss`:
        if self.training:
            return logits.transpose(1, 2)
        else:
            return logits

class TorchRNNSequenceLabeler(TorchRNNClassifier):

    def build_graph(self):
        rnn = TorchRNNModel(
            vocab_size=len(self.vocab),
            embedding=self.embedding,
            use_embedding=self.use_embedding,
            embed_dim=self.embed_dim,
            rnn_cell_class=self.rnn_cell_class,
            hidden_dim=self.hidden_dim,
            bidirectional=self.bidirectional,
            freeze_embedding=self.freeze_embedding)
        model = TorchSequenceLabeler(
            rnn=rnn,
            output_dim=self.n_classes_)
        self.embed_dim = rnn.embed_dim
        return model

    def build_dataset(self, X, y=None):
        X, seq_lengths = self._prepare_sequences(X)
        if y is None:
            return TorchRNNDataset(X, seq_lengths)
        else:
            # These are the changes from a regular classifier. All
            # concern the fact that our labels are sequences of labels.
            self.classes_ = sorted({x for seq in y for x in seq})
            self.n_classes_ = len(self.classes_)
            class2index = dict(zip(self.classes_, range(self.n_classes_)))
            # `y` is a list of tensors of different length. Our Dataset
            # class will turn it into a padding tensor for processing.
            y = [torch.tensor([class2index[label] for label in seq])
                 for seq in y]
            return TorchRNNDataset(X, seq_lengths, y)

    def predict_proba(self, X):
        seq_lengths = [len(ex) for ex in X]
        # The base class does the heavy lifting:
        preds = self._predict(X)
        # Trim to the actual sequence lengths:
        preds = [p[: l] for p, l in zip(preds, seq_lengths)]
        # Use `softmax`; the model doesn't do this because the loss
        # function does it internally.
        probs = [torch.softmax(seq, dim=1) for seq in preds]
        return probs

    def predict(self, X):
        probs = self.predict_proba(X)
        return [[self.classes_[i] for i in seq.argmax(axis=1)] for seq in probs]

    def score(self, X, y):
        #print(f"score X: {X}")
        #print(f"score y: {y}")
        preds = self.predict(X)
        flat_preds = [x for seq in preds for x in seq]
        flat_y = [x for seq in y for x in seq]
        return utils.safe_macro_f1(flat_y, flat_preds)

seq_mod = TorchRNNSequenceLabeler(
    seq_vocab,
    early_stopping=True,
    eta=0.001)

_ = seq_mod.fit(X_seq_train, y_seq_train)

print( seq_mod.score(X_seq_test, y_seq_test) )