import numpy as np
import matplotlib.pyplot as plt
import random
from pydantic import BaseModel
from typing import List
from matplotlib import colors

from kurtosis import (
	spectral_kurtosis,
)

from sampler import (
	random_normal_complex,
	rfi_polluted_normal_complex
)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def runtest(shape = (4096,), locs = [3], fraction = 0.1, display = False, saveplot = False):
	arr = rfi_polluted_normal_complex(shape = shape, locs = locs, fraction = fraction)
	sk = spectral_kurtosis(arr)
	M = shape[0]
	locstring = ", ".join([str(el) for el in locs])

	sk_mean = 1
	sk_sigma = np.sqrt(4. / M)

	if saveplot:
		plt.clf()
		plt.figure(figsize=(8, 8))
		plt.title(f"M = {M}, locs = {locstring}, frac = {fraction}\nSK: {sk}\n3σ: {sk_mean}±{3 * sk_sigma}")
		plt.hist(np.abs(arr), bins = 100)
		plt.savefig(f'kurtosis_test_{fraction}_{locs}.png')
	if display:
		plt.show()

	plt.close()
	return sk, sk_mean, sk_sigma

class SKTestCase(BaseModel):
	test_fraction: float
	test_locs: List
	thresh: float


SIGMA_MIN = 0
SIGMA_MAX = 6
FRAC_MIN = 0.1
FRAC_MAX = 0.8

SPACING = 30


test_cases = []
test_fractions = np.linspace(FRAC_MIN, FRAC_MAX, SPACING)
#test_locs = [[1], [2, 3.5]]
test_locs = [[el] for el in np.linspace(SIGMA_MIN, SIGMA_MAX, SPACING)]
thresh = 3

heatmap = np.empty(shape = (len(test_locs), len(test_fractions)))

for frac_idx, test_frac in enumerate(test_fractions):
	for loc_idx, test_loc in enumerate(test_locs):
		test_sk, test_sk_mean, test_sk_sigma = runtest(locs = test_loc, fraction = test_frac)
		
		if abs(test_sk - test_sk_mean) > thresh * test_sk_sigma:
			print(bcolors.FAIL)
		else:
			print(bcolors.OKGREEN)

		sk_distance = (test_sk - test_sk_mean) / test_sk_sigma

		print(f"Dist w/ {test_frac} pollution at μ + xσ, x = {test_loc}")
		print(f"\tSK: {round(test_sk, 4)} = μ + {round(sk_distance, 4)}σ")
		print(bcolors.ENDC)

		#heatmap[loc_idx][frac_idx] = test_sk
		heatmap[loc_idx][frac_idx] = abs(sk_distance)


fig, ax = plt.subplots()
ax.set_title("SK (σ's from μ of SK) vs. spike-σ and sample fraction")
ax.set_xlabel("Fraction of samples polluted")
ax.set_ylabel("σ from mean of spike")

#norm = colors.TwoSlopeNorm(vmin = np.amin(heatmap), vcenter=1, vmax=np.amax(heatmap))
#norm = colors.CenteredNorm(vcenter = 1)

im = ax.imshow(heatmap, 
	cmap = 'seismic', 
	extent = [FRAC_MIN, FRAC_MAX, SIGMA_MAX, SIGMA_MIN], 
	aspect = (FRAC_MAX - FRAC_MIN) / (SIGMA_MAX - SIGMA_MIN),
	#norm = norm,
	vmax = 4.
)
fig.colorbar(im, ax = ax)
plt.show()
