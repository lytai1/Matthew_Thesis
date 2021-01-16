import shutil
from pathlib import Path
import argparse
from datetime import datetime
import dicom2nifti
import os
import logging
import subprocess

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

#image descriptions from ADNI
LOOK_FOR_THESE_FILES = ["Axial_DTI", "Sagittal_3D_Accelerated_MPRAGE", "Accelerated_Sagittal_MPRAGE",
                        "Accelerated_Sag_IR-FSPRGR"]


class DCM2NIIConverter:

    def convert_directory(self, source_dir, output_dir, compression=True):
        if compression:
            subprocess.call(["dcm2niix", "-o", str(output_dir), str(source_dir)])
        else:
            subprocess.call(["dcm2niix", "-z", "n", "-o", str(output_dir), str(source_dir)])


class DICOM2NIFTIService:

    def __init__(self, source_dir, output_dir, converter):
        self.converter = converter
        self.source_dir = source_dir
        self.output_dir = output_dir

    def run(self):
        self.converter.convert_directory(self.source_dir, self.output_dir,
                                         compression=False)
        list_of_output_directory = os.listdir(self.output_dir)
        logger.info(list_of_output_directory)
        if any(".bval" in x for x in list_of_output_directory):
            return True
        return False


class DCM2NIIService:

    def __init__(self, converter):
        self.converter = converter

    def run(self, source_dir, output_dir):
        self.converter.convert_directory(source_dir, output_dir,
                                         compression=False)
        list_of_output_directory = os.listdir(output_dir)
        logger.info(list_of_output_directory)


class Formatter:

    def __init__(self, converter_service, path, viscodes, folders, patient_id, directory):
        self.converter_service = converter_service
        self.path = path
        self.viscodes = viscodes
        self.folders = folders
        self.patient_id = patient_id
        self.directory = directory

        self.full_path = os.path.join(self.path, self.directory)

    def rename_all(self, target_files, postfix):
        for viscode, date_folder_path in zip(self.viscodes, self.folders):

            output_dir = os.path.join(self.path, viscode)
            for file_in_viscode_dir in os.listdir(output_dir):
                viscode_file_full_path = os.path.join(output_dir, file_in_viscode_dir)

                if any(target_file_name in viscode_file_full_path for target_file_name in target_files):
                    self.rename(path_to_file=viscode_file_full_path,
                                patient_id=self.patient_id,
                                viscode=viscode, postfix=postfix)

    def rename(self, path_to_file, patient_id, viscode, postfix):

        named_to = return_rename_name(path_to_file, patient_id, viscode, postfix)
        logger.info("rename " + path_to_file + " to " + named_to)
        try:
            os.rename(path_to_file, named_to)
        except (FileNotFoundError, FileExistsError):
            os.remove(named_to)
            os.rename(path_to_file, named_to)

    def verify(self, required_file_extensions):

        verifications = []
        for viscode, date_folder_path in zip(self.viscodes, self.folders):

            output_dir = os.path.join(self.path, viscode)
            files_in_output_dir = os.listdir(output_dir)

            does_the_directory_contain_the_required_files = \
                any(
                    any(extension in file for extension in required_file_extensions)
                    for file in files_in_output_dir
                )
            logger.info(f"does the directory contain the required files? == {does_the_directory_contain_the_required_files}")
            verifications.append(does_the_directory_contain_the_required_files)

        if all(verifications):
            shutil.rmtree(self.full_path)
            return True
        else:
            return False

    def format(self):
        for viscode, date_folder_path in zip(self.viscodes, self.folders):

            output_dir = os.path.join(self.path, viscode)
            dcm_directory = get_directory_of_dcm_files(date_folder_path)

            self.converter_service.run(source_dir=dcm_directory, output_dir=output_dir)


class DTIFormatter(Formatter):
    #converter_service: DCM2NIIService
    #path: directory until patient number
    #viscodes: list of viscodes
    #folders: list of date folders in the directory
    #patient_id: patient id
    #directory: directory unit type of image (e.g. Axial_DTI)
    def __init__(self, converter_service, path, viscodes, folders, patient_id, directory):
        super(DTIFormatter, self).__init__(converter_service=converter_service, path=path, viscodes=viscodes,
                                           folders=folders, patient_id=patient_id, directory=directory)
        self.required_file_extensions = [".bval", ".bvec", ".nii"]
        self.target_files = ["Axial_DTI", "ADNI3"]

    def run(self):
        self.format()
        logger.info("rename all for DTI")
        self.rename_all(self.target_files, postfix="")
        if not self.verify(self.required_file_extensions):
            raise Exception("The verification failed")


