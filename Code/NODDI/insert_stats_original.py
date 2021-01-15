import argparse
import nibabel as nib
from dipy.segment.mask import bounding_box
from dipy.segment.mask import crop
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os


# Load Image functions
def get_bounded_image(vol):
    min_indicies, max_indicies = bounding_box(vol)
    bounded_image = crop(vol, min_indicies, max_indicies)
    return bounded_image


def load_image(path):
    image = nib.load(path)
    bounded_image = get_bounded_image(image.get_data())
    return bounded_image


def pull_patient_meta_data(path):
    """The patient_id and the viscode is obtained through the use of the directory structure
    ../patient_id/viscode/file.file -> patient_id = patient_id and viscode = viscode
    """
    base_path, file_name = os.path.split(path)
    base_path, patient_id = os.path.split(base_path)
    base_path, viscode = os.path.split(base_path)

    if viscode in patient_id:
        patient_id = '_'.join(patient_id.split('_')[0:-1])
    return (patient_id, viscode)


# Generate Statistics function
def generate_statistics(image, label):
    masked = np.ma.array(image, mask=0)
    stats_dict = {
        f"{label}_ODI_avg": masked.mean()
    }
    return stats_dict


# Load source csv
def load_adni_merge(path):
    adni_merged = pd.read_csv(path)
    return adni_merged


# Insert stats function
def insert_stats(stats: dict, viscode: str, ptid: str, dataframe: pd.DataFrame) -> pd.DataFrame:
    """This function acts as a way to insert the statistics generated from the generate_statistics function.
    Args:
        stats (dict): The statistics dictionary returned from the generate_statistics function
        viscode (str): The visitation code for the patient
                       (i.e. bl = baseline (first visit) m12 = 12 month after baseline)
        ptid (str): The patients ID. Usuaully of the form ###_S_####
        dataframe (pd.DataFrame): The dataframe to insert the stats into

    Returns:
        pd.DataFrame: A dataframe that now contains those statistics
    """
    for key, value in stats.items():
        print(f"VISCODE == {viscode} and PTID == {ptid}")
        
        '''
        mask = (dataframe["VISCODE"] == viscode) & (dataframe["PTID"] == ptid)
        idx = dataframe.loc[mask].index.values[0]
        dataframe.at[idx, key] = value
        '''
        dataframe.loc[(ptid, viscode), key] = value
            
        print(dataframe.loc[(ptid, viscode), key])

    return dataframe


# Main function
def post_process_run(path, adni_merge_path=None, label=None):
    """This function acts as the main function for the stat generation part of this program.

    Args:
        path (str): The path to the resulting tract.
        adni_merge_path (str): The path to the ADNIMERGE_RESULTS.csv file

    Example:
          >>> post_process_run("path/to/tract.nii.gz", "path/to/ADNIMERGE_RESULTS.csv")
    """
    if adni_merge_path is None:
        adni_merge_path = os.path.join(os.environ['adni_dir'], "INFO", "ADNIMERGE_RESULTS.csv")

    adni_merge = load_adni_merge(adni_merge_path)
    odi_image = load_image(path)
    patient_id, viscode = pull_patient_meta_data(path)
    odi_stats = generate_statistics(odi_image, label)
    result = insert_stats(stats=odi_stats, viscode=viscode, ptid=patient_id, dataframe=adni_merge)

    return result


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Takes the resulting data generated from the segmented tract and "
                                                 "inserts it into a common csv file")
    parser.add_argument('--path', metavar='-p', type=str, help="The path to the location of the nii file generated from"
                                                               " the tract segmentation", 
                        required=True)
    parser.add_argument('--save_to', metavar='-st', type=str, help="The path to the csv file to insert the information "
                                                                   "to. This is assumed to be a copy of the "
                                                                   "ADNIMERGE.csv file named ADNIMERGE_RESULTS.csv",
                        required=True)
    parser.add_argument('--label', metavar='-l', type=str, help="The label for the specific mask insert. " 
                                                                "(i.e. left_corticospinal or left_cingulum_hippo). "
                                                                "This will dictate the prepended value in the csv file "
                                                                "generated",
                        required=True)
    args = parser.parse_args()
    print(args)
    print(args.label)
    print(type(args.label))

    results = post_process_run(args.path, args.save_to, args.label)
    results.to_csv(args.save_to, index=False)
