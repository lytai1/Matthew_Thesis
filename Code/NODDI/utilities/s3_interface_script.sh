#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=20GB
#SBATCH --job-name=upload-cn
#SBATCH --output=past_runs/slurm-%j.out

## to run script 
## sbatch s3_interface_script.sh

if [[ ! -f "past_runs/" ]]; then
  mkdir -p "past_runs/"
fi

python s3_interface.py -u -b adni3-omni -p /home/ltai/fci_dti/adni3_data/cn/ADNI_omni_prep -d cn/ADNI_omni_prep