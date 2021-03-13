#!/bin/bash
<< 'DOCS'
options:
	-d The ADNI directory
	-f The FSL directory
	-p The patient number "###_S_####"
	-v The patient viscode e.g. bl

Sample run script:
bash run_analysis_omni.sh -d /home/ltai/mci_di/andi3_data/test/ADNI_omni -p 032_S_6602 -v bl
DOCS

while getopts d:f:p:v: option
	do
	case "${option}" in
		d) ADNI_DIR=${OPTARG};;
		p) PATIENT_NUM=${OPTARG};;
		v) VISCODE=${OPTARG};;
		*) INVALID_ARGS=${OPTARG};;
	esac
done

if [[ ! -f "past_runs/" ]]; then
  mkdir -p "past_runs/"
fi

ORIGINAL_DIR=$PWD

NODDI_DIR="$ADNI_DIR/$PATIENT_NUM/$VISCODE/NODDI"
INPUT_DIR="$ADNI_DIR/$PATIENT_NUM/$VISCODE/Input"

if [[ ! -f "${NODDI_DIR}" ]]; then
  mkdir -p "${NODDI_DIR}"
fi

T1_PATH="$NODDI_DIR/${PATIENT_NUM}_${VISCODE}_T1.nii"
DTI_PATH="$NODDI_DIR/${PATIENT_NUM}_${VISCODE}.nii"

#copy input files to NODDI directory
cp "${INPUT_DIR}/input_bval.bval" "${NODDI_DIR}/${PATIENT_NUM}_${VISCODE}.bval"
cp "${INPUT_DIR}/input_bvec.bvec" "${NODDI_DIR}/${PATIENT_NUM}_${VISCODE}.bvec"
cp "${INPUT_DIR}/input_dwi.nii.gz" "$DTI_PATH"
cp "${INPUT_DIR}/input_t1.nii.gz" "$T1_PATH"


NII_FILE_EXT=".nii.gz"
REORIENT_FILE_EXT="_or${NII_FILE_EXT}"
SEG_FILE_EXT="_brain${NII_FILE_EXT}"
CORRECTION_FILE_EXT="_correction${NII_FILE_EXT}"
REG_FILE_EXT="_reg${NII_FILE_EXT}"

T1_OR_PATH="${NODDI_DIR}/${PATIENT_NUM}_${VISCODE}_T1${REORIENT_FILE_EXT}"
T1_REG_PATH="${NODDI_DIR}/${PATIENT_NUM}_${VISCODE}_T1${REG_FILE_EXT}"
T1_SEG_PATH="${NODDI_DIR}/${PATIENT_NUM}_${VISCODE}_T1${SEG_FILE_EXT}"

DTI_OR_PATH="${NODDI_DIR}/${PATIENT_NUM}_${VISCODE}_DTI${REORIENT_FILE_EXT}"
DTI_SEG_PATH="${NODDI_DIR}/${PATIENT_NUM}_${VISCODE}_DTI${SEG_FILE_EXT}"
DTI_CORR_PATH="${NODDI_DIR}/${PATIENT_NUM}_${VISCODE}_DTI${CORRECTION_FILE_EXT}"
DTI_REG_PATH="${NODDI_DIR}/${PATIENT_NUM}_${VISCODE}_DTI${REG_FILE_EXT}"

RESULTS_DIR="${NODDI_DIR}/${PATIENT_NUM}_${VISCODE}"
WHITE_MATTER_SEG_PATH="${NODDI_DIR}/${PATIENT_NUM}_${VISCODE}/WHITE_MATTER_SEGMENTATION" 

sbatch <<EOT
#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=20GB
#SBATCH --job-name=${PATIENT_NUM}_${VISCODE}
#SBATCH --output=past_runs/${PATIENT_NUM}_${VISCODE}-%j.out

set -e
## These two steps make certain that the patients data is in the correct orientation
## rotating the images (in (multiple) 90 degrees), make sure it is not flip
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

## generating binary mask of registered data
if [[ ! -f "${NODDI_DIR}/${PATIENT_NUM}_${VISCODE}_mask${NII_FILE_EXT}" ]]; then
  echo "Generating binary mask from registered data"
  bet $DTI_REG_PATH "${NODDI_DIR}/${PATIENT_NUM}_${VISCODE}_mask${NII_FILE_EXT}" -m -F
fi

## Segment the T1 brain into 3 categories for use in the resulting noddi image 
## might only save the white matter one
## white matter, grey matter and CSF
## partial voxel approximation
if [[ ! -f "${RESULTS_DIR}/WHITE_MATTER_SEGMENTATION/${PATIENT_NUM}_${VISCODE}_pve_2.nii.gz" ]]; then
  echo "Segment the T1 brain into 3 categories for use in the resulting noddi image"
  mkdir -p "${RESULTS_DIR}/WHITE_MATTER_SEGMENTATION"
  fast -n 3 -o "${RESULTS_DIR}/WHITE_MATTER_SEGMENTATION/${PATIENT_NUM}_${VISCODE}" ${T1_REG_PATH}
fi


echo "Preparing the directory for the patient run"
mkdir -p $RESULTS_DIR
cp $DTI_REG_PATH "${RESULTS_DIR}/${PATIENT_NUM}_${VISCODE}${NII_FILE_EXT}"
cp "${NODDI_DIR}/${PATIENT_NUM}_${VISCODE}.bval" "${RESULTS_DIR}/${PATIENT_NUM}_${VISCODE}.bval"
cp "${NODDI_DIR}/${PATIENT_NUM}_${VISCODE}.bvec" "${RESULTS_DIR}/${PATIENT_NUM}_${VISCODE}.bvec"
cp "${NODDI_DIR}/${PATIENT_NUM}_${VISCODE}_mask${NII_FILE_EXT}" "${RESULTS_DIR}/mask${NII_FILE_EXT}"

: <<'END'

echo "Running NODDI analysis"
python run_noddi.py --path $RESULTS_DIR --model 1 --label adni 

## Segment the white matter via the T1
## ignore everything that is not white matter
echo "Masking the odi values generated with the white matter segmentation from the patients T1"
fslmaths "${RESULTS_DIR}/odi.nii.gz" -mas "${WHITE_MATTER_SEG_PATH}/${PATIENT_NUM}_${VISCODE}_pve_2.nii.gz" "${RESULTS_DIR}/odi_segmented.nii.gz"

echo
echo "*******************************************************************************************************************"
echo "Preprocessing and NODDI analysis of ${PATIENT_NUM} ${VISCODE} is done"

END
EOT
