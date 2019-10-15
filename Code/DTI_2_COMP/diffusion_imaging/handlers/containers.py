from dmipy.core.acquisition_scheme import gtab_dipy2dmipy

class MRI:
    """
    Wrapper class for each MRI processed
    
    Args:
        image (Nifti1Image): The resulting loaded image in the Nifti1Image class loaded from the dwi and the affine values
        gradient_table (gradient_table): The gradient table found through the b-values and b-vectors from the given data
        year (str): The given year?
        orientation (str): Possible use 
    """
    def __init__(self, nifti_image, gradient_table):
        self.nifti_image = nifti_image
        self.data = self.nifti_image.get_data()
        self.gradient_table = gradient_table
        self.scheme = gtab_dipy2dmipy(self.gradient_table)
        self._result = None
        
    @property
    def result(self):
        return self._result
    
    @result.setter
    def result(self, res):
        self._result = res

class Patient:
    
    def __init__(self, patient_number, mri=None):
        self.patient_number = patient_number
        self.mri = mri
        
    def __str__(self):
        return f"Patient(parient_number = {self.patient_number})"
    