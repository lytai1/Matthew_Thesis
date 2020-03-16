

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

set -ex

NII_FILE_EXT=".nii.gz"
REORIENT_FILE_EXT="_or${NII_FILE_EXT}"
SEG_FILE_EXT="_brain${NII_FILE_EXT}"
REF_FILE_EXT="_refMNI152${NII_FILE_EXT}"
CORRECTION_FILE_EXT="_correction${NII_FILE_EXT}"
MAT_FILE_EXT="_refMNI152.mat"
REG_FILE_EXT="_reg${NII_FILE_EXT}"

T1_OR_PATH="${T1_DIR}/${PATIENT_NUM}_T1${REORIENT_FILE_EXT}"
T1_REF_PATH="${T1_DIR}/${PATIENT_NUM}_T1${REF_FILE_EXT}"
T1_MAT_PATH="${T1_DIR}/${PATIENT_NUM}${MAT_FILE_EXT}"
T1_SEG_PATH="${T1_DIR}/${PATIENT_NUM}${SEG_FILE_EXT}"

DTI_OR_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI${REORIENT_FILE_EXT}"
DTI_SEG_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI${SEG_FILE_EXT}"
DTI_REF_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI${REF_FILE_EXT}"
DTI_CORR_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI${CORRECTION_FILE_EXT}"
DTI_REG_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI${REG_FILE_EXT}"

RESULTS_DIR="${DTI_DIR}/${PATIENT_NUM}"

## This step makes certain that the patients data is in the correct orientation
echo "Orienting DTI to standard space"
fslreorient2std $DTI_PATH $DTI_OR_PATH
fslreorient2std $T1_PATH $T1_OR_PATH

## This step runs the segmentation protocol
echo "Running BET to remove extra material with options -R -B -F"
echo "-R being the option for robust (run multiple iterations)"
echo "-B being extract eyes"
echo "-F being run on all volumes (4D file)"
bet $DTI_OR_PATH $DTI_SEG_PATH -R -B -F
bet $T1_OR_PATH $T1_SEG_PATH -R -B -F

## Segment the T1 brain into 3 categories for use in the resulting noddi image
mkdir -p "${RESULTS_DIR}/WHITE_MATTER_SEGMENTATION"
fast -n 3 -o "${RESULTS_DIR}/WHITE_MATTER_SEGMENTATION/${PATIENT_NUM}" ${T1_SEG_PATH}

## This step runs the movement correction on the patient data
echo "Running Eddy correction to compensate for patient movement"
eddy_correct $DTI_SEG_PATH $DTI_CORR_PATH trilinear

#echo "Running flirt on the T1 with a reference to the 2mm MNI reference"
#flirt -in $T1_OR_PATH -ref $REF_PATH -out $T1_REF_PATH -omat $T1_MAT_PATH

## This is the step that registers the patients scans into a known template space for use in extracting specific regions later
echo "Running flirt on the DTI with a reference to the 2mm MNI template."
flirt -in $DTI_CORR_PATH -ref $REF_PATH -omat "${DTI_DIR}/${PATIENT_NUM}.mat"
flirt -in $DTI_CORR_PATH -ref $REF_PATH -out $DTI_REG_PATH -applyxfm -init "${DTI_DIR}/${PATIENT_NUM}.mat"

## generating binary mask of registered data
echo "Generating binary mask from registered data"
bet $DTI_REG_PATH "${DTI_DIR}/${PATIENT_NUM}_brain${NII_FILE_EXT}" -m -F

echo "The resulting file can be found here: ${DTI_REG_PATH}"

echo "Preparing the directory for the patient run"
mkdir -p $RESULTS_DIR
cp $DTI_REG_PATH "${RESULTS_DIR}/${PATIENT_NUM}${NII_FILE_EXT}"
cp "${T1_DIR}/${PATIENT_NUM}.bval" "${RESULTS_DIR}/${PATIENT_NUM}.bval"
cp "${T1_DIR}/${PATIENT_NUM}.bvec" "${RESULTS_DIR}/${PATIENT_NUM}.bvec"
cp "${DTI_DIR}/${PATIENT_NUM}_brain_mask${NII_FILE_EXT}" "${RESULTS_DIR}/mask${NII_FILE_EXT}"