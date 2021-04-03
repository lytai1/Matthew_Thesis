while getopts d: option
	do
	case "${option}" in
		d) ADNI_DIR=${OPTARG};;
		*) INVALID_ARGS=${OPTARG};;
	esac
done
ORIGINAL_DIR=$PWD
cd ${ADNI_DIR}

for patient_no in *
do 
    cd $patient_no
    for viscode in *
    do
       echo "${patient_no}, ${viscode}"
    done
    cd ..
done

cd $ORIGINAL_DIR