class T1Formatter(Formatter):

    def __init__(self, converter_service, path, viscodes, folders, patient_id, directory):
        super(T1Formatter, self).__init__(converter_service=converter_service, path=path, viscodes=viscodes,
                                           folders=folders, patient_id=patient_id, directory=directory)
        self.required_file_extensions = ["_T1.nii"]
        self.target_files = ["Accelerated", "002a1001"]

    def run(self):
        self.format()
        self.rename_all(self.target_files, postfix="_T1")
        if not self.verify(self.required_file_extensions):
            raise Exception("The verification failed")


def get_directory_of_dcm_files(path):
    if path.endswith(".dcm"):
        p = Path(path)
        return p.parent
    else:
        for p in os.listdir(path):
            return get_directory_of_dcm_files(os.path.join(path, p))


def return_rename_name(path_to_file, patient_id, viscode, postfix=""):

    parent = str(Path(path_to_file).parent)
    basename = os.path.basename(path_to_file)
    _, extension = os.path.splitext(basename)

    named_to = os.path.join(parent, patient_id + "_" + viscode + postfix + extension)
    return named_to

#make new directories based on viscode
def make_directories(viscodes, directory):
    for viscode in viscodes:
        viscode_path = os.path.join(directory, viscode)
        if not os.path.exists(viscode_path):
            logger.info(f"Made directory: {viscode_path}")
            os.makedirs(os.path.join(directory, viscode))


#get all file names in the folder
def get_all_files_in_directory(abs_path):

    # get the visitation codes from the directory of dates
    folders = []
    for date_folder in os.listdir(abs_path):
        folders.append(os.path.join(abs_path, date_folder))

    return folders

#change date in folder name to viscode (e.g. bl, m12, m24, etc)
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

#build DTIFromatter for Axial DTI
#build T1Formatter for Accelerated_Sagittal_MPRAGE
#path: directory up to patient number
#directory: directory up to type of image (e.g. Axial_DTI)
#patient_id: patient id
#converter: DCM2NIIConverter
def build_formatter(path, directory, patient_id, converter):
    full_path = os.path.join(path, directory)
    viscodes = get_viscodes(full_path) #list of viscodes (e.g. bl, m12, etc)
    folders = get_all_files_in_directory(full_path) #list of date folders
    make_directories(viscodes, path)

    service = DCM2NIIService(converter)
    
    logger.info(full_path)
    logger.info(viscodes)
    logger.info(folders)
    logger.info(service)

    if all("Axial" in file for file in folders):
        return DTIFormatter(service, path, viscodes, folders, patient_id, directory)
    elif all("Sag" in file for file in folders):
        return T1Formatter(service, path, viscodes, folders, patient_id, directory)

def format_directory(path, patient_id):
    for directory in os.listdir(path):
        if directory in LOOK_FOR_THESE_FILES:
            formatter = build_formatter(path, directory, patient_id, converter=DCM2NIIConverter())
            #formatter.run()
"""
Description:
    Convert DCM files downloaded from ADNI database to NIfTI format.
    
    Directory will also converted to patient_number/viscode/NIfTI_files
    
    There are three NIfTI files, include '.bval', '.bvec', '.nii'
Help:

    --path The path to directory containing all of the patients
    
example command:

python format_files.py --path /home/ltai/mci_di/data_before_process/ADNI/

"""


if __name__ == "__main__":
    description = """Convert DCM files downloaded from ADNI database to NIfTI format. \n
    
                    Directory will also converted to patient_number/viscode/NIfTI_files \n
                    
                    There are three NIfTI files, include '.bval', '.bvec', '.nii'.\n
                    """
    help = """--path The path to directory containing all of the patients\n
    
            example command:\n

            python format_files.py --path /home/ltai/mci_di/data_before_process/ADNI/

            """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--path', metavar='-p', type=str, help=help)
    args = parser.parse_args()

    for patient_id in os.listdir(args.path):
        full_path = os.path.join(args.path, patient_id)
        format_directory(full_path, patient_id)
