#!/usr/bin/python
import pylab
import math
import numpy
import matplotlib
import pygraphviz as pgv
import datetime
import urllib2
import json
from scapy.all import *

#mac : disp description table
disp_table = dict()

class Package(object):
    def __init__(self, source, destination, operation):
        self.source = source
        self.destination = destination
        self.time = datetime.datetime.now()
		
        if operation == 1:
            self.operation = 'who-has'
        elif operation == 2:
            self.operation = 'is-at'

    def as_edge(self):
        return self.source, self.destination


class Histogram(object):
    def __init__(self, name):
        self.name = name
        self.data = {}

    def add_column(self, name):
        self.data[name] = 0

    def increase_column(self, name, amount=1):
        self.data.setdefault(name, 0)
        self.data[name] = self.data[name] + amount

    def draw(self):
        pylab.figure()
        X = numpy.arange(len(self.data))
        pylab.bar(X, self.data.values(), align='center', width=0.5)
        pylab.xticks(X, self.data.keys(), rotation='vertical')
        pylab.ylim(0, max(self.data.values()) + 1)
        pylab.savefig('%s.png' % self.name, bbox_inches='tight')
        pylab.close()


class EntropyStatistics(object):
    def __init__(self, name):
        self.name = name
        self.history = []
        self.information = {}

    def add_info(self, info):
        self.information.setdefault(info, 0)
        self.information[info] = self.information[info] + 1
        self.calculate_entropy()

    def calculate_entropy(self):
        time = datetime.datetime.now()
        total = sum(self.information.values())
        probabilities = dict([(key, value / float(total)) for key, value in self.information.iteritems()])
        entropy = sum([-math.log(p, 2) * p for p in probabilities.values()])
        self.history.append({'entropy': entropy, 'probabilities': probabilities, 'time': time})

    def draw(self):
        x = matplotlib.dates.date2num([e['time'] for e in self.history])
        y = [e['entropy'] for e in self.history]
        pylab.figure()
        fig, ax = pylab.subplots()
        pylab.setp(pylab.xticks()[1], rotation=30, ha='right')
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
        pylab.plot_date(x, y)
        pylab.savefig('%s.png' % self.name, bbox_inches='tight')
        pylab.close()
        

class PackageStatistics(object):
    instance = None

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = cls()
        return cls.instance

    def __init__(self):
        self.graph = pgv.AGraph(bgcolor='white', directed=True)

        # Entropys
        self.entropy_dst = EntropyStatistics(name='entropy_dst')
        self.entropy_src = EntropyStatistics(name='entropy_src')
        self.entropy_src_who_has = EntropyStatistics(name='entropy_src_who_has')
        self.entropy_dst_who_has = EntropyStatistics(name='entropy_dst_who_has')

        # Histograms
        self.histogram_dst = Histogram(name='histogram_dst')

    def add_to_graph(self, package):
        try:
            actual_weight = int(self.graph.get_edge(*package.as_edge()).attr['label'])
        except KeyError:
            self.graph.add_edge(package.as_edge())
            actual_weight = 0
        self.graph.get_edge(*package.as_edge()).attr['label'] = str(actual_weight + 1)

    def add_to_entropys(self, package):
        self.entropy_dst.add_info(package.destination)
        self.entropy_src.add_info(package.source)
        if package.operation == 'who-has':
            self.entropy_src_who_has.add_info(package.source)
            self.entropy_dst_who_has.add_info(package.destination)

    def add_to_histograms(self, package):
        self.histogram_dst.increase_column(package.destination)

    def add_package(self, package):
        self.add_to_graph(package)
        self.add_to_entropys(package)
        self.add_to_histograms(package)

    def draw_graph(self):
        self.graph.layout(prog='dot')
        self.graph.draw('graph.png')

    def draw_entropys(self):
        self.entropy_dst.draw()
        self.entropy_src.draw()
        self.entropy_src_who_has.draw()
        self.entropy_dst_who_has.draw()

    def draw_histograms(self):
        self.histogram_dst.draw()

    def draw(self):
        self.draw_graph()
        self.draw_histograms()
        self.draw_entropys()


