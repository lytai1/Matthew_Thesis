from abc import ABC, abstractmethod
from dependency_injector import providers, containers
from dipy.core.gradients import gradient_table
import nibabel as nib
import os
import numpy as np



class HandlerBase(ABC):
    """
    Base class for the Handler functions for the loading of data
    """
    
    @abstractmethod
    def load(self):
        pass

class LocalHandler(HandlerBase):
    """
    Class to handle the loading of local files
    """
    
    def __init__(self, config):
        self.config = config
        self.dwi = None
        self.bvec = None
        self.bval = None
        self.aff = []
    
    def _get_files(self, path, end_extention):
        
        out_data = []
        
        for file in os.listdir(path):
            if file.endswith(end_extention) and \
                (not "SBRef" in file and \
                 not "BIAS" in file):
                out_data.append(os.path.join(path, file))
        
        return out_data
    
    
    def _load_dwi(self, files):
        
        data = []
        aff = []
        
        for file in files:
            loaded = nib.load(file)
            data.append(loaded.get_data())
            
        aff = loaded.affine
        
        return (data, aff)
    
    
    def _load_bvec(self, files):
        
        data = []
        for file in files:
            data.append(np.loadtxt(file))
        
        return data
    
    
    def _load_bval(self, files):
        
        data = []
        for file in files:
            data.extend(np.loadtxt(file))
        
        return data
    
    
    def _get_data(self, path, end_extention):
        
        switch = {
            ".nii.gz": self._load_dwi,
            ".bvec": self._load_bvec,
            ".bval": self._load_bval
        }
        
        paths = self._get_files(path, end_extention)
        data = switch[end_extention](paths)
        
        return data
        
    
    def load(self):
        
        dwi_path = self.config['dwi_path']
        bvec_path = self.config['bvec_path']
        bval_path = self.config['bval_path']
        
        dwi, af = self._get_data(dwi_path, ".nii.gz")
        bvec = self._get_data(bvec_path, ".bvec")
        bval = self._get_data(bval_path, ".bval")
        
        out = [nib.Nifti1Image(np.concatenate(dwi, -1), af),
               gradient_table(bval, np.concatenate(bvec, -1))]
        
        return out


Handler = providers.FactoryAggregate(local=providers.Factory(LocalHandler))