#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=20GB

while getopts p: option
do
case "${option}"
in 
p) DIR=${OPTARG};;
esac
done 

cd /home/mjones/matthew/THESIS/Code/NODDI
python run_noddi.py --path $DIR --model 1 --label adni --retrain

