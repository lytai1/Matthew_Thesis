import diffusion_imaging
from run_noddi import load_files, fit_model, visualize_result
from dipy.viz import window, actor
import numpy as np
import dill
import sys

if __name__ == "__main__":
	path = "C:\\Users\\boywi\\OneDrive\\Documents\\SCHOOL\\SJSU\\thesis_data\\021_S_2077\\021_S_2077.pkl"

	with open(path, 'rb') as f:
		model = dill.load(f)

	from dipy.data import get_sphere
	sphere = get_sphere(name = 'symmetric724').subdivide()

	print(sys.getsizeof(model.fod(sphere.vertices, visual_odi_lower_bound=0.08)))