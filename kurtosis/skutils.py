from enum import Enum
from constants import *
import numpy as np

class MaskMethod(Enum):
	ZERO = 0
	CHUNK_MEDIAN = 1
	CHUNK_MEAN = 2

def mag2(data):
	return data.real * data.real + data.imag * data.imag

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

def mask_chunk(chunk, mask_method: MaskMethod = MaskMethod.CHUNK_MEDIAN, n_stds = 3):
	sk_arr = sk_from_arr(chunk)

	sk_mean = 1
	sk_std = np.sqrt(4. / SAMP_STEP)

	mask = np.abs(sk_arr - sk_mean) < n_stds * sk_std
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

def guppi_to_fil(guppi_fileptr, fil_fileptr, rfi_filter = True, n_stds = 3):
	blocknum = 0
	while True:
		print("Reading block %d of %s..." % (blocknum, guppi_fileptr.fname))
		hdr, block = guppi_fileptr.read_next_block()
		if not hdr:
			break

		print("\t(NANT, NCHAN, NSAMP, NPOL):\t", block.shape)

		for nstart in range(0, block.shape[2], SAMP_STEP):
			print("\t\tNSAMPS", nstart, "\t->\t", nstart + SAMP_STEP)
			data = block[:, :, nstart:nstart+SAMP_STEP, :]

			if rfi_filter:
				masked, mask = mask_chunk(data, MaskMethod.CHUNK_MEDIAN, n_stds = n_stds)
				write_chunk_to_fil(masked, fil_fileptr)
			else:
				write_chunk_to_fil(data, fil_fileptr)

		blocknum += 1

