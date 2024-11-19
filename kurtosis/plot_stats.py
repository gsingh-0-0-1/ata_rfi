import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

SNR_RAW = 14.53

# std
Y = np.array([3, 4, 5])

# chunksize
X = np.array([256, 512, 1024])

SNRS = np.array([
	[21.46, 15.46, 11.20],
	[21.96, 16.31, 11.51],
	[22.80, 17.07, 13.26]
])

extent = [X[0], X[-1], Y[-1], Y[0]]

aspect = (X[-1] - X[0]) / (Y[-1] - Y[0])

plt.subplot(121)
plt.title("SNR vs. stddev and chunksize (RAW %.2f)" % SNR_RAW)
im = plt.imshow(SNRS, extent = extent, aspect = aspect)
plt.colorbar(im)

plt.subplot(122)
plt.title("% Change in SNR vs stddev and chunksize")
im = plt.imshow(100 * (SNRS - SNR_RAW) / SNR_RAW,
	extent = extent,
	aspect = aspect,
	norm = colors.CenteredNorm(vcenter = 0),
	cmap = 'coolwarm'
)
plt.colorbar(im)

plt.show()