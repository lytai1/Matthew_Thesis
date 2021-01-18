#!/bin/bash
# Purpose: remove masked odi files in ADNI directory
# Author: Lok Yi Tai
# ------------------------------------------

ADNI_DIR="/home/ltai/mci_di/andi3_data/ad/ADNI"
INPUT_PATIENT_LIST="/home/ltai/mci_di/andi3_data/ad/adni3_ad_list.csv"

ORIGINAL_DIR=$PWD

OLDIFS1=$IFS
IFS=','
[ ! -f $INPUT_PATIENT_LIST ] && { echo "$INPUT_PATIENT_LIST file not found"; exit 99; }
while read patient_no viscode
do
	PATIENT_DIR="${ADNI_DIR}/$patient_no/$viscode"
	RESULTS_DIR="${PATIENT_DIR}/${patient_no}_${viscode}"
	folder="${ADNI_DIR}/$patient_no/$viscode/${patient_no}_${viscode}"
	for f in $folder/${patient_no}_${viscode}_odi_*
	do
	  echo "$f"
	done
done < $INPUT_PATIENT_LIST