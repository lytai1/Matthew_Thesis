#!/bin/bash
# Purpose: insert statistics into a csv 
# Author: Lok Yi Tai
# ------------------------------------------
ADNI_DIR="/home/ltai/mci_di/andi3_data/ad/ADNI"
INPUT_PATIENT_LIST="/home/ltai/mci_di/andi3_data/ad/adni3_ad_list.csv"
INPUT_JHU_LIST="/home/ltai/mci_di/andi3_data/jhu_mask_list.csv"

ORIGINAL_DIR=$PWD
INFO_DIR="${ADNI_DIR}/INFO"
if [[ ! -f $INFO_DIR ]]; then 
	mkdir -p $INFO_DIR
fi

python insert_stats_multiple.py -a $ADNI_DIR -p $INPUT_PATIENT_LIST -m ${INPUT_JHU_LIST} -s "${ADNI_DIR}/INFO/ADNI_ODI_RESULTS.csv"