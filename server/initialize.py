from treemodel.tree import Tree

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


    # TODO: look into maybe trying 3 different classifiers (naive bayes, SVC, random forests classifier).
    # can also try more but need to get this show on the road!

    model = None
    model_params = None

    recommendation_tree = Tree(model, model_params)

    return recommendation_tree
