#!/usr/bin/python
import pygraphviz as pgv
from scapy.all import *


class Package(object):
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

    def as_edge(self):
        return self.source, self.destination


class PackageStatistics(object):
    instance = None

    @classmethod
    def get_instance(cls):
        if not cls.instance:
            cls.instance = cls()
        return cls.instance

    def __init__(self):
        self.graph = pgv.AGraph(bgcolor='lightgray', directed=True)

    def add_package(self, package):
        try:
            actual_weight = int(self.graph.get_edge(*package.as_edge()).attr['label'])
        except KeyError:
            self.graph.add_edge(package.as_edge())
            actual_weight = 0
        self.graph.get_edge(*package.as_edge()).attr['label'] = str(actual_weight + 1)

    def get_entropy(self):
        pass

    def draw_graph(self):
        self.graph.layout(prog='dot')
        self.graph.draw('graph.png')


def monitor_callback(pkt):
    package = Package(source=pkt.psrc, destination=pkt.pdst)
    PackageStatistics.get_instance().add_package(package)
    PackageStatistics.get_instance().draw_graph()
    print pkt.sprintf("from %ARP.psrc% to %ARP.pdst%")


if __name__ == '__main__':
    sniff(prn=monitor_callback, filter="arp", store=0)
