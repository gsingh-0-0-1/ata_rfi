import numpy as np
from sigpyproc.readers import FilReader
import os
import sys
from guppi import guppi

from kurtosis_gpu import apply_kurtosis_to_block
from skutils import (
	mask_chunk,
	MaskMethod
)


guppidir = '/mnt/primary/scratch/crush/LoA.C0736/GUPPI/'

chunksize = int(sys.argv[1])
n_stds = int(sys.argv[2])


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
				mask_gpu = apply_kurtosis_to_block(data_gpu, n_stds = n_stds)

				# test CPU code
				masked, mask = mask_chunk(data, 
						MaskMethod.CHUNK_MEDIAN, 
						n_stds = n_stds, 
						chunksize = chunksize,
						return_mask = True)

				failed_samples = np.sum(masked != data_gpu)

				if failed_samples > 0:
					print("FAILURE DETECTED")
					print("CPU arr shape: ", masked.shape)
					print("GPU arr shape: ", data_gpu.shape)
					print(np.where(masked != data_gpu))
					print()
					print("CPU:")
					print(masked[np.where(masked != data_gpu)])
					print()
					print("GPU:")
					print(data_gpu[np.where(masked != data_gpu)])
					print()
					raise Exception("Detected %d instances of unequal samples" % failed_samples)


			blocknum += 1
