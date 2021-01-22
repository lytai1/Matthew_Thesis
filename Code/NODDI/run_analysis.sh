#!/bin/bash
<< 'DOCS'
options:
    -t The T1 file to run with
   -d The DTI file to run with
   -r The reference standard template to register against
   -p The patient number to use as the name

Sample run script:
bash run_analysis.sh -d /home/ltai/mci_di/andi3_data/test/ADNI -f /home/ltai/fsl -p 032_S_6602 -v bl
DOCS

while getopts t:d:r:p: option
   do
   case "${option}" in
		d) ADNI_DIR=${OPTARG};;
		f) FSL_DIR=${OPTARG};;
		p) PATIENT_NUM=${OPTARG};;
	    v) VISCODE=${OPTARG};;
		*) INVALID_ARGS=${OPTARG};;
   esac
done

if [[ ! -f "past_runs/" ]]; then
  mkdir -p "past_runs/"
fi
#while getopts t:d:r:p: option
#do
#case "${option}"
#in 
#t) T1_PATH=${OPTARG};;
#sac
#done


ORIGINAL_DIR=$PWD
T1_PATH=$ADNI_DIR/$PATIENT_NUM/$VISCODE/${PATIENT_NUM}_${VISCODE}_T1.nii
DTI_PATH=$ADNI_DIR/$PATIENT_NUM/$VISCODE/${PATIENT_NUM}_${VISCODE}.nii
REF_PATH=$FSL_DIR/data/standard/avg152T1_brain.nii


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
T1_MAT_PATH="${T1_DIR}/${PATIENT_NUM}_T1${MAT_FILE_EXT}"
T1_SEG_PATH="${T1_DIR}/${PATIENT_NUM}_T1${SEG_FILE_EXT}"

DTI_OR_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI${REORIENT_FILE_EXT}"
DTI_SEG_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI${SEG_FILE_EXT}"
DTI_REF_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI${REF_FILE_EXT}"
DTI_CORR_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI${CORRECTION_FILE_EXT}"
DTI_REG_PATH="${DTI_DIR}/${PATIENT_NUM}_DTI${REG_FILE_EXT}"

RESULTS_DIR="${DTI_DIR}/${PATIENT_NUM}"

WHITE_MATTER_SEG_PATH="${DTI_DIR}/${PATIENT_NUM}/WHITE_MATTER_SEGMENTATION" 
TRACTS_PATH="$(dirname $ADNI_DIR)/tracts"
LEFT_CINGULUM_HIPPO_PATH="${TRACTS_PATH}/left_cingulum_hippo.nii.gz"
LEFT_CORTICOSPINAL_PATH="${TRACTS_PATH}/left_corticospinal.nii.gz"

sbatch <<EOT
#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=20GB
#SBATCH --job-name=${PATIENT_NUM}_${VISCODE}
#SBATCH --output=past_runs/${PATIENT_NUM}_${VISCODE}-%j.out

set -e
## These two steps make certain that the patients data is in the correct orientation
## Just rotating the images (in (multiple) 90 degrees), make sure it is not flip
if [[ ! -f $DTI_OR_PATH ]]; then
  echo "Orienting DTI to standard space"
  fslreorient2std $DTI_PATH $DTI_OR_PATH
fi

if [[ ! -f $T1_OR_PATH ]]; then
  echo "Orienting T1 to standard space" 
  fslreorient2std $T1_PATH $T1_OR_PATH
fi

## This step runs the segmentation protocol
## extract the brain
echo "Running BET to remove extra material with options -R -B -F"
echo "-R being the option for robust (run multiple iterations)"
echo "-B being extract eyes"
echo "-F being run on all volumes (4D file)"
[[ ! -f $DTI_SEG_PATH ]] && bet $DTI_OR_PATH $DTI_SEG_PATH -R -B -F
[[ ! -f $T1_SEG_PATH ]] && bet $T1_OR_PATH $T1_SEG_PATH -R -B -F

