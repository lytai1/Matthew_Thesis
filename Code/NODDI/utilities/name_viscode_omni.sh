while getopts d: option
	do
	case "${option}" in
		d) ADNI_DIR=${OPTARG};;
		*) INVALID_ARGS=${OPTARG};;
	esac
done

for patient_no in ${ANDI_DIR}/*
do 
    echo ${ANDI_DIR}/$patient_no/*
done