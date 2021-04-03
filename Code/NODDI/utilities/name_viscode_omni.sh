while getopts d:l: option
	do
	case "${option}" in
		d) ADNI_DIR=${OPTARG};;
        l) PATIENT_LIST=${OPTARG};;
		*) INVALID_ARGS=${OPTARG};;
	esac
done
ORIGINAL_DIR=$PWD

cd ${ADNI_DIR}
for patient_no in */
do 
    cd $patient_no
    for viscode in *
    do
        # mv $viscode ${viscode#ses-}
        echo "${patient_no::-1}, ${viscode#ses-}"
    done
    cd ..
done > ${ADNI_DIR}/${PATIENT_LIST}

cd $ORIGINAL_DIR