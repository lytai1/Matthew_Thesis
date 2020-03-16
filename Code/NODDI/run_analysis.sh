#!/bin/bash
<< 'DOCS'
options:
    -t The T1 file to run with
   -d The DTI file to run with
   -r The reference standard template to register against
   -p The patient number to use as the name

Sample run script:
sbatch run_analysis.sh -t some/path/to/patient#_T1.nii.gz -d some/path/to/patient#.nii.gz -r some/path/to/avg152.nii.gz -p ###_S_####
DOCS

while getopts t:d:r:p: option
do
case "${option}"
in 
t) T1_PATH=${OPTARG};;
d) DTI_PATH=${OPTARG};;
r) REF_PATH=${OPTARG};;
p) PATIENT_NUM=${OPTARG};;
*) INVALID_ARGS=${OPTARG};;
esac
done

ORIGINAL_DIR=$PWD
T1_DIR=$(dirname "${T1_PATH}")
DTI_DIR=$(dirname "${DTI_PATH}")
RESULTS_DIR="${DTI_DIR}/${PATIENT_NUM}"

WHITE_MATTER_SEG_PATH="${DTI_DIR}/WHITE_MATTER_SEGMENTATION" 
TRACTS_PATH="~/tracts"
LEFT_CINGULUM_HIPPO_PATH="${TRACTS_PATH}/left_cingulum_hippo.nii.gz"
RIGHT_CINGULUM_HIPPO_PATH="${TRACTS_PATH}/right_cingulum_hippo.nii.gz"

sbatch <<EOT
#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=20GB

set -ex
if [ ! -f "${RESULTS_DIR}/${PATIENT_NUM}.nii.gz" ]
then
  echo "Running preprocessing"
  bash run_analysis.sh -t "${T1_PATH}" -d "${DTI_PATH}" -r "${REF_PATH}"
fi

echo "Running NODDI analysis"
python run_noddi.py --path $RESULTS_DIR --model 1 --label adni 

## Segment the white matter via the T1
fslmaths "${RESULTS_DIR}/odi.nii.gz" -mas "${WHITE_MATTER_SEG_PATH}/${PATIENT_NUM}_pve_2.nii.gz" "${RESULTS_DIR}/odi_segmented.nii.gz"

## Check to see if the tract has been generated
if [ ! -f "${LEFT_CINGULUM_HIPPO_PATH} ]; then
	# split the JHU-ICBM-tracts file
	cd $TRACTS_PATH
	fslsplit /usr/local/fsl/data/atlases/JHU/JHU-ICBM-tracts-prob-2mm.nii.gz
	# rename the 6th volume to left_cingulum_hippo.nii.gz
	# rename the 7th volume to right_cingulum_hippo.nii.gz
	mv "${TRACTS_PATH}/vol0006.nii.gz" "${LEFT_CINGULUM_HIPPO_PATH}"
	mv "${TRACTS_PATH}/vol0007.nii.gz" "${RIGHT_CINGULUM_HIPPO_PATH}"
	cd $ORIGINAL_DIR	
fi
## Segment the left cingulum hippocampal region
fslmaths "${RESULTS_DIR}/odi_segmented.nii.gz" -mas "${LEFT_CINGULUM_HIPPO_PATH}" "${RESULTS_DIR}/odi_left_cingulum_hippo.nii.gz"

## Segment the right cingulum hiipocampal region
fslmaths "${RESULTS_DIR}/odi_segmented.nii.gz" -mas "${RIGHT_CINGULUM_HIPPO_PATH}" "${RESULTS_DIR}/odi_right_cingulum_hippo.nii.gz"
EOT
