import numpy as np
from sigpyproc.readers import FilReader
from guppi import guppi
from astropy.time import Time
import matplotlib
import matplotlib.pyplot as plt
from filutils import init_filterbank
import os
import sys

from constants import *
from skutils import (
	guppi_to_fil
)


WRITE_RAW = False
WRITE_PROC = False
thresholds = []

MAX_FILES = -1

# expects [PROC] [stdthresh] [chunksize] [maxfiles]
# expects [RAW] [maxfiles]

# TODO -- use argparse for this

if sys.argv[1] == "RAW":
	WRITE_RAW = True

if sys.argv[1] == "PROC":
	WRITE_PROC = True

if WRITE_PROC:
	thresholds.append(float(sys.argv[2]))

if WRITE_PROC:
	SAMP_STEP = int(sys.argv[3])

if WRITE_PROC:
	MAX_FILES = int(sys.argv[4])
if WRITE_RAW:
	MAX_FILES = int(sys.argv[2])



proc_filout_ptrs = []
mask_stat_paths = []

imdir = 'images/'
outdir = 'outfiles/'
#guppidir = 'datafiles/'
guppidir = '/mnt/primary/scratch/crush/guppi_60516_74066_177093_J0332+5434_0001/GUPPI'

#FIL_COPY = "datafiles/fout.fil"
FIL_COPY = "/mnt/primary/scratch/crush/guppi_60479_79539_018100_J0332+5434_0001/fout.fil"


fpath = os.path.join(guppidir, [el for el in os.listdir(guppidir) if 'guppi' in el][0])


if WRITE_PROC:
	for thresh in thresholds:
		filout = init_filterbank(FIL_COPY,
			fpath,
			outdir + 'proc_std_%d_tint_%d_chunk_%d.fil' % (thresh, T_INT, SAMP_STEP),
			T_INT
		)
		proc_filout_ptrs.append(filout)

		maskoutpath = outdir + 'mask_std_%d_tint_%d_chunk_%d.fil' % (thresh, T_INT, SAMP_STEP)
		try:
			os.remove(maskoutpath)
		except Exception:
			pass
		mask_stat_paths.append(maskoutpath)
if WRITE_RAW:
	rawfilout = init_filterbank(FIL_COPY, fpath, outdir + 'raw_output.fil', T_INT)

if not WRITE_RAW and not WRITE_PROC:
	raise Exception("No files to be written!")

nfiles = 0
for fname in sorted(os.listdir(guppidir)):
	if 'guppi' in fname:

		if nfiles > MAX_FILES and MAX_FILES != -1:
			break

		print("Starting to process", fname)

		if WRITE_RAW:
			guppi_fileptr = guppi.Guppi(os.path.join(guppidir, fname))
			guppi_to_fil(guppi_fileptr, rawfilout, None, False, chunksize = SAMP_STEP)
		if WRITE_PROC:
			for thresh, filout, mask_stat_path in zip(thresholds, proc_filout_ptrs, mask_stat_paths):
				guppi_fileptr = guppi.Guppi(os.path.join(guppidir, fname))
				guppi_to_fil(guppi_fileptr, filout, mask_stat_path, n_stds = thresh, chunksize = SAMP_STEP)

		nfiles += 1
