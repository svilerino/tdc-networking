#!/usr/bin/python
# coding=utf-8
import urllib2
import json
import httplib

class Ruta:
    def __init__(self, dst_host, max_hops):
        self.dst_host = dst_host    
        self.max_hops = max_hops    
        self.hop_ip_list = []
        self.hop_location_list = []
        self.hop_name_list = []
        self.hop_rtt = []
        self.hop_rtt_acum = []
        self.hop_response = []

    def calculate_nearest_hop_behind(self, hop_index):
        if hop_index==0:
            return 0
        else:
            i=hop_index-1
            while i>0 and self.hop_response[i]!="Time exceeded":
                i-=1
            #en i tengo el hop anterior mas cercano con time exceeded o primer hop
            return i

    def solve_ip_location(self, ip_host):
        try:
            query_response = json.loads(urllib2.urlopen("http://api.hostip.info/get_json.php?ip=" + ip_host + "&position=true").read())
            return query_response
        except (ValueError, KeyError, TypeError, urllib2.URLError, httplib.BadStatusLine):
            print "Unable to solve IP GeoLocation(" + ip_host + ")"
            return {"country_name":"(Unknown Country?)", "city":"(Unknown City?)", "lat": "(Unknown)", "lng":"(Unknown)"}

    def solve_host_name(self, ip_host):
        try:
            query_response = json.loads(urllib2.urlopen("http://api.statdns.com/x/" + ip_host).read())
            for ans in query_response["answer"]:
                #print ans["type"], ans["rdata"]
                if ans["type"] == "PTR":
                    #me quedo con este nombre de host!
                    return ans["rdata"]
        except (ValueError, KeyError, TypeError, urllib2.URLError, httplib.BadStatusLine):
            print "Unable to solve reverse DNS(" + ip_host + ")"
            return "(Unknown)"

    def add_hop(self, ip, rtt, response_type):
        #agrego informacion sobre el salto
        self.hop_ip_list.append(ip)
        self.hop_rtt_acum.append(rtt)
        self.hop_response.append(response_type)

        #si tengo info de un hop o destino, obtengo info de el
        if response_type == "Time exceeded" or response_type == "Echo reply":
            #resuelvo el nombre del host por reverse dns lookup
            host_name=self.solve_host_name(ip)
            print "DNS Forward query: " + host_name
            self.hop_name_list.append(host_name)
            
            #obtengo geolocalizacion aproximada
            ip_location = self.solve_ip_location(ip)
            self.hop_location_list.append(ip_location)
            print "IP GeoLocation Result: " + ip_location["country_name"], ip_location["city"], ip_location["lat"], ip_location["lng"]
        else:
            self.hop_name_list.append(ip)
            self.hop_location_list.append({"country_name":"(Unknown Country?)", "city":"(Unknown City?)", "lat": "(Unknown)", "lng":"(Unknown)"})

        #calculo el RTT incremental    
        if len(self.hop_ip_list) == 1:
            #hay un solo hop, el rtt acumulado, es igual al rtt entre 2 hosts
            self.hop_rtt.append(rtt)
            print "Nearest hop behind " + self.hop_ip_list[0] + " is " + self.hop_ip_list[0]
            print "Incremental RTT time is " + str(rtt)
        else:            
            if response_type == "Time exceeded" or response_type == "Echo reply":
                #calcular hop entre i y i-1
                current_hop_index = len(self.hop_ip_list)-1#ultimo indice de la lista de hops
                nearest_hop_behind = self.calculate_nearest_hop_behind(current_hop_index)
                print "Nearest hop behind " + self.hop_ip_list[current_hop_index] + " is " + self.hop_ip_list[nearest_hop_behind]
                calculated_rtt=self.hop_rtt_acum[current_hop_index]-self.hop_rtt_acum[nearest_hop_behind]
                self.hop_rtt.append(calculated_rtt)
                print "Incremental RTT time is " + str(calculated_rtt)
            else:
                self.hop_rtt.append("*")

    def display_trace(self):
        #imprimimos la lista de hops
        print ""
        print "----------------------------------------------------------------------"      
        print ""
        print "Traceroute a " + str(self.dst_host) + " (max " + str(self.max_hops) + " hops)"
        print "Hop#\tHop IP\t\tHop RTT Acumulado\tHop RTT Incremental\tHop Resp. Type\tHop Location\t\t\t\tHop Name"
        hop_index = 1
        for hop in self.hop_ip_list:
            print str(hop_index) + "\t" + str(hop) + "\t" + str(self.hop_rtt_acum[hop_index-1]) + "\t\t\t" + str(self.hop_rtt[hop_index-1]) + "\t\t\t" + str(self.hop_response[hop_index-1]) + "\t" + self.hop_location_list[hop_index-1]["country_name"] + ", " + self.hop_location_list[hop_index-1]["city"] + "\t\t" + self.hop_name_list[hop_index-1]
            hop_index+=1