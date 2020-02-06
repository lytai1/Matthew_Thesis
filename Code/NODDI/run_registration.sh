#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=20GB

while getopts p:r:o: option
do
case "${option}"
in 
p) DIR=${OPTARG};;
r) REF=${OPTARG};;
o) OUT_MAT_PATH=${OPTARG};;
esac
done

echo $DIR
echo $REF
echo $OUT_MAT_PATH
flirt -in $DIR -ref $REF -omat $OUT_MAT_PATH
