from abc import ABC, abstractmethod

class BaseReader(ABC):
    def __init__(self, filepath):
        self.filepath = filepath

    @abstractmethod
    def read(self):
        '''Read file and return structured data (list, dict, DataFrame, etc.).'''
        pass
