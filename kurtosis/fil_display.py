from sigpyproc.readers import FilReader
import matplotlib.pyplot as plt
import numpy as np
import os

fil = FilReader("outfiles_1139/raw_output.fil")

print(fil.header)

i = 0
blksiz = 1024

while True:
	block = fil.read_block(i, blksiz)
	i += blksiz

	print(block.data.shape)

	#plt.subplot(211)
	plt.title(fil.header.fch1)
	plt.imshow(10 * np.log10(block.data), aspect = block.data.shape[1] / block.data.shape[0])

	#plt.subplot(212)
	#plt.plot(np.sum(10 * np.log10(block.data), axis = 0) / 192)
	plt.show()