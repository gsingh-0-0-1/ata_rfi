import numpy as np

from sampler import (
	random_normal_complex,
	rfi_polluted_normal_complex
)

def spectral_kurtosis(data):
	M = data.shape[0]
	datanorm = data - np.mean(data)
	mag = ((datanorm.real) ** 2 + (datanorm.imag) ** 2) ** 0.5

	s1 = np.sum(mag ** 2)
	s2 = np.sum(mag ** 4)

	return ((M + 1.) / (M - 1)) * ((M * (s2 / s1**2)) - 1)