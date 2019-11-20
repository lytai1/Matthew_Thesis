from dmipy.signal_models import cylinder_models, gaussian_models
from dmipy.core.modeling_framework import *
import diffusion_imaging
import argparse
import logging
import numpy as np 
import dipy
import os

logger = logging.getLogger(__name__)

stick = cylinder_models.C1Stick()
ball = gaussian_models.G1Ball()

BAS = MultiCompartmentModel(models=[ball, stick])
BAS_SM = MultiCompartmentSphericalMeanModel(models=[ball, stick])
BAS_CSD = MultiCompartmentSphericalHarmonicsModel(models=[ball, stick])

def load_files(path):

	config = {
		"patient_directory": path
	}
	
	logger.info("Loading patients")
	h = diffusion_imaging.handlers.DMIPYLocalHandler(config=config)
	patients = h.load()
	logger.info("Patients loaded")

	return patients

def fit_model(patients):

	logger.info("Fitting models")
	patient = patients[0]
	scheme = patient.mri.scheme
	data = patient.mri.data
	
	BAS_fit = BAS.fit(scheme, data, solver='brute2fine')

	logger.info("Fitted models")
	return BAS_fit

def visualize_result(model, image_name):

	affine = np.eye(4)
	affine[0,3] = -10
	affine[1,3] = -10

	ren = dipy.viz.window.Renderer()
	peaks = model.peaks_cartesian()[70:90, :, 70:90]
	volume = model.fitted_parameters['partial_volume_0']
	volume_im = dipy.viz.actor.slicer(volume[70:90, 0, 70:90, None], interpolation='nearest', affine=affine, opacity=0.7)
	logger.info("Getting volume")

	peaks_intensities = volume[70:90, :, 70:90, None]
	logger.info("Getting peaks intensities")
	
	peaks_fvtk = dipy.viz.actor.peak_slicer(peaks, peaks_intensities, affine=affine, opacity=0.7)
	peaks_fvtk.RotateX(90)
	peaks_fvtk.RotateZ(180)
	peaks_fvtk.RotateY(180)
	logger.info("Built image")

	logger.info("Rendering image")
	image_name = image_name + '.png'
	dipy.viz.window.add(ren, peaks_fvtk)
	dipy.viz.window.add(ren, volume_im)
	dipy.viz.window.record(scene=ren, size=[700, 700], out_path=image_name)		
	logger.info(f"Rendered image and saved to {os.getcwd()}")

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description="Process an mri to build a series of eigenvalues/vectors to detail water diffusion")
	parser.add_argument('--path', metavar='-p', type=str, help="The path to the location of the nii, bvec, and bval files to process")
	parser.add_argument('--name', metavar='-n', type=str, help="The name to save the image by")

	args = parser.parse_args()

	patients = load_files(args.path)
	model = fit_model(patients)
	visualize_result(model, args.name)

