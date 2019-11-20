from diffusion_imaging.handlers import DMIPYLocalHandler
from diffusion_imaging.models import FreeWaterTensorModel
from diffusion_imaging.preprocessing import PreprocessContainer
from dipy.reconst.shm import CsaOdfModel
from dipy.direction import peaks_from_model
from dipy.data import default_sphere
import dipy.reconst.dti as dti
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

dwi_file = os.path.join(os.path.expanduser("~"), ".cache", 
			"Python-Eggs", "dmipy-0.1.dev0-py3.7.egg-tmp", 
			"dmipy", "data", "hcp")

config = {
    'patient_directory': dwi_file
}

h = DMIPYLocalHandler(config=config)
patients = h.load()
masker = PreprocessContainer.mask()

for patient in patients:
    patient.mri.mask_data, patient.mri.mask = masker.process(patient.mri.data)
    
for patient in patients:
    fwdtimodel = FreeWaterTensorModel(patient.mri.gradient_table)
    fwdtifit = fwdtimodel.fit(patient.mri.data, patient.mri.mask)
    patient.mri.fitted_model = fwdtifit

dtimodel = dti.TensorModel(gtab)
dtifit = dtimodel.fit(data, mask=mask)


gtab = patients[0].mri.gradient_table
data = patients[0].mri.data
mask = patients[0].mri,mask
fwdtifit = patients[0].fitted_model

dti_FA = dtifit.fa
dti_MD = dtifit.md

FA = fwdtifit.FA
MD = fwdtifit.MD

axial_slice = 40

fig1, ax = plt.subplots(2, 4, figsize=(12, 6),
                        subplot_kw={'xticks': [], 'yticks': []})

fig1.subplots_adjust(hspace=0.3, wspace=0.05)
ax.flat[0].imshow(FA[:, :, axial_slice].T, origin='lower',
                  cmap='gray', vmin=0, vmax=1)
ax.flat[0].set_title('A) fwDTI FA')

ax.flat[1].imshow(dti_FA[:, :, axial_slice].T, origin='lower',
                  cmap='gray', vmin=0, vmax=1)
ax.flat[1].set_title('B) standard DTI FA')

FAdiff = abs(FA[:, :, axial_slice] - dti_FA[:, :, axial_slice])
ax.flat[2].imshow(FAdiff.T, cmap='gray', origin='lower', vmin=0, vmax=1)
ax.flat[2].set_title('C) FA difference')

ax.flat[3].axis('off')

ax.flat[4].imshow(MD[:, :, axial_slice].T, origin='lower',
                  cmap='gray', vmin=0, vmax=2.5e-3)
ax.flat[4].set_title('D) fwDTI MD')

ax.flat[5].imshow(dti_MD[:, :, axial_slice].T, origin='lower',
                  cmap='gray', vmin=0, vmax=2.5e-3)
ax.flat[5].set_title('E) standard DTI MD')


MDdiff = abs(MD[:, :, axial_slice] - dti_MD[:, :, axial_slice])
ax.flat[6].imshow(MDdiff.T, origin='lower', cmap='gray', vmin=0, vmax=2.5e-3)
ax.flat[6].set_title('F) MD difference')

F = fwdtifit.f.f

ax.flat[7].imshow(F[:, :, axial_slice].T, origin='lower',
                  cmap='gray', vmin=0, vmax=1)
ax.flat[7].set_title('G) free water volume')

plt.savefig('Free water DTI vs standard DTI.png')
