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

NII_FILE_EXT=".nii.gz"
REORIENT_FILE_EXT="_or${NII_FILE_EXT}"
SEG_FILE_EXT="_brain${NII_FILE_EXT}"
REF_FILE_EXT="_refMNI152${NII_FILE_EXT}"
CORRECTION_FILE_EXT="_correction${NII_FILE_EXT}"
MAT_FILE_EXT="_refMNI152.mat"
REG_FILE_EXT="_reg${NII_FILE_EXT}"

T1_OR_PATH="${T1_DIR}/${PATIENT_NUM}_T1${REORIENT_FILE_EXT}"
T1_REF_PATH="${T1_DIR}/${PATIENT_NUM}_T1${REF_FILE_EXT}"
T1_REG_PATH="${T1_DIR}/${PATIENT_NUM}_T1${REG_FILE_EXT}"
T1_MAT_PATH="${T1_DIR}/${PATIENT_NUM}${MAT_FILE_EXT}"
T1_SEG_PATH="${T1_DIR}/${PATIENT_NUM}${SEG_FILE_EXT}"

DTI_OR_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI${REORIENT_FILE_EXT}"
DTI_SEG_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI${SEG_FILE_EXT}"
DTI_REF_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI${REF_FILE_EXT}"
DTI_CORR_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI${CORRECTION_FILE_EXT}"
DTI_REG_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI${REG_FILE_EXT}"

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

## This step makes certain that the patients data is in the correct orientation
echo "Orienting DTI to standard space"
[[ ! -f $DTI_OR_PATH ]] && fslreorient2std $DTI_PATH $DTI_OR_PATH
[[ ! -f $T1_OR_PATH ]] && fslreorient2std $T1_PATH $T1_OR_PATH

## This step runs the segmentation protocol
echo "Running BET to remove extra material with options -R -B -F"
echo "-R being the option for robust (run multiple iterations)"
echo "-B being extract eyes"
echo "-F being run on all volumes (4D file)"
[[ ! -f $DTI_SEG_PATH ]] && bet $DTI_OR_PATH $DTI_SEG_PATH -R -B -F
[[ ! -f $T1_SEG_PATH ]] && bet $T1_OR_PATH $T1_SEG_PATH -R -B -F

## Segment the T1 brain into 3 categories for use in the resulting noddi image
if [[ ! -f "${RESULTS_DIR}/WHITE_MATTER_SEGMENTATION/${PATIENT_NUM}_pve_2.nii.gz" ]]; then
  mkdir -p "${RESULTS_DIR}/WHITE_MATTER_SEGMENTATION"
  fast -n 3 -o "${RESULTS_DIR}/WHITE_MATTER_SEGMENTATION/${PATIENT_NUM}" ${T1_SEG_PATH}
fi

## This step runs the movement correction on the patient data
if [[ ! -f "${DTI_CORR_PATH}" ]]; then
  echo "Running Eddy correction to compensate for patient movement"
  eddy_correct $DTI_SEG_PATH $DTI_CORR_PATH trilinear
fi

#echo "Running flirt on the T1 with a reference to the 2mm MNI reference"
if [[ ! -f "${T1_REG_PATH}" ]]; then
  flirt -in $T1_OR_PATH -ref $REF_PATH -omat "${T1_DIR}/${PATIENT_NUM}_T1.mat"
  flirt -in $T1_OR_PATH -ref $REF_PATH -out $T1_REG_PATH -applyxfm -init "${DTI_DIR}/${PATIENT_NUM}_T1.mat"
fi

## This is the step that registers the patients scans into a known template space for use in extracting specific regions later
echo "Running flirt on the DTI with a reference to the 2mm MNI template."
if [[ ! -f "${DTI_REG_PATH}" ]]; then
  flirt -in $DTI_CORR_PATH -ref $REF_PATH -omat "${DTI_DIR}/${PATIENT_NUM}.mat"
  flirt -in $DTI_CORR_PATH -ref $REF_PATH -out $DTI_REG_PATH -applyxfm -init "${DTI_DIR}/${PATIENT_NUM}.mat"
fi

## generating binary mask of registered data
echo "Generating binary mask from registered data"
if [[ ! -f "${DTI_DIR}/${PATIENT_NUM}_brain${NII_FILE_EXT}" ]]; then
  bet $DTI_REG_PATH "${DTI_DIR}/${PATIENT_NUM}_brain${NII_FILE_EXT}" -m -F
fi

echo "The resulting file can be found here: ${DTI_REG_PATH}"

echo "Preparing the directory for the patient run"
mkdir -p $RESULTS_DIR
cp $DTI_REG_PATH "${RESULTS_DIR}/${PATIENT_NUM}${NII_FILE_EXT}"
cp "${T1_DIR}/${PATIENT_NUM}.bval" "${RESULTS_DIR}/${PATIENT_NUM}.bval"
cp "${T1_DIR}/${PATIENT_NUM}.bvec" "${RESULTS_DIR}/${PATIENT_NUM}.bvec"
cp "${DTI_DIR}/${PATIENT_NUM}_brain_mask${NII_FILE_EXT}" "${RESULTS_DIR}/mask${NII_FILE_EXT}"

echo "Running NODDI analysis"
python run_noddi.py --path $RESULTS_DIR --model 1 --label adni --retrain

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
