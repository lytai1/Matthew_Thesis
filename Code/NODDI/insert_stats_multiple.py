import argparse
import nibabel as nib
from dipy.segment.mask import bounding_box
from dipy.segment.mask import crop
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import fcntl


class InsertStats:
    """
        This InsertStats class is used to extract average odi value from .nii.gz files and insert them into a csv file

        Args:
            adni_path (str): The path to the ADNI folder.
            patient_file (file): The list of patients stored in a csv file
            mask_file (file): The list of masks used to extract odi value stored in a csv file
            result (file): The result stored in a csv file (can be empty)

        Functions:
            insert_odi_adni()
    """
    def __init__(self, adni_path, patient_file, mask_file, result_file):
        self.adni_path = adni_path
    
        self.patient_df = pd.read_csv(patient_file, header=None, names=["PTID","VISCODE"])
        self.mask_df = pd.read_csv(mask_file, header=None, names=["volume_no","name"])
        try:
            self.result_df = pd.read_csv(result_file, index_col=["PTID","VISCODE"])
        except pd.errors.EmptyDataError:
            my_index = pd.MultiIndex.from_tuples([], names=("PTID", "VISCODE"))
            self.result_df = pd.DataFrame(index=my_index)
    
    # Load Image functions
    def get_bounded_image(self, vol):
        min_indicies, max_indicies = bounding_box(vol)
        bounded_image = crop(vol, min_indicies, max_indicies)
        return bounded_image


    def load_image(self, path):
        image = nib.load(path)
        bounded_image = self.get_bounded_image(image.get_data())
        return bounded_image

    # Generate Statistics function
    def generate_statistics(self, image, label):
        masked = np.ma.array(image, mask=0)
        stats_dict = {
            f"{label}_ODI_avg": masked.mean()
        }
        return stats_dict


    def post_process_run(self, path, patient_id, viscode, label):
        """This function acts as the main function for the stat generation of individual odi files.

        Args:
            path (str): The path to the resulting tract. (odi file)
            patient_id (str): The patient number
            viscode (str): The patient viscode
            label (str): The name of the mask tract applied
        """
            
        odi_image = self.load_image(path)
        odi_stats = self.generate_statistics(odi_image, label)

        for key, value in odi_stats.items():
            self.result_df.loc[(patient_id, viscode), key] = value


    def insert_odi_adni(self):
        """
            The function acts as the main function for the stat generation of multiple patients. It extracts the path of ODI values and name of the mask tract applied.
            It calls post_process_run to extract odi value of individual mask of each patient.
        """
        for p_row in self.patient_df.itertuples():
            path = os.path.join(self.adni_path, p_row.PTID + "/" + p_row.VISCODE)
            path = os.path.join(path, p_row.PTID + "_" + p_row.VISCODE)
            
            for m_row in self.mask_df.itertuples():
                odi_path = os.path.join(path, p_row.PTID + "_" + p_row.VISCODE + "_odi_" + m_row.name + ".nii.gz")
                try: 
                    self.post_process_run(odi_path, p_row.PTID, p_row.VISCODE, m_row.name)
                except FileNotFoundError:
                    print(odi_path + " not found")
        self.result_df.to_csv(result_file)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Takes the resulting data generated from the segmented tract and "
                                                 "inserts it into a common csv file")
    parser.add_argument('--adni', metavar='-a', type=str, help="The ADNI path storing all patients data", required=True)
    parser.add_argument('--patient', metavar='-p', type=str, help="The list of patients stored in the ADNI directory", required=True)
    parser.add_argument('--mask', metavar='-m', type=str, help="The list of mask used to generate odi values in the ADNI directory", required=True)
    parser.add_argument('--save_to', metavar='-s', type=str, help="The path to the csv file to insert the information "
                                                                   "to. This is assumed to be a copy of the "
                                                                   "ADNI_ODI_RESULTS.csv file named ADNI_ODI_RESULTS.csv",
                        required=True)

    args = parser.parse_args()
    print("Start extracting ODI values and insert into csv file")

    with open(args.patient, "r") as patient_file, open(args.mask, "r") as mask_file, open(args.save_to, "w+") as result_file:
        i_s = InsertStats(args.adni, patient_file, mask_file, result_file)
        i_s.insert_odi_adni()
    print("Done")
