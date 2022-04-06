# https://docs.python.org/3/tutorial/modules.html#packages
import numpy as np
from sklearn.metrics import ConfusionMatrixDisplay
import matplotlib.pyplot as plt

def make_confusion_matrix(y_true, y_pred, labels, percentage=True, plot=True, size=15):
    """
    This function makes a confusion matrix.
    parameters:
        - y_true: list of true labels
        - y_pred: list of predicted labels
        - labels: list of label names (=> list of strings)
        - pecentage:
              - True (default) => the values in each row (that is for each actual class) a converted to percentages
              - False => keep raw counts
        - plot:
              - True (default) => plot confusion matrix
              - False => return confusion matrix as np.array
         - size: size of plot (15 by default)
    """
    y_true_flat = [y for y_true_i in y_true for y in y_true_i]
    y_pred_flat = [y for y_pred_i in y_pred for y in y_pred_i]
    idx_dict = {}
    dim = len(labels)
    for i in range(dim):
        idx_dict[labels[i]] = i
    conf_matrix = np.zeros((dim, dim))
    for i in range(len(y_true_flat)):
        row = idx_dict[y_true_flat[i]] # true label
        col = idx_dict[y_pred_flat[i]] # pred label
        conf_matrix[row, col] += 1
    if percentage==True:
        values_format = ".1f"
        for i in range(len(conf_matrix)):
            conf_matrix[i] *= 100/np.sum(conf_matrix[i])
    else:
        values_format = "d"
        conf_matrix = conf_matrix.astype(int)
    if not plot:
        return conf_matrix
    cmd = ConfusionMatrixDisplay(conf_matrix, display_labels=labels)
    fig, ax = plt.subplots(figsize=(size,size))
    cmd.plot(ax=ax, xticks_rotation="vertical", values_format=values_format)
    pass

# https://github.com/chakki-works/seqeval
from seqeval.scheme import IOB2
from seqeval.metrics import f1_score

def f1_strict_IOB2(y_true, y_pred):
    return f1_score(y_true, y_pred, mode="strict", scheme=IOB2)
