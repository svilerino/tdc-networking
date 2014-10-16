from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties

class BarPlotter:
    def __init__(self, filename, y_axis_title, plot_data, title):
    	self.filename=filename
    	self.y_axis_title=y_axis_title
    	self.plot_data=plot_data
    	self.title=title

    def plot(self):
    	data=self.plot_data        
    	#print data
        N = len( data )
        x = np.arange(1, N+1)
        y = [ num for (s, num) in data ]
        labels = [ s for (s, num) in data ]
        width = 1
        bar1 = plt.bar( x, y, width, color="#ffa500", align="center")
        plt.title(self.title)
        plt.ylabel(self.y_axis_title)
        plt.xlabel("Hops")
        plt.xticks(x + width/2.0, labels, rotation=17 )
        plt.grid(True)
        #plt.show()
        plt.savefig(self.filename + ".png", format="png" )
        plt.close()