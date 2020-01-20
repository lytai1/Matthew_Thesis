#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=3GB

cd /home/mjones/matthew/THESIS/Code/NODDI
python run_noddi.py --path /home/mjones/matthew/data --name adni_noddi
