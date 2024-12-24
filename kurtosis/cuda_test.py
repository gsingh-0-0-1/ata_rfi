import numpy as np
from sigpyproc.readers import FilReader
import os

from kurtosis_gpu import apply_kurtosis_to_block
from skutils import (
	guppi_to_fil
)


guppidir = '/mnt/primary/scratch/crush/LoA.C0736/GUPPI/'

chunksize = int(sys.argv[1])
nstds = int(sys.argv[2])


for fname in sorted(os.listdir(guppidir)):
	if 'guppi' in fname:
		guppi_fileptr = guppi.Guppi(os.path.join(guppidir, fname))

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

				# test GPU code
				data_gpu = np.copy(data)
				apply_kurtosis_to_block(data_gpu, n_stds = n_stds)

				# test CPU code
				masked, mask_frac = mask_chunk(data, MaskMethod.CHUNK_MEDIAN, n_stds = n_stds, chunksize = chunksize)

				failed_samples = np.sum(masked != data_gpu)

				if failed_samples > 0:
					raise Exception("Detected %d instances of unequal samples" % failed_samples)


			blocknum += 1