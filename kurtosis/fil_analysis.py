from sigpyproc.readers import FilReader
import matplotlib.pyplot as plt
import numpy as np
import os

from mpl_toolkits.axes_grid1 import make_axes_locatable

#genfil = FilReader("datafiles/fout.fil")

fdir = "outfiles_1139/"
hdir = "heimdall_1139"

fnames = [
	"raw_output.fil",
	"proc_std_3_tint_16_chunk_256.fil",
	"proc_std_3_tint_16_chunk_512.fil",
	"proc_std_3_tint_16_chunk_1024.fil",
	#"proc_std_4_tint_16_chunk_256.fil",
	#"proc_std_4_tint_16_chunk_512.fil",
	#"proc_std_4_tint_16_chunk_1024.fil",
	#"proc_std_5_tint_16_chunk_256.fil",
	#"proc_std_5_tint_16_chunk_512.fil",
	#"proc_std_5_tint_16_chunk_1024.fil",
]

masks = [
	"mask_raw.fil",
	"mask_std_3_tint_16_chunk_256.mask",
	"mask_std_3_tint_16_chunk_512.mask",
	"mask_std_3_tint_16_chunk_1024.mask",
	#"mask_std_4_tint_16_chunk_256.mask",
	#"mask_std_4_tint_16_chunk_512.mask",
	#"mask_std_4_tint_16_chunk_1024.mask",
	#"mask_std_5_tint_16_chunk_256.mask",
	#"mask_std_5_tint_16_chunk_512.mask",
	#"mask_std_5_tint_16_chunk_1024.mask",
]

ncols = len(fnames)

PULSE_START = 56
PULSE_END = 71

for col, (fname, maskfile) in enumerate(zip(fnames, masks)):
	maskarr = np.loadtxt(os.path.join(fdir, maskfile))

	zap_perc = round((1 - np.mean(maskarr)) * 100, 2)

	fil = FilReader(os.path.join(fdir, fname))
	folded = fil.fold(0.71452, 26.76410, nints = 1, nbins = 200, nbands = 400)
	fp = folded.get_freq_phase()

	plt.subplot(2, ncols, col + 1)
	plt.title(fname)
	im = plt.imshow(10 * np.log10(fp.data))
	plt.colorbar(im, shrink = 0.6)


	plt.subplot(2, ncols, ncols + col + 1)

	profile = 10 * np.log10(folded.get_profile().data / 192)
	med = np.median(profile)
	signal = np.sum((profile - med)[PULSE_START:PULSE_END]) / np.sqrt(9)

	# remove the pulse from the profile
	offpulse = profile - med
	offpulse[PULSE_START:PULSE_END] = 0

	cand_dir = os.path.join(hdir, fname.split(".")[0])
	ncands = int(os.popen("cat " + cand_dir + "/* | wc -l").read())


	noise = np.sqrt(np.mean(offpulse ** 2))
	title = fname + ("\n@ FCH1 {:.2f} MHz\nSNR = {:.5f}\nncands = {:d}\nZapped {:.2f}%".format(fil.header.fch1, signal / noise, ncands, zap_perc))
	plt.title(title)
	plt.plot(profile)

plt.subplots_adjust(left=0.1,
                    bottom=0.1, 
                    right=0.9, 
                    top=0.9, 
                    wspace=0.4, 
                    hspace=0.4)
plt.show()
