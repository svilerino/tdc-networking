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
        ip_point_table=[]
    	data=self.plot_data        
    	#print data
        N = len( data )
        x = np.arange(1, N+1)
        y = [ num for (s, num) in data ]

        #labels = [ s for (s, num) in data ]
        for i in x:
            ip_point_table.append(data[i-1][0])

        width = 1
        bar1 = plt.bar( x, y, width, color="#ffa500", align="center")
        plt.title(self.title)
        plt.ylabel(self.y_axis_title)
        plt.xlabel("Hops")
        #plt.xticks(x + width/2.0, ip_point_table, rotation=17 )
        plt.xticks(x, x)
        plt.grid(True)
        #plt.show()

        #Draw Hops IP Table
        str_to_print="Hops - IP Table\n"
        iptable_idx=0
        for ip in ip_point_table:
            str_to_print = str_to_print + str(iptable_idx+1) + " - " + ip + "\n"
            iptable_idx+=1

        bboxprops = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        plt.text(1, 1,str_to_print, style='italic', bbox=bboxprops)

        plt.savefig(self.filename + ".svg", format="svg" )
        plt.close()