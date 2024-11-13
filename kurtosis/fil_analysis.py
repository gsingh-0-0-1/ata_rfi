from sigpyproc.readers import FilReader
import matplotlib.pyplot as plt
import numpy as np
import os

#genfil = FilReader("datafiles/fout.fil")

fdir = "outfiles/"

fnames = [
	"raw_output.fil",
	"proc_std_3_tint_32_chunk_256.fil",
	"proc_std_5_tint_32_chunk_256.fil",
]

ncols = len(fnames)

for col, fname in enumerate(fnames):
	fil = FilReader(os.path.join(fdir, fname))
	folded = fil.fold(0.71452, 26.76410, nints = 1, nbins = 200, nbands = 400)
	fp = folded.get_freq_phase()

	plt.subplot(2, ncols, col + 1)
	plt.title(fname)
	im = plt.imshow(10 * np.log10(fp.data))
	plt.colorbar(im)

	plt.subplot(2, ncols, ncols + col + 1)

	profile = 10 * np.log10(folded.get_profile().data / 192)
	med = np.median(profile)
	signal = np.sum((profile - med)[60:69]) / np.sqrt(9)
	noise = np.sqrt(np.mean((profile - med) ** 2))
	title = fname + ("\nSNR = %.5f" % (signal / noise,))
	plt.title(title)
	plt.plot(profile)

plt.show()
