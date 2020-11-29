import abc

class Model(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def classify(self):
        pass

     
    @abc.abstractmethod
    def train(self):
        pass