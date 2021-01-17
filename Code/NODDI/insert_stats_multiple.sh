#!/bin/bash
# Purpose: insert statistics into a csv 
# Author: Lok Yi Tai
# ------------------------------------------
ADNI_DIR="/home/ltai/mci_di/andi3_data/mci/ADNI"
INPUT_PATIENT_LIST="/home/ltai/mci_di/andi3_data/mci/adni3_mci_list.csv"
INPUT_JHU_LIST="/home/ltai/mci_di/andi3_data/jhu_mask_list.csv"

ORIGINAL_DIR=$PWD
INFO_DIR="${ADNI_DIR}/INFO"
if [[ ! -f $INFO_DIR ]]; then 
	mkdir -p $INFO_DIR
fi

python insert_stats_multiple.py --adni $ADNI_DIR --patient $INPUT_PATIENT_LIST --mask ${INPUT_JHU_LIST} --save_to "${INFO_DIR}/ADNI_ODI_RESULTS.csv"