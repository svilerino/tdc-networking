#!/usr/bin/python
import pylab
import math
import numpy
import matplotlib
import pygraphviz as pgv
import datetime
from scapy.all import *


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
    def __init__(self, name, data):
        self.name = name
        self.data = data

    def draw(self):
        pylab.figure()
        X = numpy.arange(len(self.data))
        pylab.bar(X, self.data.values(), align='center', width=0.5)
        pylab.xticks(X, self.data.keys(), rotation='vertical')
        pylab.ylim(0, max(self.data.values()) + 1)
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
        self.data_dst = {}
        self.data_dst_who_has = {}
        self.data_src = {}
        self.data_src_who_has = {}
        self.entropy_list_dst = []
        self.entropy_list_dst_who_has = []
        self.entropy_list_src = []
        self.entropy_list_src_who_has = []

    def add_to_graph(self, package):
        try:
            actual_weight = int(self.graph.get_edge(*package.as_edge()).attr['label'])
        except KeyError:
            self.graph.add_edge(package.as_edge())
            actual_weight = 0
        self.graph.get_edge(*package.as_edge()).attr['label'] = str(actual_weight + 1)

    def add_to_data(self, package):
        self.data_dst.setdefault(package.destination, []).append(package.source)
        self.data_src.setdefault(package.source, []).append(package.destination)
        if package.operation == 'who-has':
			self.data_dst_who_has.setdefault(package.destination, []).append(package.source)
			self.data_src_who_has.setdefault(package.source, []).append(package.destination)

    def add_package(self, package):
        self.add_to_graph(package)
        self.add_to_data(package)
        self.get_entropy_dst()
        self.get_entropy_src()
        self.get_entropy_dst_who_has()
        self.get_entropy_src_who_has()
        
    def get_entropy_dst_who_has(self):
        time = datetime.datetime.now()
        total = sum([len(value) for value in self.data_dst_who_has.values()])
        probabilities = dict([(key, len(value) / float(total)) for key, value in self.data_dst_who_has.iteritems()])
        entropy = sum([-math.log(p, 2) * p for p in probabilities.values()])
        self.entropy_list_dst_who_has.append({'entropy': entropy, 'probabilities': probabilities, 'time': time})
        print probabilities

    def get_entropy_src_who_has(self):
        time = datetime.datetime.now()
        total = sum([len(value) for value in self.data_src_who_has.values()])
        probabilities = dict([(key, len(value) / float(total)) for key, value in self.data_src_who_has.iteritems()])
        entropy = sum([-math.log(p, 2) * p for p in probabilities.values()])
        self.entropy_list_src_who_has.append({'entropy': entropy, 'probabilities': probabilities, 'time': time})
        print probabilities

    def get_entropy_dst(self):
        time = datetime.datetime.now()
        total = sum([len(value) for value in self.data_dst.values()])
        probabilities = dict([(key, len(value) / float(total)) for key, value in self.data_dst.iteritems()])
        entropy = sum([-math.log(p, 2) * p for p in probabilities.values()])
        self.entropy_list_dst.append({'entropy': entropy, 'probabilities': probabilities, 'time': time})
        print probabilities

    def get_entropy_src(self):
        time = datetime.datetime.now()
        total = sum([len(value) for value in self.data_src.values()])
        probabilities = dict([(key, len(value) / float(total)) for key, value in self.data_src.iteritems()])
        entropy = sum([-math.log(p, 2) * p for p in probabilities.values()])
        self.entropy_list_src.append({'entropy': entropy, 'probabilities': probabilities, 'time': time})
        print probabilities

    def draw_entropy_dst(self):
        x = matplotlib.dates.date2num([e['time'] for e in self.entropy_list_dst])
        y = [e['entropy'] for e in self.entropy_list_dst]
        pylab.figure()
        fig, ax = pylab.subplots()
        pylab.setp(pylab.xticks()[1], rotation=30, ha='right')
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
        pylab.plot_date(x, y)
        pylab.savefig('entropy_dst.png', bbox_inches='tight')
        pylab.close()

    def draw_entropy_src(self):
        x = matplotlib.dates.date2num([e['time'] for e in self.entropy_list_src])
        y = [e['entropy'] for e in self.entropy_list_src]
        pylab.figure()
        fig, ax = pylab.subplots()
        pylab.setp(pylab.xticks()[1], rotation=30, ha='right')
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
        pylab.plot_date(x, y)
        pylab.savefig('entropy_src.png', bbox_inches='tight')
        pylab.close()
        
    def draw_entropy_dst_who_has(self):
        x = matplotlib.dates.date2num([e['time'] for e in self.entropy_list_dst_who_has])
        y = [e['entropy'] for e in self.entropy_list_dst_who_has]
        pylab.figure()
        fig, ax = pylab.subplots()
        pylab.setp(pylab.xticks()[1], rotation=30, ha='right')
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
        pylab.plot_date(x, y)
        pylab.savefig('entropy_dst_who_has.png', bbox_inches='tight')
        pylab.close()

    def draw_entropy_src_who_has(self):
        x = matplotlib.dates.date2num([e['time'] for e in self.entropy_list_src_who_has])
        y = [e['entropy'] for e in self.entropy_list_src_who_has]
        pylab.figure()
        fig, ax = pylab.subplots()
        pylab.setp(pylab.xticks()[1], rotation=30, ha='right')
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
        pylab.plot_date(x, y)
        pylab.savefig('entropy_src_who_has.png', bbox_inches='tight')
        pylab.close()

    def draw_graph(self):
        self.graph.layout(prog='dot')
        self.graph.draw('graph.png')

    def draw_histogram(self):
        data = dict([(key, len(value)) for key, value in self.data_dst.iteritems()])
        histogram = Histogram(name='data', data=data)
        histogram.draw()

    def draw_entropy(self):
        self.draw_entropy_src()
        self.draw_entropy_src_who_has()
        self.draw_entropy_dst()
        self.draw_entropy_dst_who_has()

    def draw(self):
        self.draw_graph()
        self.draw_histogram()
        self.draw_entropy()


def monitor_callback(pkt):
    package = Package(source=pkt.psrc, destination=pkt.pdst, operation=pkt.op)
    PackageStatistics.get_instance().add_package(package)
    PackageStatistics.get_instance().draw()
    print pkt.sprintf("from %ARP.psrc% to %ARP.pdst%")


if __name__ == '__main__':
    sniff(prn=monitor_callback, filter="arp", store=0)
