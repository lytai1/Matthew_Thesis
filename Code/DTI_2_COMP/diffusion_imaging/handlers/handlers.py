from abc import ABC, abstractmethod
from dependency_injector import providers, containers
from dipy.core.gradients import gradient_table
import nibabel as nib
import os
import numpy as np
from itertools import groupby

from .containers import Patient, MRI


class HandlerBase(ABC):
    """
    Base class for the Handler functions for the loading of data
    """
    
    @abstractmethod
    def load(self):
        pass
    
class HCPLocalHandler(HandlerBase):
    """
    Class to hanlde the loading of the specific patient files from the Human Connectome Project
    """
    
    def __init__(self, config):
        self.config = config
        self.patient_directory = config['patient_directory']
        self.sub_directory = os.path.join("unprocessed", "3T", "Diffusion")
        
    def _get_files(self, path):
        
        grouped_file_paths = []
        base = os.path.join(self.patient_directory, path, self.sub_directory)
        files = os.listdir(base)
        
        filtered = []
        for file in files:
            if "DWI" in file and not "SBRef" in file:
                filtered.append(file)
        
        for key, group in groupby(filtered, lambda x: x.split('_')[2] + x.split('_')[3]):
            inner_group = []
            for file in group:
                inner_group.append(os.path.join(base, file))
            grouped_file_paths.append(list(inner_group))
        
        return grouped_file_paths
        
    def _load_dwi(self, file):
        image = nib.load(file)
        return image
    
    def _load_bvec(self, file):
        return np.loadtxt(file)
    
    def _load_bval(self, file):
        return np.loadtxt(file)
    
    def _make_mri(self, group):
        
        image = []
        bvecs = []
        bvals = []
        
        # The group is the group associated with the specific 'dir*'
        # this includes both LR and RL orientations
        for file in group:
            if file.endswith(".nii.gz"):
                dwi_data = self._load_dwi(file)
                image.append(dwi_data.get_data())
                aff = dwi_data.affine
            elif file.endswith(".bvec"):
                bvecs.append(self._load_bvec(file))
            elif file.endswith(".bval"):
                bvals.extend(self._load_bval(file))
        
        # Take the 
        gtab = gradient_table(bvals, np.concatenate(bvecs, -1))
        
        nifti_file = nib.Nifti1Image(np.concatenate(image, -1), aff)
        image = nifti_file.get_data()
        
        splitted = file.split("_")
        year = splitted[3][-2:]
        orientation = splitted[4]
        mri = MRI(nifti_file, gtab, year, orientation)
        
        return mri
        
    def load(self):
        
        patients = []
        for patient in os.listdir(self.patient_directory):
            p = Patient(patient_number=int(patient))
            
            grouped_files = self._get_files(os.path.join(self.patient_directory,
                                                         patient))
            mris = []
            for group in grouped_files:
                mris.append(self._make_mri(group))
            
            p.mri_list = mris
            patients.append(p)
            
        return patients
        

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