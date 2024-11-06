from astropy.time import Time
from constants import *
from guppi import guppi
from sigpyproc.readers import FilReader

def init_filterbank(sample_fil_path, path_to_guppi, outfile_name, t_int = T_INT):
	# fil = FilReader("/mnt/primary/scratch/crush/guppi_60479_79539_018100_J0332+5434_0001/fout.fil")

	# Opens filterbank file for example header
	fil = FilReader(sample_fil_path)
	header = fil.header

	#dir = "./LoA.C0544/"
	# gfiles = os.listdir("/mnt/primary/scratch/crush/guppi_60479_79539_018100_J0332+5434_0001/LoA.C0544")

	# Opens guppi file to populate filterbank header
	gup_file = guppi.Guppi(path_to_guppi)
	hdr, block = gup_file.read_next_block()

	# Copy info from guppi header to filterbank header
	header.fch1 = float(hdr['OBSFREQ']) - hdr['OBSBW']/2.0
	header.foff = float(hdr['CHAN_BW'])
	header.nchans = hdr['NCHAN']
	header.source = hdr['SOURCE']
	header.nbits = 32
	# header.bandwidth = float(hdr['OBSBW'])
	tstart_unix = hdr['PKTSTART'] * float(hdr['TBIN']) + hdr['SYNCTIME']
	t = Time(tstart_unix, format='unix')
	header.tstart = t.mjd
	header.tsamp = hdr['TBIN'] * t_int

	# some weird sorcery, leave as is
	fout_name = outfile_name
	fio = header.prep_outfile(fout_name)
	fio.close()

	# Returns pointer to open filterbank file
	return open(fout_name, "ab")

