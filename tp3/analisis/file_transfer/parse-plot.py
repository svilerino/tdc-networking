import sys
from glob import glob
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.cm as cm

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
		self.retransmissions = []
		self.diffsRtoRtt = []
		self.diffsRttVsRTOProm = []
		self.fill_with_data()
		self.export_as_csv()

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
			diffsRtoRttTmp = []
			retr = 0

			for line in lines:
				line = line.split()
				if len(line)==4:
					delay = float(line[0])
					pError = float(line[1])
					alfa = float(line[2])
					beta = float(line[3])
				if len(line)==3:
					rttsTmp.append(float(line[0]))
					rtosTmp.append(float(line[1]))
					diffsRtoRttTmp.append(float(line[2]))
				if len(line)==1:
					retr = int(line[0])

			self.alfas.append(alfa)
			self.betas.append(beta)
			self.rtosProm.append(sum(rtosTmp)/len(rtosTmp))
			self.rttsProm.append(sum(rttsTmp)/len(rttsTmp))
			
			self.diffsRttVsRTOProm.append(sum(diffsRtoRttTmp)/len(diffsRtoRttTmp))
			self.diffsRtoRtt.append(diffsRtoRttTmp)
			self.delays.append(delay)
			self.pErrors.append(pError)
			self.rtts.append(rttsTmp)
			self.rtos.append(rtosTmp)
			self.retransmissions.append(retr)
			self.alfasRep.append([alfa]*len(rtosTmp))
			self.betasRep.append([beta]*len(rtosTmp))
			rttsTmp = []
			rtosTmp = []			
			diffsRtoRttTmp = []

	def export_as_csv(self):
		for i in range(0,len(self.rtts)):
			f = open("../csvs/" + str(self.delays[i]) + "." + str(self.retransmissions[i]) + "." + str(self.alfas[i]) + "." + str(self.betas[i]) + ".csv", "w")
			f.write("RTT,RTO,Diferencia RTT-RTO\n")
			for j in range(0,len(self.rtts[i])):
				f.write(str(self.rtts[i][j]) + "," + str(self.rtos[i][j]) + "," + str(self.diffsRtoRtt[i][j]) + "\n")


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
		print "Retransmissions: "
		print self.retransmissions		
		print "-----------------"
		print "|RTO-RTT| diff: "
		print self.diffsRttVsRTOProm
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

def plot(data, graph_type, file_prefix, label_param):
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')

	if(graph_type == 1):#heatmap alfa beta vs accuracy rto vs rtt	
		title="Aproximacion Rtt vs Rto"
		ax.set_title(title)
		ancho_barra_x=([0.1]*len(data.alfas))
		ancho_barra_y=([0.1]*len(data.alfas))
		pos_inicial_z=([0]*len(data.alfas))
		#con el calculo loco de aca abajo, entre 0 y 1 los valores normalizados indican, mientras mas grande el valor, mas cerca RTT y RTO
		normalized_values = [1-(elem/float(max(data.diffsRttVsRTOProm))) for elem in data.diffsRttVsRTOProm]
		bar_colors_heat = [cm.hot(heat) for heat in normalized_values]
		ejex = "Alpha"
		ejey = "Beta"
		ejez = "Precision"
		ax.set_xlabel(ejex)
		ax.set_ylabel(ejey)
		ax.set_zlabel(ejez)
		#parametros:
		#pos_inicial_x, pos_inicial_y, pos_inicial_z, ancho_barra_x, ancho_barra_y, altura_barra_z, color=color_barras, alpha= transparencia entre 0 y 1
		ax.bar3d(data.alfas, data.betas, pos_inicial_z, ancho_barra_x, ancho_barra_y, normalized_values, color=bar_colors_heat, alpha=1)
		plt.suptitle(label_param)		

		plt.savefig(file_prefix + "_rtt_vs_rto.png")
		#plt.show()
		plt.close()

	if(graph_type == 2):
		title="Cant. Retransmisiones"
		ax.set_title(title)
		ancho_barra_x=([0.1]*len(data.alfas))
		ancho_barra_y=([0.1]*len(data.alfas))
		pos_inicial_z=([0]*len(data.alfas))
		#con el calculo loco de aca abajo, entre 0 y 1 los valores normalizados indican, mientras mas grande el valor, mas cerca RTT y RTO
		normalized_values = [(elem/float(max(data.retransmissions))) for elem in data.retransmissions]
		bar_colors_heat = [cm.hot(heat) for heat in normalized_values]		
		ejex = "Alpha"
		ejey = "Beta"
		ejez = "Cant. Retransmisiones"
		ax.set_xlabel(ejex)
		ax.set_ylabel(ejey)
		ax.set_zlabel(ejez)
		#parametros:
		#pos_inicial_x, pos_inicial_y, pos_inicial_z, ancho_barra_x, ancho_barra_y, altura_barra_z, color=color_barras, alpha= transparencia entre 0 y 1
		ax.bar3d(data.alfas, data.betas, pos_inicial_z, ancho_barra_x, ancho_barra_y, data.retransmissions, color=bar_colors_heat, alpha=1)
		plt.suptitle(label_param)

		plt.savefig(file_prefix + "_retransmisiones.png")
		#plt.show()
		plt.close()

	if(graph_type == 3):
		title="Rtx Timeout(RTO)"
		ax.set_title(title)
		ancho_barra_x=([0.1]*len(data.alfas))
		ancho_barra_y=([0.1]*len(data.alfas))
		pos_inicial_z=([0]*len(data.alfas))
		#con el calculo loco de aca abajo, entre 0 y 1 los valores normalizados indican, mientras mas grande el valor, mas cerca RTT y RTO
		normalized_values = [(elem/float(max(data.rtosProm))) for elem in data.rtosProm]
		bar_colors_heat = [cm.hot(heat) for heat in normalized_values]		
		ejex = "Alpha"
		ejey = "Beta"
		ejez = "RTO"
		ax.set_xlabel(ejex)
		ax.set_ylabel(ejey)
		ax.set_zlabel(ejez)
		#parametros:
		#pos_inicial_x, pos_inicial_y, pos_inicial_z, ancho_barra_x, ancho_barra_y, altura_barra_z, color=color_barras, alpha= transparencia entre 0 y 1
		ax.bar3d(data.alfas, data.betas, pos_inicial_z, ancho_barra_x, ancho_barra_y, data.rtosProm, color=bar_colors_heat, alpha=1)
		plt.suptitle(label_param)

		plt.savefig(file_prefix + "_rto.png")
		#plt.show()
		plt.close()

if __name__ == '__main__':
	data = Data()
	#data.show()
	
	plot(data, 1, sys.argv[1], sys.argv[2])
	plot(data, 2, sys.argv[1], sys.argv[2])
	plot(data, 3, sys.argv[1], sys.argv[2])
