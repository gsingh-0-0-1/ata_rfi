import numpy as np
import cupy as cp

sklim_vals = {
	3 : {
		256 : [0.698159, 1.49597],
		512 : [0.775046, 1.32542],
		1024 : [0.834186, 1.21695]
	},
	4 : {
		256 : [0.613738, 1.784],
		512 : [0.711612, 1.48684],
		1024 : [0.786484, 1.31218],
	},
	5 : {
		256 : [0.526881, 2.18694],
		512 : [0.649093, 1.69044],
		1024 : [0.740405, 1.42332]
	}
}

def apply_kurtosis_to_block(block: np.array, n_stds = 3):
	# expecting something of the form (nants, nfreqs, nsamps, npols)

	# convert to cupy array
	block_cp = cp.array(block)

	# ################################
	# compute the sk_arr
	
	# assuming mean of 0 and std of 1
	# block = block - np.mean(block)
	# block = block / np.std(block)

	chunksize = block_cp.shape[2]
	nants, nfreqs, nsamples, npols = block_cp.shape
	m = nsamples

	d_dt = block_cp.real * block_cp.real + block_cp.imag * block_cp.imag

	s1 = d_dt.sum(axis = 2, keepdims = True)
	s2 = (d_dt ** 2).sum(axis = 2, keepdims = True)
	sk_arr = ((m + 1.) / (m - 1.)) * ((m * (s2 / (s1**2))) - 1)
	# done computing sk_arr
	# ################################


	sk_mean = 1
	sk_bounds = sklim_vals[n_stds][chunksize]


	mask = cp.logical_and(sk_arr > sk_bounds[0], sk_arr < sk_bounds[1])
	# mask = cp.logical_and(sk_arr > sk_bounds[0], sk_arr < sk_bounds[1])
	maskedblock = block_cp * mask

	maskedblock[cp.where(maskedblock == 0)] = cp.median(block_cp)

	block = cp.asnumpy(maskedblock)

