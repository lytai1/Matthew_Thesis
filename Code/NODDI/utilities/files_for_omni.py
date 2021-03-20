import argparse
from pathlib import Path
from datetime import datetime
import os
import shutil
import logging


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

#image descriptions from ADNI
LOOK_FOR_THESE_FILES = ["Axial_DTI", "Sagittal_3D_Accelerated_MPRAGE", "Accelerated_Sagittal_MPRAGE",
                        "Accelerated_Sag_IR-FSPRGR"]

def get_viscodes(path):
    viscodes = ["bl", "m12", "m24", "m36", "m48", "m60", "m72"]
    files = os.listdir(path)

    dates = []
    for f in files:
        try:
            date_string = f.split('_')[0]
            date_object = datetime.strptime(date_string, '%Y-%m-%d').date()
            dates.append(date_object)
        except Exception as e:
            logger.error(e)
            logger.error(
                "The direct given must just include directories with names that resemble dates in this format: %Y-%m-%d"
                " (there can be anything after the _)")
            return
    pre_date = dates[0]
    v = [0]
    for date in dates[1:]:
        v.append(v[-1] + int(round((date - pre_date).days / 365)))
        pre_date = date

    return list(map(lambda x: viscodes[x], v))

def get_all_files_in_directory(abs_path):

    # get the visitation codes from the directory of dates
    folders = []
    for date_folder in os.listdir(abs_path):
        folders.append(os.path.join(abs_path, date_folder))

    return folders

def make_directories(viscodes, directory):
    for viscode in viscodes:
        viscode_path = os.path.join(directory, viscode)
        if not os.path.exists(viscode_path):
            # logger.info(f"Made directory: {viscode_path}")
            os.makedirs(os.path.join(directory, viscode))

def move_files(path, viscodes, folders, patient_id, directory, type_image):
    logger.info("move " + str(type_image))

    n = len(folders)
    for i in range(n):
        viscode_path = os.path.join(path, viscodes[i])
        type_path = os.path.join(viscode_path, type_image)
        if not os.path.exists(type_path):
            logger.info(f"Made directory: {type_path}")
            os.makedirs(type_path)
        logger.info(f"Copy files in: {folders[i]}")
        for root, dirs, files in os.walk(folders[i]):
            logger.info(root)
            logger.info(dirs)
            logger.info(files)
            # if os.path.isfile(files):
            #     shutil.copy(files, type_path)

def org_dir(path, directory, patient_id):
    full_path = os.path.join(path, directory)
    viscodes = get_viscodes(full_path) #list of viscodes (e.g. bl, m12, etc)
    folders = get_all_files_in_directory(full_path) #list of date folders
    make_directories(viscodes, path)

    # logger.info(full_path)
    # logger.info(viscodes)
    # logger.info(folders)

    if all("Axial" in file for file in folders):
        move_files(path, viscodes, folders, patient_id, directory, "DTI")
    elif all("Sag" in file for file in folders):
        move_files(path, viscodes, folders, patient_id, directory, "T1")

def format_directory(path, patient_id):
    for directory in os.listdir(path):
        if directory in LOOK_FOR_THESE_FILES:
            org_dir(path, directory, patient_id)


def main():
    description = """
                    convert directory to compatible one for easier processing.
                    organize files based on viscode
                    """
    help = """--path The path to directory containing all of the patients\n
    
            example command:\n

            python files_for_omni.py --path /home/ltai/mci_di/andi3_data/test/ADNI_omniprep

            """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--path', metavar='-p', type=str, help=help)
    args = parser.parse_args()

    for patient_id in os.listdir(args.path):
        full_path = os.path.join(args.path, patient_id)
        format_directory(full_path, patient_id)


main()