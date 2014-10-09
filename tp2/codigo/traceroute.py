#!/usr/bin/python
# coding=utf-8
from scapy.all import *
import sys

#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)

host_dst=sys.argv[1]
max_hops=int(sys.argv[2])

print "Calculating trace to " + host_dst + " with " + str(max_hops) + " max hops..."

for ttl_iter in xrange(1, max_hops):
	res=sr(IP(dst=host_dst, ttl=ttl_iter))
	res[0][ICMP].display()