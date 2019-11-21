from dmipy.signal_models import cylinder_models, gaussian_models
from dmipy.core.modeling_framework import *
from dmipy.distributions.distribute_models import SD1WatsonDistributed
import diffusion_imaging
import argparse
import logging
import numpy as np 
import dipy
import os

logger = logging.getLogger(__name__)

stick = cylinder_models.C1Stick()
ball = gaussian_models.G1Ball()
zeppelin = gaussian_models.G2Zeppelin()

watson_dispersed_bundle = SD1WatsonDistributed(models=[stick, zeppelin])
watson_dispersed_bundle.set_tortuous_parameter('G2Zeppelin_1_lambda_perp', 'C1Stick_1_lambda_par', 'partial_volume_0')
watson_dispersed_bundle.set_equal_parameter('G2Zeppelin_1_lambda_par', 'C1Stick_1_lambda_par')
watson_dispersed_bundle.set_fixed_parameter('G2Zeppelin_1_lambda_par', 1.7e-9)

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
	
        NODDI_mod = MultiCompartmentModel(models=[ball, watson_dispersed_bundle])
        NODDI_mod.set_fixed_parameter('G1Ball_1_lambda_iso', 3e-9)
	
        NODDI_fit_hcp = NODDI_mod.fit(
            scheme, data, mask=data[..., 0]>0)

        logger.info("Fitted models")
        return NODDI_fit_hcp

def visualize_result(model, image_name):

        sphere = dipy.data.get_sphere('symmetric724').subdivide()
        fods = model.fod(sphere.verticies, visual_odi_lower_bound=0.08)
	
        affine = np.eye(4)
        volume_res = fitted_parameters['SD1WatsonDistributed_1_SD1Watson_1_odi']
        volume_im = dipy.viz.actor.slicer(volume_res[:, 0, :, None],
                                          interpolation='nearest',
                                          affine=affine, opacity=0.7)

        ren = dipy.viz.window.Renderer()
        fod_spheres = dipy.viz.actor.odf_slicer(
                                     fods,
                                     sphere=sphere,
                                     scale=0.9,
                                     norm=False)
        fod_spheres.display_extent(0, fods.shape[0]-1, 0, fods.shape[1]-1,
                                   0, fods.shape[2]-1)
        fod_spheres.RotateX(90)
        fod_spheres.RotateZ(180)
        fod_spheres.RotateY(180)
        ren.add(fod_spheres)
        ren.add(volume_im)
        image_name = image_name + '.png'
        window.record(ren, size=[700, 700], outpath=image_name)
        logger.info(f"Rendered image and saved to {os.getcwd()}")

if __name__ == "__main__":

        parser = argparse.ArgumentParser(description="Process an mri to build a series of eigenvalues/vectors to detail water diffusion")
        parser.add_argument('--path', metavar='-p', type=str, help="The path to the location of the nii, bvec, and bval files to process")
        parser.add_argument('--name', metavar='-n', type=str, help="The name to save the image by")

        args = parser.parse_args()

        patients = load_files(args.path)
        model = fit_model(patients)
        visualize_result(model, args.name)