def monitor_callback(pkt):
#    ls(pkt)  command to get package field list
#   package fields list
    #dst        : DestMACField         = 'ff:ff:ff:ff:ff:ff' (None)
    #src        : SourceMACField       = '1c:6f:65:94:70:68' (None)
    #type       : XShortEnumField      = 2054            (0)
    #--
    #hwtype     : XShortField          = 1               (1)
    #ptype      : XShortEnumField      = 2048            (2048)
    #hwlen      : ByteField            = 6               (6)
    #plen       : ByteField            = 4               (4)
    #op         : ShortEnumField       = 1               (1)
    #hwsrc      : ARPSourceMACField    = '1c:6f:65:94:70:68' (None)
    #psrc       : SourceIPField        = '192.168.1.102' (None)
    #hwdst      : MACField             = '00:00:00:00:00:00' ('00:00:00:00:00:00')
    #pdst       : IPField              = '192.168.1.1'   ('0.0.0.0')
    #--
    #load       : StrField             = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' ('')


    # ------- Parse Operation Type  -------

    if pkt.op == 1:
        arp_operation_name = 'who-has'
    elif pkt.op == 2:
        arp_operation_name = 'is-at'

    # ------- Parse MAC Vendors  -------
    # ------- Parse URL GET response  -------
    if pkt.hwsrc != "00:00:00:00:00:00":
        try:
            vendor_src = json.loads(urllib2.urlopen("http://www.macvendorlookup.com/api/v2/" + pkt.hwsrc).read())
            #print json.dumps(vendor_src, sort_keys=True, indent=4)
            vendor_src = "Ip Addr: " + pkt.psrc +  " - Mac Addr: " + pkt.hwsrc + " - Company: " + vendor_src[0]["company"]
        except (ValueError, KeyError, TypeError):
            vendor_src = pkt.hwsrc
    else:
        vendor_src = pkt.hwsrc

    if pkt.hwdst != "00:00:00:00:00:00":
        try:
            vendor_dst = json.loads(urllib2.urlopen("http://www.macvendorlookup.com/api/v2/" + pkt.hwdst).read())
            #print json.dumps(vendor_dst, sort_keys=True, indent=4)
            vendor_dst = "Ip Addr: " + pkt.pdst +  " - Mac Addr: " + pkt.hwdst + " - Company: " + vendor_dst[0]["company"]
        except (ValueError, KeyError, TypeError):
            vendor_dst = pkt.hwdst
    else:
        vendor_dst = pkt.hwdst

    # -------- Print info -------

    print "ARP '" + arp_operation_name + "' operation was sent from (" + vendor_src + ")" + " to (" + vendor_dst + ")"
    #print pkt.sprintf("from %ARP.psrc% (%ARP.hwsrc%) to %ARP.pdst% (%ARP.hwdst%)")
    
    package = Package(source=pkt.psrc, destination=pkt.pdst, operation=pkt.op)
    #package = Package(source=str(pkt.psrc) + " " + vendor_src, destination=str(pkt.pdst) + " " + vendor_dst, operation=pkt.op)
    PackageStatistics.get_instance().add_package(package)
    PackageStatistics.get_instance().draw()

    # -------- Update disp table -------

    disp_table[pkt.hwsrc] = vendor_src
    print " ------ Updated dispositives table:  ------ "    
    for mac, disp in disp_table.iteritems():
        print "| " + disp + " |"
    print "------------------------------------------------------------------------------------------------------------------------------------------------------"

    # -------- Update disp table to file -------    
    f = open("disp_table.txt", "w")    
    f.write(" ------ Discovered dispositives in network table:  ------ \n")
    for mac, disp in disp_table.iteritems():
        f.write("| " + disp + " |\n")
    f.write("------------------------------------------------------------------------------------------------------------------------------------------------------")
    f.close()

if __name__ == '__main__':
    sniff(prn=monitor_callback, filter="arp", store=0)
