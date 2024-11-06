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

# expects [mode -- RAW/PROC] [stdthresh, if proc]

if sys.argv[1] == "RAW":
	WRITE_RAW = True
if sys.argv[1] == "PROC":
	WRITE_PROC = True

if WRITE_PROC:
	thresholds.append(float(sys.argv[2]))

proc_filout_ptrs = []

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
if WRITE_RAW:
	rawfilout = init_filterbank(FIL_COPY, fpath, outdir + 'raw_output.fil', T_INT)

if not WRITE_RAW and not WRITE_PROC:
	raise Exception("No files to be written!")

nfiles = 0
for fname in sorted(os.listdir(guppidir)):
	if 'guppi' in fname:
		print("Starting to process", fname)

		if WRITE_RAW:
			guppi_fileptr = guppi.Guppi(os.path.join(guppidir, fname))
			guppi_to_fil(guppi_fileptr, rawfilout, False)
		if WRITE_PROC:
			for thresh, filout in zip(thresholds, proc_filout_ptrs):
				guppi_fileptr = guppi.Guppi(os.path.join(guppidir, fname))
				guppi_to_fil(guppi_fileptr, filout, n_stds = thresh)

		nfiles += 1

		if (nfiles + 1) % 5 == 0:
			cont = input("Processed %d files, press enter to continue: ")
