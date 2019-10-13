class MRI:
    """
    Wrapper class for each MRI processed
    
    Args:
        image (Nifti1Image): The resulting loaded image in the Nifti1Image class loaded from the dwi and the affine values
        gradient_table (gradient_table): The gradient table found through the b-values and b-vectors from the given data
        year (str): The given year?
        orientation (str): Possible use 
    """
    def __init__(self, image, gradient_table, year=None, orientation=None):
        self.nifti1_image = image
        self.data = image.get_data()
        self.year = year
        self.gradient_table = gradient_table
        self.orientation = orientation
        self._result = None
        
    @property
    def result(self):
        return self._result
    
    @result.setter
    def result(self, res):
        self._result = res

class Patient:
    
    def __init__(self, patient_number, mri_list=None):
        self.patient_number = patient_number
        self.mri_list = mri_list
        
    def __str__(self):
        return f"Patient(parient_number = {self.patient_number})"
    