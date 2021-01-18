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
    def __init__(self, adni_path, patient_file, mask_file, result_file):
        self.adni_path = adni_path
    
        self.patient_df = pd.read_csv(patient_file, header=None, names=["PTID","VISCODE"])
        self.mask_df = pd.read_csv(mask_file, header=None, names=["volume_no","name"])
        try:
            self.result_df = pd.read_csv(result_file, index_col=["PTID","VISCODE"])
        except pd.errors.EmptyDataError:
            self.result_df = pd.DataFrame(index=["PTID","VISCODE"])
    
    # Load Image functions
    def get_bounded_image(self, vol):
        min_indicies, max_indicies = bounding_box(vol)
        bounded_image = crop(vol, min_indicies, max_indicies)
        return bounded_image


    def load_image(self, path):
        image = nib.load(path)
        bounded_image = get_bounded_image(image.get_data())
        return bounded_image


    def pull_patient_meta_data(self, path):
        """
        The patient_id and the viscode is obtained through the use of the directory structure
        ../patient_id/viscode/file.file -> patient_id = patient_id and viscode = viscode
        """
        base_path, file_name = os.path.split(path)
        base_path, patient_id = os.path.split(base_path)
        base_path, viscode = os.path.split(base_path)

        if viscode in patient_id:
            patient_id = '_'.join(patient_id.split('_')[0:-1])
        return (patient_id, viscode)


    # Generate Statistics function
    def generate_statistics(self, image, label):
        masked = np.ma.array(image, mask=0)
        stats_dict = {
            f"{label}_ODI_avg": masked.mean()
        }
        return stats_dict


    # Load source csv
    def load_adni_merge(self, path):
        try:
            adni_merged = pd.read_csv(path, index_col=["PTID", "VISCODE"])
        except pd.errors.EmptyDataError:
            my_index = pd.MultiIndex.from_tuples([], names=("PTID", "VISCODE"))
            adni_merged = pd.DataFrame(index=my_index)
        return adni_merged


    # Insert stats function
    def insert_stats(self, stats: dict, viscode: str, ptid: str, dataframe: pd.DataFrame)->pd.DataFrame:

        # This function acts as a way to insert the statistics generated from the generate_statistics function.
        # Args:
        #     stats (dict): The statistics dictionary returned from the generate_statistics function
        #     viscode (str): The visitation code for the patient
        #                 (i.e. bl = baseline (first visit) m12 = 12 month after baseline)
        #     ptid (str): The patients ID. Usuaully of the form ###_S_####
        #     dataframe (pd.DataFrame): The dataframe to insert the stats into

        # Returns:
        #     pd.DataFrame: A dataframe that now contains those statistics
        
        for key, value in stats.items():
            print(f"VISCODE == {viscode} and PTID == {ptid}")       
            dataframe.loc[(ptid, viscode), key] = value
            print(dataframe.loc[(ptid, viscode), key])

        return dataframe

    # Main function
    def post_process_run(self, path, adni_merge_path=None, label=None):
        """This function acts as the main function for the stat generation part of this program.

        Args:
            path (str): The path to the resulting tract.
            adni_merge_path (str): The path to the ADNIMERGE_RESULTS.csv file

        Example:
              >>> post_process_run("path/to/tract.nii.gz", "path/to/ADNIMERGE_RESULTS.csv")
        """
            
        adni_merge = load_adni_merge(adni_merge_path)
        odi_image = load_image(path)
        patient_id, viscode = pull_patient_meta_data(path)
        odi_stats = generate_statistics(odi_image, label)

        for key, value in stats.items():
            print(f"VISCODE == {viscode} and PTID == {ptid}")       
            print(value)
           
        #result = insert_stats(stats=odi_stats, viscode=viscode, ptid=patient_id, dataframe=adni_merge)
        #result.to_csv(adni_merge_path)

        #return result
        
    def insert_odi_adni(self):
        for p_row in self.patient_df.itertuples():
            path = os.path.join(self.adni_path, p_row.PTID + "/" + p_row.VISCODE)
            path = os.path.join(path, p_row.PTID + "_" + p_row.VISCODE)
            
            for m_row in self.mask_df.itertuples():
                adni_merge_path = os.path.join(path, p_row.PTID + "_" + p_row.VISCODE + "_odi_" + m_row.name + ".nii.gz")
                self.post_process_run(path, adni_merge_path, m_row.name)
            

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
    print(args)

    with open(args.patient, "r") as patient_file, open(args.mask, "r") as mask_file, open(args.save_to, "w+") as result_file:
        i_s = InsertStats(args.adni, patient_file, mask_file, result_file)
        i_s.insert_odi_adni()
        

    # results = post_process_run(args.path, args.save_to, args.label)
