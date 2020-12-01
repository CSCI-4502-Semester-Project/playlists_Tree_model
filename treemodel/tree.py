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
        parent_branch = -1

        while not current.is_leaf():

            branch = np.average(current.elem.predict(data))

            if branch < 0.5:
                current = current.left
                parent_branch = 0
            else:
                current = current.right
                parent_branch = 1
        
        # since we've hit a leaf node we have a recommended playlist
        # need to create a new classifier to distinguish between the 
        new_classifier = self.model(**self.model_args)

        # format data to be classified

        # attempt to fix class imbalances
        # take a random sample from the larger class so that the sample size is the same size as smaller class

        # determine which playlist to sample
        small, sample = ((current.elem , 'l'), (data, 'r')) if current.elem.shape[0] < data.shape[0] else ((data, 'r'), (current.elem, 'l'))
        N = small[0].shape[0]
        # only sample if they are not the same size
        sample = (sample[0][np.random.choice(a=sample[0].shape[0], size=N, replace=False), :], sample[1]) if N != sample[0].shape[0] else sample

        # determine order to concatenate based on if it should be the right or left node
        # this way we can put the correct full size playlist dataset with the correct node and not continually truncate data
        # in this case, the left branch data (from current.elem) always goes first and is associated with '0' in y array
        x_concat = (small[0], sample[0]) if small[1] == 'l' else (sample[0], small[0])

        X = np.concatenate(x_concat)
        y = np.concatenate((np.zeros(N), np.ones(N)))

        # train new classifier
        new_classifier.fit(X, y)

        # create new nodes for the tree
        classifier_node = TreeNode(elem=new_classifier, label=None)
        new_playlist_node = TreeNode(elem=data, label=label)

        # set the classifier nodes branches to is respective classification
        classifier_node.left = current
        classifier_node.right = new_playlist_node

        # update the parent classifier node's correct branch
        # also update the new classifiers parent node to be the current node's parent
        if parent_branch == 0:
            current.parent.left = classifier_node
            classifier_node.parent = current.parent
        elif parent_branch == 1:
            current.parent.right = classifier_node
            classifier_node.parent = current.parent
        else:
            self.head = classifier_node # no parent, which means it is the head

        # update parent of the data nodes
        current.parent = classifier_node
        new_playlist_node.parent = classifier_node

        # if the return flag is set, return recommended playlist name
        return current.label if ret else None
        