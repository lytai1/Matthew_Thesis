Requirement:
CentOs Linux 7.7.1908 (Core)
python 3.7.x
conda 4.6.8
pip

dmipy (python package)
https://github.com/AthenaEPI/dmipy.git

other python package:
numpy(1.17.3 <= for dmipy to work)
dipy
pathos
numba
pandas
matplotlib
fury
dill
dicom2nifti
dcm2niix (installed using conda)

git repos:
THESIS
https://github.com/plyte/THESIS.git
diffusion_imaging
https://github.com/plyte/diffusion_imaging.git

Installation instructions:
1) clone thesis, diffusion_imaging and dmipy repos
2) create conda environment (dmipy is the name of the environment used in this readme file)
conda create --name dmipy python==3.7
==> y to proceed
conda init
conda activate dmipy
3) install all python packages. Make sure the numpy installed is in version 1.17.3
pip install numpy==1.17.3 pandas matplotlib dipy pathos numba fury dill
4) install fsl
  a) download fslinstaller.py in https://fsl.fmrib.ox.ac.uk/fsldownloads_registration
  b) python fslinstaller.py (make sure it is in python 2.x environment. do conda deactivate to run in base environment)
  c) select the right directory for the fsl folder

5) install dmipy package
(need numpy==1.15.4 for windows to work)
cd dmipy
python setup.py install
6) install diffusion_imaging package
cd diffusion_imaging
python setup.py install
7) install dicom2nifti python package
pip install dicom2nifti
8) install dcm2niix
conda install -c conda-forge dcm2niix
(make sure it is in the "dmipy" conda environment)
** restart after fsl and dmipy package installation

Run analysis:
1) cd mci_di/THESIS/Code/NODDI
2) set environment variables
export adni_dir="/home/ltai/mci_di/data_test/ADNI"  
export data_dir="/home/ltai/mci_di/data_test" 
export mni_dir="/home/ltai/fsl/data/standard"

export adni_dir="/home/ltai/mci_di/data/ADNI"  
export data_dir="/home/ltai/mci_di/data" 
export mni_dir="/home/ltai/fsl/data/standard"
3) make sure it is running in dmipy environment
conda activate dmipy
4) run this line:
PATIENT_ID="002_S_1155" VISCODE="bl"; bash run_analysis.sh -t $adni_dir/$PATIENT_ID/$VISCODE/"${PATIENT_ID}_${VISCODE}"_T1.nii -d $adni_dir/$PATIENT_ID/$VISCODE/"${PATIENT_ID}_${VISCODE}".nii -r $mni_dir/avg152T1_brain.nii -p "${PATIENT_ID}"_$VISCODE 

PATIENT_ID="301_S_6326" VISCODE="bl"; bash run_analysis.sh -t $adni_dir/non_amnesic_mci/$PATIENT_ID/$VISCODE/"${PATIENT_ID}_${VISCODE}"_T1.nii -d $adni_dir/non_amnesic_mci/$PATIENT_ID/$VISCODE/"${PATIENT_ID}_${VISCODE}".nii -r $mni_dir/avg152T1_brain.nii -p "${PATIENT_ID}"_$VISCODE 
5) cat slurm-xxxxx.out 
// replace xxxxx with the number of the slurm file generated


ADNI database access:
1) go to http://adni.loni.usc.edu/
2) go to the "data & sample" tab, click "access data and samples"
3) click on login in the middle of the page
4) log in or create account using the box in the right upper corner (new accounts need to be approved by the ADNI manager. It usually takes 1-2 days for the new accout to be approved)
5) Click on the search tab, click "Advance Image Search(beta)"
6) We can search for images using the search page. In this project, the setting we used are as follow:
Phase: ADNI3
Research Group: MCI (for MCI patients) or CN (for control)
image: select both "DTI", "MRI" and "and"
7) hit "search" 
8) select the patients with "Accelerated Sgital MPRAGE" and "Axial DTI"
9) click one click download

Preprocessing:
1) make sure dicom2nifti and dcm2niix is installed in conda environment
pip install dicom2nifti
conda install -c conda-forge dcm2niix
2) cd /home/ltai/mci_di/THESIS/Code/NODDI/utilities
3) run the following command
python format_files.py --path /home/ltai/mci_di/data_test/ADNI/
4) new folders bl and m12 will be found in the directory instead of the orignial files

visualization:
1) find the pickel file that needed to be visualized
/home/ltai/mci_di/data/ADNI/non_amnesic_mci/301_S_6326/bl/301_S_6326_bl/301_S_6326
_bl.pkl

2) make sure all python packages are installed
dill
dipy
dmipy*
fury
scipy
psutil
* need to install through git repository
2) run the following command
python utilities/visualize_edited.py --path /home/ltai/mci_di/data/ADNI/non_amnesic_mci/301_S_6326/bl/301_S_6326_bl/301_S_6326_bl.pkl

