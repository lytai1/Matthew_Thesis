#!/bin/bash
# Purpose: Read patient id and viscode from CSV File and run noddi analysis
# Author: Lok Yi Tai
# ------------------------------------------

INPUT_PATIENT_LIST=/home/ltai/mci_di/andi3_data/test/adni3_test_list.csv
ADNI_DIR=/home/ltai/mci_di/andi3_data/test/ADNI
FSL_DIR=/home/ltai/fsl


OLDIFS=$IFS
IFS=','
[ ! -f $INPUT_PATIENT_LIST ] && { echo "$INPUT_PATIENT_LIST file not found"; exit 99; }
echo "start preprocessing and run NODDI of:"
while read s_id viscode
do
	echo "s_id : $s_id"
	echo "viscode : $viscode"
	bash run_analysis.sh -d $ADNI_DIR -f $FSL_DIR -p $s_id -v $viscode

done < $INPUT_PATIENT_LIST
IFS=$OLDIFS
echo "all runs can be found in /past_runs"