import os
import subprocess
import shlex
import argparse



if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="Contains all required arguments to run the pipeline")
	parser.add_argument('--patient_path', metavar='-p', type=str, help="The path to the location of the nii, bvec, and bval files to process")

	args = parser.parse_args()

	patient_directory = args.patient_path
	input_command = f"sbatch run_registration.sh -p {patient_directory} -r {os.environ['mni_template_file'] -o {os.path.join(patient_directory, 'affine')}"
	# run the registration for the patient

	input_command_args = shlex.split(input_command)
	return_code = subprocess.call(input_command_args)
	
	if return_code == 1:
		raise Exception

	# run the noddi calculation
	noddi_input_command = f"sbatch run_noddi.sh -p {patient_directory}"
	noddi_input_args = shlex.split(noddi_input_command)	
	return_code = subprocess.call(noddi_input_commands)
