from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties

msize_min_limit=0.75
msize_max_limit=1.1

class MapPlotter:
    def __init__(self, lats, lons, titles, scores, filename):
        self.lats=lats
        self.lons=lons
        self.titles=titles
        self.scores=scores
        self.filename=filename

    def plot(self):
        #map instantiation and configuration
        map = Basemap(projection='robin', lat_0=0, lon_0=-100,
                      resolution='h', area_thresh=1000.0)
         
        #image map
        #map.bluemarble()
        map.etopo()
        
        #vectorial map
        #map.drawcoastlines()
        #map.drawcountries()
        #map.drawmapboundary()
        #map.drawrivers()
        #map.drawmeridians(np.arange(0, 360, 30))
        #map.drawparallels(np.arange(-90, 90, 30))
         
        ip_point_table=[]
        next_ip_index_in_table=0
        min_marker_size = 8
        for lon, lat, msize, ip_number in zip(self.lons, self.lats, self.scores, self.titles):
            x,y = map(lon, lat)

            #msize min limit code
            if msize < 0.1:
                msize=msize_min_limit

            #msize max limit code
            if msize > msize_max_limit :
                msize=msize_max_limit

            msize = msize * min_marker_size

            print ip_number + " msize: " + str(msize)
            ip_point_table.append(ip_number)
            next_ip_index_in_table+=1

            map.plot(x, y, 'b*', markersize=msize)
            font = FontProperties()
            font.set_weight('normal')
            font.set_size(8)
            #plt.text(x+10000, y+5000, "Hop#" + str(next_ip_index_in_table), fontproperties=font)

            bboxprops = dict(boxstyle='round', facecolor='wheat', alpha=0.30)
            plt.text(x+10000, y+5000, "Hop#" + str(next_ip_index_in_table), bbox=bboxprops, fontproperties=font)

        # draw great circle route between the points
        for i in range(1, len(self.titles)):
            print "Drawing route from " + self.titles[i-1] + " to " + self.titles[i]
            map.drawgreatcircle(self.lons[i-1], self.lats[i-1], self.lons[i], self.lats[i], linewidth=1.25, color='r')

        #Draw Hops IP Table
        str_to_print="Hops - IP Table\n"
        iptable_idx=0
        for ip in ip_point_table:
            str_to_print = str_to_print + str(iptable_idx+1) + " - " + ip + "\n"
            iptable_idx+=1

        bboxprops = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        #plt.text(10000, 5000, str_to_print, style='italic', bbox=bboxprops)
        plt.text(10000, 10, str_to_print, style='italic', bbox=bboxprops)

        plt.show()
        #plt.savefig(self.filename + ".jpg", format="jpg" )