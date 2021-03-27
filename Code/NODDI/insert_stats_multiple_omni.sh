#!/bin/bash
# Purpose: insert statistics into a csv by running insert_stats_multiple.py
# Author: Lok Yi Tai
# ------------------------------------------
ADNI_DIR="/home/ltai/fci_dti/adni3_data/test/ADNI_omni"
INPUT_PATIENT_LIST="/home/ltai/fci_dti/adni3_data/test/adni3_test_list.csv"
INPUT_MASK_LIST="/home/ltai/fci_dti/adni3_data/test/mask_list.csv"

INFO_DIR="${ADNI_DIR}/INFO"
if [[ ! -f $INFO_DIR ]]; then 
	mkdir -p $INFO_DIR
fi

python insert_stats_multiple.py --adni $ADNI_DIR --patient $INPUT_PATIENT_LIST --mask ${INPUT_MASK_LIST} --save_to "${INFO_DIR}/ADNI_ODI_RESULTS.csv"