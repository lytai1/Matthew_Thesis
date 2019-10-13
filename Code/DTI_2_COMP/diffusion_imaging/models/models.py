from abc import (
    ABC,
    abstractmethod
)
import dipy.reconst.fwdti as fwdti

class Model(ABC):
    
    @abstractmethod
    def fit(data, mask):
        pass


class FreeWaterTensorModel(Model):

    def __init__(self, gradient_table):
        self.gradient_table = gradient_table
    
    def fit(self, data, mask):
        self.model = fwdti.FreeWaterTensorModel(self.gradient_table)
        self.f = self.model.fit(data, mask=mask)
        self.FA = self.f.fa
        self.MD = self.f.md
        
        return self