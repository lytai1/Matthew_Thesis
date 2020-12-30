#!/bin/bash
# Purpose: Read patient id and viscode from CSV File and run noddi analysis
# Author: Lok Yi Tai
# ------------------------------------------


export adni_dir="/home/ltai/mci_di/andi3_data/ad/ADNI"  
export data_dir="/home/ltai/mci_di/andi3_data/ad/" 
export mni_dir="/home/ltai/fsl/data/standard"

INPUT=/home/ltai/mci_di/andi3_data/ad/adni3_ad_list.csv
OLDIFS=$IFS
IFS=','
[ ! -f $INPUT ] && { echo "$INPUT file not found"; exit 99; }
while read s_id viscode
do
	echo "s_id : $flname"
	echo "viscode : $viscode"

done < $INPUT
IFS=$OLDIFS
