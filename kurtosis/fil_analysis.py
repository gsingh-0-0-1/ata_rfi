from sigpyproc.readers import FilReader
import matplotlib.pyplot as plt
import numpy as np
import os

#genfil = FilReader("datafiles/fout.fil")

fdir = "outfiles/"

fnames = [
	"raw_output.fil",
	#"proc_std_3_tint_16_chunk_256.fil",
	#"proc_std_3_tint_16_chunk_512.fil",
	#"proc_std_3_tint_16_chunk_1024.fil",
	#"proc_std_4_tint_16_chunk_256.fil",
	#"proc_std_4_tint_16_chunk_512.fil",
	#"proc_std_4_tint_16_chunk_1024.fil",
	"proc_std_5_tint_16_chunk_256.fil",
	"proc_std_5_tint_16_chunk_512.fil",
	"proc_std_5_tint_16_chunk_1024.fil",
]

ncols = len(fnames)

PULSE_START = 56
PULSE_END = 71

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
	signal = np.sum((profile - med)[PULSE_START:PULSE_END]) / np.sqrt(9)

	# remove the pulse from the profile
	offpulse = profile - med
	offpulse[PULSE_START:PULSE_END] = 0


	noise = np.sqrt(np.mean(offpulse ** 2))
	title = fname + ("\nSNR = %.5f" % (signal / noise,))
	plt.title(title)
	plt.plot(profile)

plt.show()
