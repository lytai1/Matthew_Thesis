import diffusion_imaging
from diffusion_imaging.models import NODDIModel
from dipy.viz import window, actor
import argparse
import logging
import numpy as np 
import dipy
import os
import warnings
import dill
# from xvfbwrapper import Xvfb

# vdisplay = Xvfb()

warnings.filterwarnings("ignore")

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def load_files(path):

        config = {
                "patient_directory": path
        }
	
        logger.info("Loading patients")
        h = diffusion_imaging.handlers.DMIPYLocalHandler(config=config)
        patients = h.load()
        logger.info("Patients loaded")

        return patients

def fit_model(patients, model_type, middle_slice=False):

        switch = {
            "NODDI": NODDIModel()
        }

        patient = patients[0]
        scheme = patient.mri.scheme
        data = patient.mri.data
        label = patient.mri.label

        if middle_slice:
            if label == 'hcp':
                slice_index = data.shape[1] // 2
                data = data[:, slice_index : slice_index + 1]
            elif label == 'adni':
                slice_index = data.shape[1] // 2
                # adni data's shape is of the shape: (x, y, z, t)
                # this should return an array of shape: (x, y, z)
                data = data[:, :, slice_index : slice_index + 1, 0]
       
        picklefile_path = os.path.join(patient.directory,
                                       patient.patient_number + ".pkl") 
        if not os.path.exists(picklefile_path): 
            logger.info("Fitting model")  
            model = switch[model_type]	
            fitted_model = model.fit(
                scheme, data, mask=data[..., 0]>0)
            
            fitted_model_filepath = picklefile_path 
            with open(fitted_model_filepath, "wb") as f:
                dill.dump(fitted_model, f)
        else:
            logger.info("Loading model")
            print(picklefile_path)
            with open(picklefile_path, "rb") as f:
                fitted_model = dill.load(f)

        logger.info("Fitted model")
        return fitted_model 

def visualize_result(model, image_name):

        logger.info("Getting volume")
        affine = np.eye(4)
        affine[0,3] = -10
        affine[1,3] = -10

        ren = window.Renderer()
        peaks = model.peaks_cartesian()[:, :, :]
        
        volume = model.fitted_parameters['partial_volume_0']
        volume_im = actor.slicer(volume,
                                 interpolation='nearest',
                                 affine=affine, opacity=0.7)
        peaks_intensities = volume[:, :, :, None]
        
        peaks_fvtk = actor.peak_slicer(peaks, peaks_intensities,
                                       affine=affine, opacity=0.7)
        peaks_fvtk.RotateX(90)
        peaks_fvtk.RotateZ(180)
        peaks_fvtk.RotateY(180)
       
        logger.info("Rendering image") 
        image_name = image_name + '.png'
        window.add(ren, peaks_fvtk)
        window.add(ren, volume_im)
        
        # vdisplay.start()
        # try:
        window.record(scene=ren, size=[700, 700], out_path=image_name) 
        # finally:
        #    vdisplay.stop()

        #cwd = os.getcwd()
        #logger.info(f"Rendered image and saved to {cwd}")

if __name__ == "__main__":

        parser = argparse.ArgumentParser(description="Process an mri to build a series of eigenvalues/vectors to detail water diffusion")
        parser.add_argument('--path', metavar='-p', type=str, help="The path to the location of the nii, bvec, and bval files to process")
        parser.add_argument('--name', metavar='-n', type=str, help="The name to save the image by")

        args = parser.parse_args()

        patients = load_files(args.path)
        model = fit_model(patients, model_type="NODDI", middle_slice=True)
        # visualize_result(model, args.name)

