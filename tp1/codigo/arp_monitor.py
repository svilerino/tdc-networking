#!/usr/bin/python
import pylab
import math
import numpy
import matplotlib
import pygraphviz as pgv
import datetime
from scapy.all import *


class Package(object):
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination
        self.time = datetime.datetime.now()

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
        self.data = {}
        self.entropy_list = []

    def add_to_graph(self, package):
        try:
            actual_weight = int(self.graph.get_edge(*package.as_edge()).attr['label'])
        except KeyError:
            self.graph.add_edge(package.as_edge())
            actual_weight = 0
        self.graph.get_edge(*package.as_edge()).attr['label'] = str(actual_weight + 1)

    def add_to_data(self, package):
        self.data.setdefault(package.destination, []).append(package.source)

    def add_package(self, package):
        self.add_to_graph(package)
        self.add_to_data(package)
        self.get_entropy()

    def get_entropy(self):
        time = datetime.datetime.now()
        total = sum([len(value) for value in self.data.values()])
        probabilities = dict([(key, len(value) / float(total)) for key, value in self.data.iteritems()])
        entropy = sum([-math.log(p, 2) * p for p in probabilities.values()])
        self.entropy_list.append({'entropy': entropy, 'probabilities': probabilities, 'time': time})
        print probabilities

    def draw_entropy(self):
        x = matplotlib.dates.date2num([e['time'] for e in self.entropy_list])
        y = [e['entropy'] for e in self.entropy_list]
        pylab.figure()
        fig, ax = pylab.subplots()
        pylab.setp(pylab.xticks()[1], rotation=30, ha='right')
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M'))
        pylab.plot_date(x, y)
        pylab.savefig('entropy.png', bbox_inches='tight')
        pylab.close()

    def draw_graph(self):
        self.graph.layout(prog='dot')
        self.graph.draw('graph.png')

    def draw_histogram(self):
        data = dict([(key, len(value)) for key, value in self.data.iteritems()])
        histogram = Histogram(name='data', data=data)
        histogram.draw()

    def draw(self):
        self.draw_graph()
        self.draw_histogram()
        self.draw_entropy()


def monitor_callback(pkt):
    package = Package(source=pkt.psrc, destination=pkt.pdst)
    PackageStatistics.get_instance().add_package(package)
    PackageStatistics.get_instance().draw()
    print pkt.sprintf("from %ARP.psrc% to %ARP.pdst%")


if __name__ == '__main__':
    sniff(prn=monitor_callback, filter="arp", store=0)