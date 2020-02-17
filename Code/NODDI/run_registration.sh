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

REORIENT_FILE_EXT="_or.nii.gz"
REF_FILE_EXT="_refMNI152.nii.gz"
MAT_FILE_EXT="_refMNI152.mat"

T1_OR_PATH="${T1_DIR}/${PATIENT_NUM}_T1${REORIENT_FILE_EXT}"
DTI_OR_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI${REORIENT_FILE_EXT}"

T1_REF_PATH="${T1_DIR}/${PATIENT_NUM}_T1${REF_FILE_EXT}"
DTI_REF_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI_${REF_FILE_EXT}"


T1_MAT_PATH="${T1_DIR}/${PATIENT_NUM}${MAT_FILE_EXT}"


echo "Orienting T1 to standard space"
fslreorient2std $T1_PATH $T1_OR_PATH

echo "Orienting DTI to standard space"
fslreorient2std $DTI_PATH $DTI_OR_PATH

echo "Running flirt on the T1 with a reference to the 2mm MNI reference"
flirt -in $T1_OR_PATH -ref $REF_PATH -out $T1_REF_PATH -omat $T1_MAT_PATH

echo "Running flirt on the DTI with a reference to the 2mm MNI reference using the Matrix generated from the previous step as an initialization"
flirt -in $DTI_OR_PATH -ref $REF_PATH -out $DTI_REF_PATH -applyxfm -init $T1_MAT_PATH -interp trilinear