## This step runs the movement correction on the patient data
## only in DTI because multiple "DTI" are taken with different gradient
## check for other movement correction method (eddy)
if [[ ! -f "${DTI_CORR_PATH}" ]]; then
  echo "Running Eddy correction to compensate for patient movement"
  eddy_correct $DTI_SEG_PATH $DTI_CORR_PATH trilinear
fi

echo $T1_SEG_PATH
echo "We're just before we call flirt"

## linear registration (rotate, translate, resizing, skew) (coregistration)
## first line saving transformation matrix 
## second line applying transformation to T1 images
## check line 112  "DTI_DIR" or "T1"?
if [[ ! -f "${T1_REG_PATH}" ]]; then
  echo "Running flirt on the T1 with a reference to the 2mm MNI reference"
  flirt -in $T1_SEG_PATH -ref $REF_PATH -omat "${T1_DIR}/${PATIENT_NUM}_T1.mat"
  flirt -in $T1_SEG_PATH -ref $REF_PATH -out $T1_REG_PATH -applyxfm -init "${DTI_DIR}/${PATIENT_NUM}_T1.mat" ## check this!!!
fi

## This is the step that registers the patients scans into a known template space for use in extracting specific regions later
if [[ ! -f "${DTI_REG_PATH}" ]]; then
  echo "Running flirt on the DTI with a reference to the 2mm MNI template."
  flirt -in $DTI_CORR_PATH -ref $REF_PATH -omat "${DTI_DIR}/${PATIENT_NUM}.mat"
  flirt -in $DTI_CORR_PATH -ref $REF_PATH -out $DTI_REG_PATH -applyxfm -init "${DTI_DIR}/${PATIENT_NUM}.mat"
fi

## generating binary mask of registered data
if [[ ! -f "${DTI_DIR}/${PATIENT_NUM}_mask${NII_FILE_EXT}" ]]; then
  echo "Generating binary mask from registered data"
  bet $DTI_REG_PATH "${DTI_DIR}/${PATIENT_NUM}_mask${NII_FILE_EXT}" -m -F
fi

## Segment the T1 brain into 3 categories for use in the resulting noddi image 
## might only save the white matter one
## white matter, grey matter and CSF
## partial voxel approximation
if [[ ! -f "${RESULTS_DIR}/WHITE_MATTER_SEGMENTATION/${PATIENT_NUM}_pve_2.nii.gz" ]]; then
  mkdir -p "${RESULTS_DIR}/WHITE_MATTER_SEGMENTATION"
  fast -n 3 -o "${RESULTS_DIR}/WHITE_MATTER_SEGMENTATION/${PATIENT_NUM}" ${T1_REG_PATH}
fi

echo "The resulting file can be found here: ${DTI_REG_PATH}"


echo "Preparing the directory for the patient run"
mkdir -p $RESULTS_DIR
cp $DTI_REG_PATH "${RESULTS_DIR}/${PATIENT_NUM}${NII_FILE_EXT}"
cp "${T1_DIR}/${PATIENT_NUM}.bval" "${RESULTS_DIR}/${PATIENT_NUM}.bval"
cp "${T1_DIR}/${PATIENT_NUM}.bvec" "${RESULTS_DIR}/${PATIENT_NUM}.bvec"
cp "${DTI_DIR}/${PATIENT_NUM}_mask${NII_FILE_EXT}" "${RESULTS_DIR}/mask${NII_FILE_EXT}"


echo "Running NODDI analysis"
python run_noddi.py --path $RESULTS_DIR --model 1 --label adni 

## Segment the white matter via the T1
## ignore everything that is not white matter
echo "Masking the odi values generated with the white matter segmentation from the patients T1"
fslmaths "${RESULTS_DIR}/odi.nii.gz" -mas "${WHITE_MATTER_SEG_PATH}/${PATIENT_NUM}_pve_2.nii.gz" "${RESULTS_DIR}/odi_segmented.nii.gz"

EOT
