import matplotlib.pyplot as plt
import numpy as np

def plothist(arr):
	# expects complex input, hence the np.abs
	plt.hist(np.abs(arr), bins = 100)
	plt.show()