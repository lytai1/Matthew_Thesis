from pathlib import Path
import argparse
from datetime import datetime
import dicom2nifti
import os
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

LOOK_FOR_THESE_FILES = ["Axial_DTI", "Sagittal_3D_Accelerated_MPRAGE", "Accelerated_Sagittal_MPRAGE",
                        "Accelerated_Sag_IR-FSPRGR"]

class DICOM2NIFTIService:

    def __init__(self, source_dir, output_dir, converter):
        self.converter = converter
        self.source_dir = source_dir
        self.output_dir = output_dir

    def run(self):
        self.converter.convert_directory(self.source_dir, self.output_dir,
                                         compression=False)


class DTIFormatter:

    def __init__(self, converter_service):
        self.converter_service = converter_service

    def run(self):
        self.converter_service.run()


class T1Formatter:

    def __init__(self, converter_service):
        self.converter_service = converter_service

    def run(self):
        self.converter_service.run()


def build_formatter(path, source_dir, output_dir, converter):
    service = DICOM2NIFTIService(source_dir, output_dir, converter)
    if "Axial" in path:
        return DTIFormatter(service)
    elif "Sag" in path:
        return T1Formatter(service)


def make_directories(viscodes, directory):
    for viscode in viscodes:
        viscode_path = os.path.join(directory, viscode)
        if not os.path.exists(viscode_path):
            logger.info(f"Made directory: {viscode_path}")
            os.makedirs(os.path.join(directory, viscode))


def get_directory_of_dcm_files(path):
    if path.endswith(".dcm"):
        p = Path(path)
        return p.parent
    else:
        for p in os.listdir(path):
            return get_directory_of_dcm_files(os.path.join(path, p))


def rename_dti_file(path_to_file, patient_id, viscode):
    parent = str(Path(path_to_file).parent)
    basename = os.path.basename(path_to_file)
    _, extension = os.path.splitext(basename)

    named_to = os.path.join(parent, patient_id + "_" + viscode + extension)
    os.rename(path_to_file, named_to)


def rename_t1_file(path_to_file, patient_id, viscode):
    parent = str(Path(path_to_file).parent)
    basename = os.path.basename(path_to_file)
    _, extension = os.path.splitext(basename)

    named_to = os.path.join(parent, patient_id + "_" + viscode + "_T1" + extension)
    os.rename(path_to_file, named_to)


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

    out = []
    for date, viscode in zip(dates, viscodes):
        out.append(viscode)

    return out


def format_directory(path, patient_id):

    for directory in os.listdir(path):

        full_path = os.path.join(path, directory)
        viscodes = get_viscodes(full_path)

        if directory in LOOK_FOR_THESE_FILES:

            # get the visitation codes from the directory of dates
            folders = []
            for date_folder in os.listdir(full_path):
                folders.append(os.path.join(full_path, date_folder))

            # make viscode directory at the directory under the patient id
            make_directories(viscodes, path)

            # for each viscode generated from the list of date folders we format the files in
            # those folders and convert them from dicom to nifti format
            # then we change the names of those files to the convension set by the project
            for viscode, date_folder_path in zip(viscodes, folders):
                output_dir = os.path.join(path, viscode)
                dcm_directory = get_directory_of_dcm_files(date_folder_path)

                formatter = build_formatter(path=directory, source_dir=dcm_directory, output_dir=output_dir,
                                            converter=dicom2nifti)
                formatter.run()

                for file_in_viscode_dir in os.listdir(output_dir):
                    viscode_file_full_path = os.path.join(output_dir, file_in_viscode_dir)
                    logger.info(f"Renaming this file to project spec: {viscode_file_full_path}")
                    if "axial" in file_in_viscode_dir:
                        rename_dti_file(path_to_file=viscode_file_full_path, patient_id=patient_id,
                                        viscode=viscode)
                    elif "mprage" in file_in_viscode_dir:
                        rename_t1_file(path_to_file=viscode_file_full_path, patient_id=patient_id,
                                       viscode=viscode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Formatting ADNI files to the format of the project")
    parser.add_argument('--path', metavar='-p', type=str, help="The path to directory containing all of the patients")
    args = parser.parse_args()

    for patient in os.listdir(args.path):
        full_path = os.path.join(args.path, patient)

        format_directory(full_path, patient)
