import sys
from glob import glob
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

#http://stackoverflow.com/questions/25383698/error-string-to-bool-in-mplot3d-workaround-found

class Data:
	def __init__(self):
		self.alfas = []
		self.alfasRep = []
		self.betas = []
		self.betasRep = []
		self.rtos = []
		self.rtts = []
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
			
			#ignoro archivos vacios
			if len(lines) == 0:
				continue

			#Parseo

			rttsTmp = []
			rtosTmp = []

			for line in lines:
				line = line.split()
				if len(line)==4:
					delay = float(line[0])
					pError = float(line[1])
					alfa = float(line[2])
					beta = float(line[3])
				if len(line)==2:
					rttsTmp.append(float(line[0]))
					rtosTmp.append(float(line[1]))

			self.alfas.append(alfa)
			self.betas.append(beta)
			self.rtosProm.append(sum(rtosTmp)/len(rtosTmp))
			self.rttsProm.append(sum(rttsTmp)/len(rttsTmp))
			self.delays.append(delay)
			self.pErrors.append(pError)
			self.rtts.append(rttsTmp)
			self.rtos.append(rtosTmp)
			rttsTmp = []
			rtosTmp = []

		self.alfasRep = [[a]*len(self.alfas) for a in self.alfas]
		self.betasRep = [[b]*len(self.betas) for b in self.betas]

	def show(self):
		print "Alphas: "
		print self.alfas
		print "-----------------"
		print "Betas: "
		print self.betas
		print "-----------------"
		print "Delays: "
		print self.delays
		print "-----------------"
		print "pErros: "
		print self.pErrors
		print "-----------------"
		print "RTO prom: "
		print self.rtosProm
		print "-----------------"
		print "RTT prom: "
		print self.rttsProm
		print "-----------------"
		print "RTO's: "
		print self.rtos
		print "-----------------"
		print "RTT's: "
		print self.rtts

def graph(data, ejex, ejey, ejez, graph_type, color_param):
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	ax.set_xlabel(ejex)
	ax.set_ylabel(ejey)
	ax.set_zlabel(ejez)


	if(graph_type == 1):
		ax.plot(data.alfas, data.betas, data.rtosProm, color=color_param)

	if(graph_type == 2):
		ax.plot_wireframe(data.alfasRep, data.betasRep, data.rtos, color=color_param)

	if(graph_type == 3):
		ax.plot_surface(data.alfas, data.betas, data.rtosProm, color=color_param)

	#plt.show()
	plt.savefig("grafico.png")

if __name__ == '__main__':

	d = Data()
#	print d.alfas
#	print d.betas
#	print d.rtosProm
#	print d.rttsProm
	
	ejex = "Alfa"
	ejey = "Beta"
	ejez = "RTO"
#	d.show()

	graph_type = 2#tipo grafico(ver ifs en metodo graph)
	color_param = "blue"
	graph(d, ejex, ejey, ejez, graph_type, color_param)
		
