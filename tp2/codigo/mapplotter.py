from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties

msize_limit=1.75

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
         
        map.drawcoastlines()
        map.drawcountries()
        map.bluemarble()
        map.drawmapboundary()
        map.drawrivers()
        map.drawmeridians(np.arange(0, 360, 30))
        map.drawparallels(np.arange(-90, 90, 30))
         
        min_marker_size = 10
        for lon, lat, mag, title in zip(self.lons, self.lats, self.scores, self.titles):
            x,y = map(lon, lat)
            msize = abs(mag)
            
            #msize limit code
            if msize > msize_limit :
                msize=msize_limit

            msize = msize * min_marker_size

            print title + " msize: " + str(msize)
            map.plot(x, y, 'ro', markersize=msize)
            font = FontProperties()
            font.set_weight('semibold')
            font.set_size(5)
            plt.text(x+10000, y+5000, title, fontproperties=font)

        # draw great circle route between the points
        for i in range(1, len(self.titles)):
            print "Drawing route from " + self.titles[i-1] + " to " + self.titles[i]
            map.drawgreatcircle(self.lons[i-1], self.lats[i-1], self.lons[i], self.lats[i], linewidth=1, color='g')

        plt.show()
        #plt.savefig(self.filename + ".jpg", format="jpg" )