from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties

class Plotter:
    def __init__(self, lats, lons, titles, scores):
        self.lats=lats
        self.lons=lons
        self.titles=titles
        self.scores=scores

    def plot(self):
        #map instantiation and configuration
        map = Basemap(projection='robin', lat_0=0, lon_0=-100,
                      resolution='i', area_thresh=1000.0)
         
        map.drawcoastlines()
        map.drawcountries()
        map.bluemarble()
        map.drawmapboundary()
        map.drawrivers()
        map.drawmeridians(np.arange(0, 360, 30))
        map.drawparallels(np.arange(-90, 90, 30))
         
        min_marker_size = 15
        for lon, lat, mag, title in zip(self.lons, self.lats, self.scores, self.titles):
            x,y = map(lon, lat)
            msize = abs(mag/float(5)) * min_marker_size
            print title + " msize: " + str(msize)
            map.plot(x, y, 'ro', markersize=msize)
            font = FontProperties()
            font.set_weight('semibold')
            font.set_size(8)
            plt.text(x+10000, y+5000, title, fontproperties=font)
            #plt.text(x+10000, y+5000, title, bbox=dict(facecolor='yellow', alpha=0.5))             

        # draw great circle route between the points
        for i in range(1, len(self.titles)):
            print "Drawing route from " + self.titles[i-1] + " to " + self.titles[i]
            map.drawgreatcircle(self.lons[i-1], self.lats[i-1], self.lons[i], self.lats[i], linewidth=2, color='g')

        plt.show()