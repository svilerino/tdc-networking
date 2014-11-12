import sys
from glob import glob
import os
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

class Data:
	def __init__(self):
		self.alfas = []
		self.betas = []
		self.rtosProm = []
		self.rttsProm = []
		self.delays = []
		self.pErrors = []
		self.fill_with_data()

	def fill_with_data(self):
		path="../experimentos"
		for filename in sorted(glob(os.path.join(path, '*.resultado'))):
			file = open(filename, "r")
			lines = file.readlines()

			rtts = []
			rtos = []

			for line in lines:
				line = line.split()
				if len(line)==4:
					delay = float(line[0])
					pError = float(line[1])
					alfa = float(line[2])
					beta = float(line[3])
				if len(line)==2:
					rtts.append(float(line[0]))
					rtos.append(float(line[1]))

			self.alfas.append(alfa)
			self.betas.append(beta)
			self.rtosProm.append(sum(rtos)/len(rtos))
			self.rttsProm.append(sum(rtts)/len(rtts))
			self.delays.append(delay)
			self.pErrors.append(pError)
			rtts = []
			rtos = []

def graph(data, ejex, ejey, ejez):
	plt.xlim=([0,1])
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
#	for c, z in zip(['r', 'g', 'b', 'y', 'r']*5, data.betas):
	for c, z in zip(['r', 'g', 'b'], data.betas):

	    xs = data.alfas
	    ys = data.rtosProm
	    ys = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]

	    # You can provide either a single color or an array. To demonstrate this,
	    # the first bar of each set will be colored cyan.
	    cs = [c] * len(xs)
	    cs[0] = 'c'
	    ax.bar(xs, ys, zs=z, zdir='y', color=cs, alpha=0.8)

	ax.set_xlabel(ejex)
	ax.set_ylabel(ejey)
	ax.set_zlabel(ejez)


	plt.show()

if __name__ == '__main__':
	d = Data()
	ejex = "Alfa"
	ejey = "Beta"
	ejez = "RTO"
	#graph(d,ejex,ejey,ejez)

#	print d.alfas
#	print d.betas
#	print d.rtosProm
#	print d.rttsProm

	graph(d,ejex,ejey,ejez)
		