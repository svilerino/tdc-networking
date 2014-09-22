#!/usr/bin/python
# coding=utf-8
import pylab
import math
import numpy
import matplotlib
import pygraphviz as pgv
import datetime
import urllib2
import json
import httplib
from scapy.all import *

mac_disp_table = dict()
ip_disp_table = dict()

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))
   
def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

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

    def set_src(self, source):
        self.source=source

    def set_dst(self, destination):
        self.destination=destination


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

    def draw_probabilities(self):
        #calculate probabilities
        total_events = sum([amount for amount in self.data.values()])#sumo la cantidad total de paquetes de todas las ips
        normalized_values = [value/float(total_events) for value in self.data.values()]
        pylab.figure()
        X = numpy.arange(len(self.data))
        pylab.bar(X, normalized_values, align='center', width=0.5)
        pylab.xticks(X, self.data.keys(), rotation='vertical')
        pylab.ylim(0, 1)#probabilidades siempre entre 0 y 1...
        pylab.savefig('%s_probabilities.png' % self.name, bbox_inches='tight')
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
        # ----- Atributos de grafo -----
        self.graph.graph_attr['label'] = 'Esquema de red'        
        self.graph.graph_attr['ratio'] = 0.4

        # ----- Atributos de aristas -----
        self.graph.edge_attr['style']='setlinewidth(2)'
        
        # ----- Atributos de nodos -----
        self.graph.node_attr['fontsize'] = '11'
        self.graph.node_attr['style']='filled'
        #self.graph.node_attr['fillcolor']='#BABABA'
        self.graph.node_attr['fillcolor']='#EFEFEF'
        self.graph.node_attr['fontcolor']='#000000'

        # Entropys
        self.entropy_dst = EntropyStatistics(name='entropy_dst')
        self.entropy_src = EntropyStatistics(name='entropy_src')

        # Histograms
        self.histogram_dst = Histogram(name='histogram_dst')
        self.histogram_src = Histogram(name='histogram_src')

    def add_to_graph(self, package):
        # ----- Set color for directed edge -----
        if package.operation == 'who-has':
            edge_color='red'
        elif package.operation == 'is-at':
            edge_color='green'
            
        # ----- Update graph edge weigth -----                
        try:
            actual_weight = int(self.graph.get_edge(*package.as_edge()).attr['label'])
        except KeyError:
            self.graph.add_edge(package.as_edge(), color=edge_color)
            actual_weight = 0
        actual_weight = actual_weight + 1
        self.graph.get_edge(*package.as_edge()).attr['label'] = str(actual_weight)
        
        # ----- Update ip definition with metadata(company vendor) -----
        if (package.as_edge()[0] in ip_disp_table):
            disp_descr=str(ip_disp_table[package.as_edge()[0]])
            print "Se descubrio que la IP " + package.as_edge()[0] + " corresponde a " + disp_descr
            node_src = self.graph.get_node(package.as_edge()[0])
            node_src.attr['label'] = disp_descr

        # ----- Update destination node color in function of its "who-has" activity -----
        if(package.operation == 'who-has'):            
            if (package.as_edge()[1] in ip_disp_table):
                disp_descr=str(ip_disp_table[package.as_edge()[1]])
                if(self.graph.has_node(disp_descr)):                    
                    node_dst = self.graph.get_node(disp_descr)
                else:
                    node_dst = self.graph.get_node(package.as_edge()[1])
            else:
                node_dst = self.graph.get_node(package.as_edge()[1])

            new_color = hex_to_rgb(node_dst.attr['fillcolor'])
            red = new_color[0]
            green = new_color[1]
            blue = new_color[2]

            if(blue > 0):
                blue = blue - 15
            elif(green > 0):
                green = green - 15
                blue = 255
            elif(red > 0):
                #cross-over de colores por la vista(intercambio blanco negro fontcolor y bgcolor)
                self.graph.node_attr['fontcolor']='#FFFFFF'
                red = red - 15
                blue = 255
                green = 255
            else:
                blue=0
                green=0
                red=0

            new_color = red, green, blue
            node_dst.attr['fillcolor']="#" + rgb_to_hex(new_color)

    def add_to_entropys(self, package):
        if package.operation == 'who-has':
            self.entropy_dst.add_info(package.destination)
            self.entropy_src.add_info(package.source)

    def add_to_histograms(self, package):
        if package.operation == 'who-has':
            self.histogram_dst.increase_column(package.destination)
            self.histogram_src.increase_column(package.source)

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

    def draw_histograms(self):
        self.histogram_src.draw()
        self.histogram_src.draw_probabilities()
        self.histogram_dst.draw()
        self.histogram_dst.draw_probabilities()

    def draw(self):
        self.draw_graph()
        self.draw_histograms()
        self.draw_entropys()

def monitor_callback(pkt):
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
            vendor_src = "Ip Addr: " + pkt.psrc +  "\\nMac Addr: " + pkt.hwsrc + "\\nCompany: " + vendor_src[0]["company"]
        except (ValueError, KeyError, TypeError):
            vendor_src = pkt.hwsrc
    else:
        vendor_src = pkt.hwsrc

    if pkt.hwdst != "00:00:00:00:00:00":
        try:
            vendor_dst = json.loads(urllib2.urlopen("http://www.macvendorlookup.com/api/v2/" + pkt.hwdst).read())
            #print json.dumps(vendor_dst, sort_keys=True, indent=4)
            vendor_dst = "Ip Addr: " + pkt.pdst +  "\\nMac Addr: " + pkt.hwdst + "\\nCompany: " + vendor_dst[0]["company"]
        except (ValueError, KeyError, TypeError, urllib2.URLError, httplib.BadStatusLine):
            vendor_dst = pkt.hwdst
    else:
        vendor_dst = pkt.hwdst

    # -------- Print info -------
    print "ARP '" + arp_operation_name + "' operation was sent from (" + vendor_src + ")" + " to (" + vendor_dst + ")"

    # -------- Update mac disp table -------
    mac_disp_table[pkt.hwsrc] = vendor_src

    # -------- Update disp table to file and print it -------    
    print " ------ Updated dispositives table:  ------ "    
    for mac, disp in mac_disp_table.iteritems():
        print "| " + disp + " |"
    print "------------------------------------------------------------------------------------------------------------------------------------------------------"
    
    f = open("mac_disp_table.txt", "w")    
    f.write(" ------ Discovered dispositives in network table:  ------ \n")
    for mac, disp in mac_disp_table.iteritems():
        f.write("| " + disp + " |\n")
    f.write("------------------------------------------------------------------------------------------------------------------------------------------------------")
    f.close()

    # -------- Update ip disp table -------
    ip_disp_table[pkt.psrc] = vendor_src

    # ----- Update statistics -----
    package = Package(source=pkt.psrc, destination=pkt.pdst, operation=pkt.op)
    PackageStatistics.get_instance().add_package(package)
    PackageStatistics.get_instance().draw()

if __name__ == '__main__':
    sniff(prn=monitor_callback, filter="arp", store=0)
