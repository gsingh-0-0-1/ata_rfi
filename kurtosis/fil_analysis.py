from sigpyproc.readers import FilReader
import matplotlib.pyplot as plt
import numpy as np
import os

#genfil = FilReader("datafiles/fout.fil")

fdir = "outfiles/"

fnames = [
	"raw_output.fil",
	"proc_std_3_tint_32_chunk_256.fil",
]

ncols = len(fnames)

for col, fname in enumerate(fnames):
	fil = FilReader(os.path.join(fdir, fname))
	folded = fil.fold(0.71452, 26.76410, nints = 1, nbins = 200, nbands = 400)
	fp = folded.get_freq_phase()

	plt.subplot(2, ncols, col + 1)
	plt.title(fname)
	im = plt.imshow(fp.data)
	plt.colorbar(im)

	plt.subplot(2, ncols, ncols + col + 1)
	plt.title(fname)
	plt.plot(folded.get_profile().data)

plt.show()
