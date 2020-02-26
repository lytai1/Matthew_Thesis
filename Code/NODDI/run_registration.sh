#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=20GB

"""
Sample run script:
bash run_registration.sh -t some/t1/path.nii.gz -d some/dti/path.nii.gz -r some/ref/path.nii.gz -p 0##_S_####
"""
while getopts t:d:r:p: option
do
case "${option}"
in 
t) T1_PATH=${OPTARG};;
d) DTI_PATH=${OPTARG};;
r) REF_PATH=${OPTARG};;
p) PATIENT_NUM=${OPTARG};;
esac
done

T1_DIR=$(dirname "${T1_PATH}")
DTI_DIR=$(dirname "${DTI_PATH}")

NII_FILE_EXT=".nii.gz"
REORIENT_FILE_EXT="_or${NII_FILE_EXT}"
SEG_FILE_EXT="_brain${NII_FILE_EXT}"
REF_FILE_EXT="_refMNI152${NII_FILE_EXT}"
CORRECTION_FILE_EXT="_correction${NII_FILE_EXT}"
MAT_FILE_EXT="_refMNI152.mat"

T1_OR_PATH="${T1_DIR}/${PATIENT_NUM}_T1${REORIENT_FILE_EXT}"
T1_REF_PATH="${T1_DIR}/${PATIENT_NUM}_T1${REF_FILE_EXT}"
T1_MAT_PATH="${T1_DIR}/${PATIENT_NUM}${MAT_FILE_EXT}"

DTI_OR_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI${REORIENT_FILE_EXT}"
DTI_SEG_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI${SEG_FILE_EXT}"
DTI_REF_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI${REF_FILE_EXT}"
DTI_CORR_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI${CORRECTION_FILE_EXT}"

#echo "Orienting T1 to standard space"
#fslreorient2std $T1_PATH $T1_OR_PATH

## This step makes certain that the patients data is in the correct orientation
echo "Orienting DTI to standard space"
fslreorient2std $DTI_PATH $DTI_OR_PATH

## This step runs the segmentation protocol
echo "Running BET to remove extra material with options -R -B -F"
echo "-R being the option for robust (run multiple iterations)"
echo "-B being extract eyes"
echo "-F being run on all volumes (4D file)"
bet $DTI_OR_PATH $DTI_SEG_PATH -R -B -F

## This step runs the movement correction on the patient data
echo "Running Eddy correction to compensate for patient movement"
eddy_correct $DTI_SEG_PATH $DTI_CORR_PATH trilinear

#echo "Running flirt on the T1 with a reference to the 2mm MNI reference"
#flirt -in $T1_OR_PATH -ref $REF_PATH -out $T1_REF_PATH -omat $T1_MAT_PATH

## This is the step that registers the patients scans into a known template space for use in extracting specific regions later
echo "Running flirt on the DTI with a reference to the 2mm MNI template."
flirt -in $DTI_CORR_PATH -ref $REF_PATH -out $DTI_REF_PATH 

echo "The resulting file can be found here: ${DTI_REF_PATH}"
