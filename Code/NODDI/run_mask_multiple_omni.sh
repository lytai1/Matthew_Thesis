#!/bin/bash
# Purpose: apply multiple mask to multiple patients optimized by omni directory
# Author: Lok Yi Tai
# ------------------------------------------


ADNI_DIR="/home/ltai/fci_dti/adni3_data/test/ADNI_omni"
INPUT_PATIENT_LIST="/home/ltai/fci_dti/adni3_data/test/adni3_test_list.csv"
INPUT_MASK_LIST="/home/ltai/fci_dti/adni3_data/test/mask_list.csv"

ORIGINAL_DIR=$PWD

## Resample all mask tracks
## also apply mask to odi_segmented

echo "running run_mask_multiple_omni.sh"

OLDIFS1=$IFS
IFS=','
[ ! -f $INPUT_PATIENT_LIST ] && { echo "$INPUT_PATIENT_LIST file not found"; exit 99; }
while read patient_no viscode
do
	echo "working on patient $patient_no $viscode"
	PATIENT_DIR="${ADNI_DIR}/$patient_no/$viscode/NODDI"
	RESULTS_DIR="${PATIENT_DIR}/${patient_no}_${viscode}"
	MASK_DIR="${ADNI_DIR}/$patient_no/$viscode/Atlas/outputs/atlas_reindex_matrix/conservative/"

	OLDIFS2=$IFS
	IFS=','
	[ ! -f $INPUT_JHU_LIST ] && { echo "$INPUT_JHU_LIST file not found"; exit 99; }
	while read mask_name
	do
		MASK_PATH="${MASK_DIR}/${mask_name}_resample.nii.gz"

		if [[ ! -f ${MASK_PATH} ]]; then 
			echo "resampling the ${mask_name} region"
			flirt -in "${MASK_DIR}/${mask_name}.nii.gz" -ref "${RESULTS_DIR}/odi.nii.gz" -applyxfm -usesqform -interp nearestneighbour -out "${MASK_PATH}"
		fi

		if [[ ! -f "${RESULTS_DIR}/${patient_no}_${viscode}_odi_${mask_name}.nii.gz" ]]; then 
			echo "Segmenting the ${mask_name} region using the white matter segmented odi values"
			fslmaths "${RESULTS_DIR}/odi_segmented.nii.gz" -mas "${MASK_PATH}" "${RESULTS_DIR}/${patient_no}_${viscode}_odi_${mask_name}.nii.gz"
		fi
	done < $INPUT_JHU_LIST
	IFS=$OLDIFS2

done < $INPUT_PATIENT_LIST
IFS=$OLDIFS1



