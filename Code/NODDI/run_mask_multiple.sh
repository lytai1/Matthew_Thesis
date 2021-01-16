#!/bin/bash
# Purpose: apply multiple mask to multiple patients
# Author: Lok Yi Tai
# ------------------------------------------


ADNI_DIR="/home/ltai/mci_di/andi3_data/ad/ADNI"
INPUT_PATIENT_LIST="/home/ltai/mci_di/andi3_data/ad/adni3_ad_list.csv"
INPUT_JHU_LIST="/home/ltai/mci_di/andi3_data/jhu_mask_list.csv"
FSL_DIR="/home/ltai/fsl"

ORIGINAL_DIR=$PWD
TRACTS_PATH="$(dirname "${ADNI_DIR}")/tracts"



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

## Rename all mask tracks
OLDIFS=$IFS
IFS=','
[ ! -f $INPUT_JHU_LIST ] && { echo "$INPUT_JHU_LIST file not found"; exit 99; }
while read m_id mask_name
do
	MASK_PATH="${TRACTS_PATH}/$mask_name.nii.gz"

	if [[ ! -f "${MASK_PATH}" ]]; then 
		echo "$mask_name not found. Rename the volume related to the mask track"
		cd $TRACTS_PATH
		# rename the volumes related to the mask tracts
		mv "${TRACTS_PATH}/vol$m_id.nii.gz" "${MASK_PATH}"
		cd $ORIGINAL_DIR
	fi
done < $INPUT_JHU_LIST
IFS=$OLDIFS



OLDIFS1=$IFS
IFS=','
[ ! -f $INPUT_PATIENT_LIST ] && { echo "$INPUT_PATIENT_LIST file not found"; exit 99; }
while read patient_no viscode
do
	echo "working on patient $patient_no $viscode"
	PATIENT_DIR="${ADNI_DIR}/$patient_no/$viscode"
	RESULTS_DIR="${PATIENT_DIR}/${patient_no}_${viscode}"

	OLDIFS2=$IFS
	IFS=','
	[ ! -f $INPUT_JHU_LIST ] && { echo "$INPUT_JHU_LIST file not found"; exit 99; }
	while read m_id mask_name
	do
		echo "Check if odi value of $mask_name exists."
		if [[ ! -f "${RESULTS_DIR}/${patient_no}_${viscode}_odi_${mask_name}.nii.gz" ]]; then 
			MASK_PATH="${TRACTS_PATH}/$mask_name.nii.gz"
			echo "odi of $mask_name for this patient does not exist"
			echo "Segmenting the ${mask_name} region using the white matter segmented odi values"
			fslmaths "${RESULTS_DIR}/odi_segmented.nii.gz" -mas "${MASK_PATH}" "${RESULTS_DIR}/${patient_no}_${viscode}_odi_${mask_name}.nii.gz"
		fi
	done < $INPUT_JHU_LIST
	IFS=$OLDIFS2

done < $INPUT_PATIENT_LIST
IFS=$OLDIFS1



