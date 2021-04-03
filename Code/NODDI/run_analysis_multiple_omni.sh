#!/bin/bash
# Purpose: Read patient id and viscode from CSV File and run noddi analysis
# Author: Lok Yi Tai
# ------------------------------------------

INPUT_PATIENT_LIST=/home/ltai/fci_dti/o8t_derivatives/ad/omni_ad_patient_list.csv
ADNI_DIR=/home/ltai/fci_dti/o8t_derivatives/ad


OLDIFS=$IFS
IFS=','
[ ! -f $INPUT_PATIENT_LIST ] && { echo "$INPUT_PATIENT_LIST file not found"; exit 99; }
echo "start preprocessing and run NODDI of:"
while read s_id viscode
do
	echo "s_id : $s_id"
	echo "viscode : $viscode"
	bash run_analysis_omni.sh -d $ADNI_DIR -p $s_id -v $viscode

done < $INPUT_PATIENT_LIST
IFS=$OLDIFS
echo "all runs can be found in /past_runs"