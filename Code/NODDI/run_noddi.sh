#!/bin/bash
#SBATCH --ncpus=50
#SBATCH --time=12:00:00

cd /home/mjones/matthew/THESIS/Code/NODDI
module purge
module load dmipy
python noddi_run.py --path /home/mjones/matthew/data --name adni_noddi

