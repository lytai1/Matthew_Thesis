#!/bin/bash
# Purpose: Read patient id and viscode from CSV File and run noddi analysis
# Author: Lok Yi Tai
# ------------------------------------------


export adni_dir="/home/ltai/mci_di/andi3_data/cn/ADNI"  
export data_dir="/home/ltai/mci_di/andi3_data/cn/" 
export mni_dir="/home/ltai/fsl/data/standard"

INPUT=/home/ltai/mci_di/andi3_data/cn/adni3_cn_list.csv
OLDIFS=$IFS
IFS=','
[ ! -f $INPUT ] && { echo "$INPUT file not found"; exit 99; }
while read s_id viscode
do
	echo "run noddi of"
	echo "s_id : $s_id"
	echo "viscode : $viscode"
	PATIENT_ID=$s_id VISCODE=$viscode; bash run_analysis.sh -t $adni_dir/$PATIENT_ID/$VISCODE/"${PATIENT_ID}_${VISCODE}"_T1.nii -d $adni_dir/$PATIENT_ID/$VISCODE/"${PATIENT_ID}_${VISCODE}".nii -r $mni_dir/avg152T1_brain.nii -p "${PATIENT_ID}"_$VISCODE

done < $INPUT
IFS=$OLDIFS
