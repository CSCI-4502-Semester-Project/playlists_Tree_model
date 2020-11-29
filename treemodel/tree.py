import numpy as np

class TreeNode():
    def __init__(self, elem, label):
        self.elem = elem
        self.label = label # label to keep track of a playlists name, since elem will either be full of features, or None if a classifier is elem
        self.left = None
        self.right = None
        self.parent = None

    def is_leaf(self):
        return self.left is None and self.right is None

class Tree():
    # TODO: look into dumping parts of tree as *.pkl files, since we're gonna have a ton of nodes (roughly 2^log_2(1,000,000) ~= 2^20) that are either classifiers of fairly large data clouds. i.e. this will be eating up memory

    def __init__(self, node_model, **kwargs):
        self.model = node_model
        self.model_args = kwargs
        self.head = None
    
    def push(self, data, label, ret=False):
        if self.head is None:
            self.head = TreeNode(elem=data, label=label)
            return
        
        current = self.head
        parent_branch = 0

        while not current.is_leaf():

            # TODO: see if classify can handle a bunch of points, rather than just one off points
            branch = current.elem.classify(data)

            if branch == -1:
                current = current.left
                parent_branch = -1
            elif branch == 1:
                current = current.right
                parent_branch = 1
        
        # since we've hit a leaf node we have a recommended playlist
        # need to create a new classifier to distinguish between the 
        new_classifier = self.model(kwargs=self.model_args)

        # format data to be classified
        # all data passed in should be a 
        X = np.array([current.elem, data], dtype=np.float64)
        y = np.array([-1, 1], dtype=np.float64)

        # train new classifier
        new_classifier.fit(X, y)

        # create new nodes for the tree
        classifier_node = TreeNode(elem=new_classifier, label=None)
        new_playlist_node = TreeNode(elem=data, label='')

        # set the classifier nodes branches to is respective classification
        classifier_node.left = current
        classifier_node.right = new_playlist_node

        # update the parent classifier node's correct branch
        if parent_branch == -1:
            current.parent.left = classifier_node
        elif parent_branch == 1:
            current.parent.right = classifier_node

        # if the return flag is set, return recommended playlist name
        return current.elem.label if ret else None
        
        
        
        
