"""This file contains the required logic to run the noddi anaylsis on a given patient

In order to run this file use the following commandline arguments
python run_noddi.py --

"""
import diffusion_imaging
from diffusion_imaging.models import NODDIModel, BallStickModel
from diffusion_imaging.handlers import make_handler
from dipy.segment.mask import median_otsu
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

def load_files(path, label):

        logger.info("Loading patient")
        h = make_handler(path, label)
        patient = h.load()
        logger.info("Patient loaded")

        return patient

def fit_model(patient, model_type, label, retrain, index_range=[], middle_slice=True):

        switch = {
            "NODDI": NODDIModel(),
            "BallStick": BallStickModel()
        }

        scheme = patient.mri.scheme
        data = patient.mri.data

        logger.info(f"Label is {label}")
        if not index_range is None and len(index_range) == 2:
            data = patient.mri.pull_axial_slices(index_range[0], index_range[1])
            picklefile_path = os.path.join(patient.directory, 
                                           patient.patient_number + f"_{index_range[0]}-{index_range[1]}.pkl") 
        elif middle_slice:
            data = patient.mri.pull_middle_slice()
            picklefile_path = os.path.join(patient.directory,
                                           patient.patient_number + ".pkl")
        else:
            picklefile_path = os.path.join(patient.directory,
                                           patient.patient_number + ".pkl")
        
        padding = 3 
        #data = data[52-padding:199+padding, 24-padding:222+padding, :, :] 
         
        b0_slice = data[:, :, :, 0]
        b0_mask, mask = median_otsu(b0_slice)
 
        logger.info(f"The shape of the data is {data.shape}")
        if not os.path.exists(picklefile_path) or retrain: 
             
            logger.info("Fitting model")  
            model = switch[model_type]	
            
            fitted_model = model.fit(
                scheme, data, mask=mask)
            
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

if __name__ == "__main__":

        parser = argparse.ArgumentParser(description="Process an mri to build a series of eigenvalues/vectors to detail water diffusion")
        parser.add_argument('--path', metavar='-p', type=str, help="The path to the location of the nii, bvec, and bval files to process")
        parser.add_argument('--name', metavar='-n', type=str, help="The name to save the image by")
        parser.add_argument('--model', metavar='-m', type=int, help="The number corresponding to this list of models: 1 -> NODDI, 2 -> BallStick")
        parser.add_argument('--label', metavar='-l', type=str, help="The label to use for the data provided. Options: hcp, adni, rosen")
        parser.add_argument('--retrain', action="store_true", help="Whether or not to retain the model")
        parser.add_argument('--index_range', metavar='-ir', type=int, nargs='+', help="Specify the index range for the image to be generated, input is two integers i.e. 1 5 indicating the range from 1 to before 5")
        parser.add_argument('--middle_slice', action="store_true", help="Whether or not to use the middle slice of the image")
        args = parser.parse_args()

        print(args)
        #if len(args.index_range) != 2:
        #    raise Exception

        if args.middle_slice is True and not args.index_range is None:
            raise Exception("Please specify either the middle_slice or the index_range. These two options conflict")

        model_type = {
            1: "NODDI",
            2: "BallStick"
        }
 
        patients = load_files(args.path, args.label)
        try:
            model = fit_model(patients, label=args.label, model_type=model_type[args.model], index_range=args.index_range, middle_slice=args.middle_slice, retrain=args.retrain)
        except KeyError:
            logger.info("The model selected is not one of the few presented, please add --help to your next run of this program to see the list of models allowed")

        # visualize_result(model, args.name)

