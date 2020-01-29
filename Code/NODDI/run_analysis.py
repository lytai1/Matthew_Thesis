from diffusion_imaging.handlers import make_handler
import subprocess
import nibabel as nib
import argparse

NUM_SLICES_PER_RUN = 20
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parallelization execution of seperate slices")
    parser.add_argument('--path', metavar='-p', type=str, help="The path of the location of the nii, bvec, and bval files to process")
    parser.add_argument('--name', metavar='-n', type=str, help="The name to save the image by")
    parser.add_argument('--model', metavar='-m', type=int, help="The number corresponding to this list of models: 1 -> NODDI, 2 -> BallStick")
    parser.add_argument('--label', metavar='-l', type=str, help="The label to use for the data provided. Options: hcp, adni, rosen")
    args = parser.parse_args()


    model_type = {
        1: "NODDI",
        2: "BallStick"
    }

    patient = make_handler(args.path, args.label).load()
    
    num_slices = patient.mri.data.shape[2]
    slice_list = [(x, x + 20) for x in range(0 , num_slices, NUM_SLICES_PER_RUN)]
    for s in slice_list:
        print(s)

