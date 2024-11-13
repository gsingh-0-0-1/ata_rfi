from enum import Enum
from constants import *
import numpy as np

class MaskMethod(Enum):
	ZERO = 0
	CHUNK_MEDIAN = 1
	CHUNK_MEAN = 2

def mag2(data):
	return data.real * data.real + data.imag * data.imag

def sklim_bounds(std, nsamps):
	# rather than slowing ourselves down with a call
	# to os.system, we can just hardcode the values
	# that we'll need

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

	try:
		return sklim_vals[std][nsamps]
	else:
		raise Exception("no sklim values present for stddev %.2f and nsamps %d" % (stddev, nsamps))

def time_integrate(data, t_int = T_INT):
	pol_sum = mag2(data).sum(axis = -1)

	# integrate
	t = pol_sum.reshape(pol_sum.shape[0], -1, t_int).sum(axis = -1)

	return t.T

def sk_from_arr(data):
	"""
	data : np.ndarray-like
		data of shape (nants, nfreqs, nsamples, npols)
	"""

	data = data - np.mean(data)
	data = data / np.std(data)

	nants, nfreqs, nsamples, npols = data.shape
	m = nsamples

	d_dt = mag2(data)

	s1 = d_dt.sum(axis = 2, keepdims = True)
	s2 = (d_dt ** 2).sum(axis = 2, keepdims = True)
	sk_array = ((m + 1.) / (m - 1.)) * ((m * (s2 / (s1**2))) - 1)

	return sk_array

def mask_chunk(chunk, mask_method: MaskMethod = MaskMethod.CHUNK_MEDIAN, n_stds = 3, chunksize = SAMP_STEP):
	sk_arr = sk_from_arr(chunk)

	sk_mean = 1
	
	#sk_std = np.sqrt(4. / chunksize)
	sk_bounds = sklim_bounds(n_stds, chunksize)

	#mask = np.abs(sk_arr - sk_mean) < n_stds * sk_std
	mask = np.logical_and(sk_arr > sk_bounds[0], sk_arr < sk_bounds[1])
	maskedblock = chunk * mask

	if mask_method == MaskMethod.CHUNK_MEDIAN:
		maskedblock[np.where(maskedblock == 0)] = np.median(chunk)

	return maskedblock, mask

def write_chunk_to_fil(chunk, fileptr):
	# sum over antenna axis
	sum_ant = chunk.sum(axis = 0)

	towrite = time_integrate(sum_ant)
	towrite = towrite.astype(np.float32)

	towrite.tofile(fileptr)

def guppi_to_fil(guppi_fileptr, fil_fileptr, rfi_filter = True, n_stds = 3, chunksize = SAMP_STEP):
	blocknum = 0
	while True:
		print("Reading block %d of %s..." % (blocknum, guppi_fileptr.fname))
		hdr, block = guppi_fileptr.read_next_block()
		if not hdr:
			break

		print("\t(NANT, NCHAN, NSAMP, NPOL):\t", block.shape)

		for nstart in range(0, block.shape[2], chunksize):
			print("\t\tNSAMPS", nstart, "\t->\t", nstart + chunksize)
			data = block[:, :, nstart:nstart+chunksize, :]

			if rfi_filter:
				masked, mask = mask_chunk(data, MaskMethod.CHUNK_MEDIAN, n_stds = n_stds, chunksize = chunksize)
				write_chunk_to_fil(masked, fil_fileptr)
			else:
				write_chunk_to_fil(data, fil_fileptr)

		blocknum += 1

