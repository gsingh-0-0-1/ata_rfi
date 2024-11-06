import numpy as np

from sampler import (
	random_normal_complex,
	rfi_polluted_normal_complex
)

def spectral_kurtosis(data):
	M = data.shape[0]
	datanorm = data - np.mean(data)

	mag = ((datanorm.real) ** 2 + (datanorm.imag) ** 2) ** (1 / 2)

	s1 = np.sum(mag ** 2)
	s2 = np.sum(mag ** 4)

	return ((M + 1.) / (M - 1)) * ((M * (s2 / s1**2)) - 1)


def sk_from_arr(data):
	"""
	data : np.ndarray-like
		data of shape (nants, nfreqs, nsamples, npols)
	"""

	data = data - np.mean(data)
	data = data / np.std(data)

	nants, nfreqs, nsamples, npols = data.shape
	m = nsamples
	#print(data)
	d_dt = data.real * data.real + data.imag * data.imag
	#print(d_dt)
	s1 = d_dt.sum(axis = 2, keepdims = True)
	s2 = (d_dt**2).sum(axis = 2, keepdims = True)
	sk_array = ((m + 1.) / (m - 1.)) * ((m * (s2 / (s1**2))) - 1)
	#print(np.mean(sk_array))

	return sk_array
