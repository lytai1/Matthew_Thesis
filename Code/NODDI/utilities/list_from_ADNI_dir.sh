#!/bin/bash
# Purpose: Generate a CSV file with patient id and viscode in ADNI dir
# Author: Lok Yi Tai
# usage:
#       bash list_from_ADNI_dir.sh -d "/home/ltai/fci_dti/adni3_data/ad/ADNI_omni_prep" -l "ad_patient_list.csv"
# ------------------------------------------


while getopts d:l: option
	do
	case "${option}" in
		d) ADNI_DIR=${OPTARG};;
        l) PATIENT_LIST=${OPTARG};;
		*) INVALID_ARGS=${OPTARG};;
	esac
done
ORIGINAL_DIR=$PWD

cd ${ADNI_DIR}
for patient_no in */
do 
    cd $patient_no
    # rm -R " "*/
    for viscode in *
    do
        # mv $viscode ${viscode#ses-}
        echo "${patient_no::-1},${viscode#ses-}"
    done
    cd ..
done > ${ADNI_DIR}/${PATIENT_LIST}

cd $ORIGINAL_DIR