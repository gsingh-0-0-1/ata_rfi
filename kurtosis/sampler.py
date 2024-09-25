import numpy as np
import random

def random_normal_complex(shape = (100,), loc = 100, scale = 1):
	'''
	Generate complex normally distributed noise values

	:param shape: the shape / size of the noise array
	:param loc: mean of the intended distribution -- setting to 0 causes issues
		as we're working with complex values and an absolute magnitude with negative
		real components in the mix will be nasty
	:param scale: standard dev of the intended distribution
	'''
	return np.random.normal(size = list(shape) + [2],
		loc = loc,
		scale = scale
	).view(np.complex128).flatten()

def rfi_polluted_normal_complex(shape = (100,), locs = [3], fraction = 0.1):
	'''
	Generate complex normally distributed noise values which have
	off-nominal peaks

	:param shape: the shape / size of the noise array
	:param locs: a list of values of x such that an RFI "spike" is
		created with values µ + xσ, with μ and σ calculated from the
		base, non-polluted array
	'''

	assert len(shape) == 1

	basearr = random_normal_complex(shape)

	if len(locs) == 0:
		return basearr

	mu = np.mean(basearr)
	sigma = np.std(basearr)

	inds = random.sample(range(0, shape[0]), int(fraction * shape[0]))
	n_inds = len(inds)
	n_locs = len(locs)

	inds_per_spike = int(n_inds / n_locs)

	# we have allocated some indices to be "polluted"
	# we should select an even amount for each spike and then
	# pollute those
	for idx, loc in enumerate(locs):
		this_spike_start_ind = int(idx * n_inds / n_locs)
		these_inds = inds[this_spike_start_ind:this_spike_start_ind + inds_per_spike]

		basearr[these_inds] = mu + loc * sigma

	return basearr