from dipy.segment.mask import median_otsu
from abc import (
    ABC,
    abstractmethod
)
from dependency_injector import providers, containers
import numpy as np
from dipy.segment.mask import median_otsu

class Preprocess(ABC):
    """
    Base class for the preprocessing step
    """
    
    @abstractmethod
    def process(self, data):
        pass


class Mask(Preprocess):
    """
    Wrapper for the Mask process
    """
    
    def _mask(self, image):
        maskdata, mask = median_otsu(image, vol_idx=[0, 1], median_radius=4, numpass=2,
                                     autocrop=False, dilate=1)

        axial_slice = 40
        mask_roi = np.zeros(image.shape[:-1], dtype=bool)
        mask_roi[:, :, axial_slice] = mask[:, :, axial_slice]
        
        return mask_roi
    
    def process(self, mri_data):
        
        return self._mask(mri_data)
    
    
class PreprocessProvider(providers.Factory):
    
    provided_type = Preprocess
    
    
class PreprocessContainer(containers.DeclarativeContainer):
    
    mask = PreprocessProvider(Mask)
    