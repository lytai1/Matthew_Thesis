#!/bin/bash
# Purpose: apply JHU mask
# Author: Lok Yi Tai
# ------------------------------------------

<< 'DOCS'
options:
   -t The T1 file to run with
   -d The DTI file to run with
   -r The reference standard template to register against
   -p The patient number to use as the name

bash run_mask.sh -d /home/ltai/mci_di/andi3_data/test/ADNI -p 003_S_6264 -v bl -m anterior_thalamic_radiation_l -n 0000 -f /home/ltai/fsl
DOCS

while getopts d:p:v:m:n:f: option
   do
   case "${option}" in
      d) ADNI_DIR=${OPTARG};;
      p) PATIENT_NUM=${OPTARG};;
	  v) VISCODE=${OPTARG};;
      m) MASK=${OPTARG};;
	  n) MASK_NO=${OPTARG};; ## four digit
	  f) FSL_DIR=${OPTARG};;
      *) INVALID_ARGS=${OPTARG};;
   esac
done

ORIGINAL_DIR=$PWD

PATIENT_DIR="${ADNI_DIR}/${PATIENT_NUM}/${VISCODE}"
RESULTS_DIR="${PATIENT_DIR}/${PATIENT_NUM}_${VISCODE}"
WHITE_MATTER_SEG_PATH="${RESULTS_DIR}/WHITE_MATTER_SEGMENTATION" 

TRACTS_PATH="$(dirname "${ADNI_DIR}")/tracts"
MASK_PATH="${TRACTS_PATH}/${MASK}.nii.gz"


## Segment the white matter via the T1
## ignore everything that is not white matter
echo "Masking the odi values generated with the white matter segmentation from the patients T1"
fslmaths "${RESULTS_DIR}/odi.nii.gz" -mas "${WHITE_MATTER_SEG_PATH}/${PATIENT_NUM}_pve_2.nii.gz" "${RESULTS_DIR}/odi_segmented.nii.gz"


## Check to see if the tract has been generated
## split the tracts in one file to individual ones
if [[ ! -f "${TRACTS_PATH}" ]]; then 
	echo "No tract volumes were found. Preparing the JHU-ICBM tract segmentations"
	# split the JHU-ICBM-tracts file
        mkdir -p $TRACTS_PATH
	cd $TRACTS_PATH
	fslsplit "${FSL_DIR}/data/atlases/JHU/JHU-ICBM-tracts-prob-2mm.nii.gz"
	cd $ORIGINAL_DIR	
fi

if [[ ! -f "${MASK_PATH}" ]]; then 
	echo "MASK not found. Rename the volume related to the mask track"
	cd $TRACTS_PATH
	# rename the volumes related to the mask tracts
	mv "${TRACTS_PATH}/vol${MASK_NO}.nii.gz" "${MASK_PATH}"
	cd $ORIGINAL_DIR
fi

# Segment the mask region
echo "Segmenting the ${MASK} region using the white matter segmented odi values"
fslmaths "${RESULTS_DIR}/odi_segmented.nii.gz" -mas "${MASK_PATH}" "${RESULTS_DIR}/${PATIENT_NUM}_odi_${MASK}.nii.gz"

echo "Inserting the data in to the csv file found here: ${ADNI_DIR}/INFO/ADNI_ODI_RESULTS.csv"

if [[ ! -f "${ADNI_DIR}/INFO/" ]]; then
  mkdir -p "${ADNI_DIR}/INFO/"
fi

## Insert the generated statistics from the left corticospinal tract 
python insert_stats.py --path "${RESULTS_DIR}/${PATIENT_NUM}_odi_${MASK}.nii.gz" --save_to "${ADNI_DIR}/INFO/ADNI_ODI_RESULTS.csv" --label "${MASK}"
