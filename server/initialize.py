from treemodel.tree import Tree

from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC

def init_tree():
    # choose which classifier model to use for the tree
    # models from scikit-learn should work out of the box
    # 
    # if you use a model from somewhere else it needs to have implemented a `fit` and `predict` methods
    # also needs to be able to ingest data the same way as scikit-learn models

    # A random example:
    #
    #   from sklearn import svm
    #   
    #   model = svm.SVC
    #   model_params = {'kernel': 'sigmoid',
    #                   'tol': '1e-5'}

    model = GaussianNB
    model_params = {}

    recommendation_tree = Tree(model, **model_params)

    return recommendation_tree
