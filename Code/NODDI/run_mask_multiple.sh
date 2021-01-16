#!/bin/bash
# Purpose: apply multiple mask to multiple patients
# Author: Lok Yi Tai
# ------------------------------------------


ADNI_DIR="/home/ltai/mci_di/andi3_data/ad/ADNI"
FSL_DIR="/home/ltai/fsl"
INPUT_PATIENT_LIST="/home/ltai/mci_di/andi3_data/ad/adni3_ad_list.csv"
INPUT_JHU_LIST="/home/ltai/mci_di/andi3_data/jhu_mask_list.csv"

OLDIFS1=$IFS
IFS=','
[ ! -f $INPUT_PATIENT_LIST ] && { echo "$INPUT_PATIENT_LIST file not found"; exit 99; }
while read patient_no viscode
do
	OLDIFS2=$IFS
	IFS=','
	[ ! -f $INPUT_JHU_LIST ] && { echo "$INPUT_JHU_LIST file not found"; exit 99; }
	while read m_id mask_name
	do
		bash run_mask.sh -d ${ADNI_DIR} -p ${patient_no} -v ${viscode} -m ${mask_name} -n ${m_id} -f ${FSL_DIR}
	done < $INPUT_JHU_LIST
	IFS=$OLDIFS2

done < $INPUT_PATIENT_LIST
IFS=$OLDIFS1



