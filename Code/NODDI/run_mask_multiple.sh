#!/bin/bash
# Purpose: apply multiple mask to multiple patients
# Author: Lok Yi Tai
# ------------------------------------------


ADNI_DIR="/home/ltai/mci_di/andi3_data/test/ADNI"
FSL_DIR="/home/ltai/fsl"
PATIENT_NO="003_S_6264"
VISCODE="bl"

INPUT=/home/ltai/mci_di/andi3_data/test/jhu_mask_list.csv
OLDIFS=$IFS
IFS=','

[ ! -f $INPUT ] && { echo "$INPUT file not found"; exit 99; }
while read m_id mask_name
do
	echo "run noddi of"
	echo "s_id : $s_id"
	echo "viscode : $viscode"
	bash run_mask.sh -d ${ADNI_DIR} -p ${PATIENT_NO} -v ${VISCODE} -m ${mask_name} -n ${m_id} -f ${FSL_DIR}

done < $INPUT
IFS=$OLDIFS