import numpy as np
import matplotlib.pyplot as plt
import random
from pydantic import BaseModel
from typing import List

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

def runtest(shape = (100000,), locs = [3], fraction = 0.1, display = False, saveplot = False):
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


test_cases = []
test_fractions = [0, 0.001, 0.005, 0.01, 0.05]
test_locs = [[0], [1], [2], [3]]

for test_frac in test_fractions:
	for test_loc in test_locs:
		test_cases.append(SKTestCase(
			test_fraction = test_frac,
			test_locs = test_loc,
			thresh = 3
			)
		)

for case in test_cases:
	test_sk, test_sk_mean, test_sk_sigma = runtest(locs = case.test_locs, fraction = case.test_fraction, saveplot = True)
	if abs(test_sk - test_sk_mean) > case.thresh * test_sk_sigma:
		print(bcolors.FAIL)
	else:
		print(bcolors.OKGREEN)

	sk_distance = (test_sk - test_sk_mean) / test_sk_sigma

	print(f"Dist w/ {case.test_fraction} pollution at μ + xσ, x = {case.test_locs}")
	print(f"\tSK: {round(test_sk, 4)} = μ + {round(sk_distance, 4)}σ")
	print(bcolors.ENDC)
