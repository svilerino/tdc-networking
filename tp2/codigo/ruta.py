#!/usr/bin/python
# coding=utf-8
import urllib2
import json
import httplib
import numpy
from mapplotter import MapPlotter
from distrplotter import BarPlotter

class Ruta:
    def __init__(self, dst_host, max_hops, zscore_threshold):
        self.zscore_threshold=zscore_threshold
        self.dst_host = dst_host    
        self.max_hops = max_hops    
        self.hop_ip_list = []
        self.hop_location_list = []
        self.hop_name_list = []
        self.hop_rtt = []
        self.hop_rtt_acum = []
        self.hop_response = []
        self.hop_zrtt = []
        self.rtt_mean=0.0
        self.rtt_stdev=0.0

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
            query_response = json.loads(urllib2.urlopen("http://freegeoip.net/json/" + ip_host).read())
            return query_response
        except (ValueError, KeyError, TypeError, urllib2.URLError, httplib.BadStatusLine):
            print "Unable to solve IP GeoLocation(" + ip_host + ")"
            return {"country_name":"(Unknown Country?)", "city":"(Unknown City?)", "latitude": "None", "longitude":"None"}   

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
            print "IP GeoLocation Result: " + ip_location["country_name"], ip_location["city"], ip_location["latitude"], ip_location["longitude"]
        else:
            self.hop_name_list.append(ip)
            self.hop_location_list.append({"country_name":"(Unknown Country?)", "city":"(Unknown City?)", "latitude": "None", "longitude":"None"})

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
                calculated_rtt=(self.hop_rtt_acum[current_hop_index]-self.hop_rtt_acum[nearest_hop_behind])/float(current_hop_index-nearest_hop_behind)
                #set calculated rtt
                self.hop_rtt.append(round(calculated_rtt, 3))
                
                #fill gaps of unknown hops in the middle of current hop and nearest hop behind
                for i in range(nearest_hop_behind+1, current_hop_index):
                    #print str(self.hop_ip_list[i]) + " rtt is " + str(round(calculated_rtt, 3))
                    self.hop_rtt[i]=round(calculated_rtt, 3)

                
                print "Incremental RTT time is " + str(round(calculated_rtt, 3))
            else:
                self.hop_rtt.append("*")

    def make_statistics(self):
        effective_sample=[]        
        for rtt in self.hop_rtt:
            if rtt != "*":
                effective_sample.append(rtt)
        
        rtt_mean=round(numpy.mean(effective_sample), 3)
        rtt_stdev=round(numpy.std(effective_sample), 3)        
        #actualizamos los datos de la clase
        self.rtt_mean=rtt_mean
        self.rtt_stdev=rtt_stdev

        #calculamos zscores
        hop_index=0
        for rtt in self.hop_rtt:
            if rtt != "*":
                zrtti = (self.hop_rtt[hop_index] - rtt_mean)/float(rtt_stdev)
                self.hop_zrtt.append(round(zrtti, 3)) 
            else:
                self.hop_zrtt.append("*") 
            hop_index+=1            

    def save_trace(self):
        file_ = open("Traceroute to " + self.dst_host + ".txt", 'w')
        file_.write("Traceroute a " + str(self.dst_host) + " (max " + str(self.max_hops) + " hops)")
        file_.write("\n")
        file_.write("Hop Score\tHop#\tHop IP\t\tHop RTT Acumulado\tHop RTT Incremental\tHop Resp. Type\tHop Location\t\t\t\t\tHop Name")
        file_.write("\n")
        hop_index = 1
        for hop in self.hop_ip_list:
            file_.write(str(self.hop_zrtt[hop_index-1]) + "\t\t" + str(hop_index) + "\t" + str(hop) + "\t" + str(self.hop_rtt_acum[hop_index-1]) + "\t\t\t" + str(self.hop_rtt[hop_index-1]) + "\t\t\t" + str(self.hop_response[hop_index-1]) + "\t" + self.hop_location_list[hop_index-1]["country_name"] + ", " + self.hop_location_list[hop_index-1]["city"] + "\t\t" + self.hop_name_list[hop_index-1])
            file_.write("\n")
            hop_index+=1

        file_.write("")
        file_.write("\n")
        file_.write("----------------------------------------------------------------------")
        file_.write("\n")
        file_.write("")
        file_.write("\n")
        file_.write("Nodos distinguidos hacia " + str(self.dst_host))
        file_.write("\n")
        file_.write("Hop Score\tHop#\tHop IP\t\tHop RTT Acumulado\tHop RTT Incremental\tHop Resp. Type\tHop Location\t\t\t\t\tHop Name")
        file_.write("\n")
        hop_index = 1
        for hop in self.hop_ip_list:
            if self.hop_zrtt[hop_index-1] != "*" and self.hop_zrtt[hop_index-1] > self.zscore_threshold:
                file_.write(str(self.hop_zrtt[hop_index-1]) + "\t\t" + str(hop_index) + "\t" + str(hop) + "\t" + str(self.hop_rtt_acum[hop_index-1]) + "\t\t\t" + str(self.hop_rtt[hop_index-1]) + "\t\t\t" + str(self.hop_response[hop_index-1]) + "\t" + self.hop_location_list[hop_index-1]["country_name"] + ", " + self.hop_location_list[hop_index-1]["city"] + "\t\t" + self.hop_name_list[hop_index-1])
                file_.write("\n")
            hop_index+=1
        file_.write("promedio de RTT entre hops: " + str(self.rtt_mean))
        file_.write("\n")
        file_.write("stdev de RTT entre hops: " + str(self.rtt_stdev))
        file_.write("\n")
        file_.close()

    def display_trace(self):
        #imprimimos la lista de hops
        print ""
        print "----------------------------------------------------------------------"      
        print ""
        print "Traceroute a " + str(self.dst_host) + " (max " + str(self.max_hops) + " hops)"
        print "Hop Score\tHop#\tHop IP\t\tHop RTT Acumulado\tHop RTT Incremental\tHop Resp. Type\tHop Location\t\t\t\t\tHop Name"
        hop_index = 1
        for hop in self.hop_ip_list:
            print str(self.hop_zrtt[hop_index-1]) + "\t\t" + str(hop_index) + "\t" + str(hop) + "\t" + str(self.hop_rtt_acum[hop_index-1]) + "\t\t\t" + str(self.hop_rtt[hop_index-1]) + "\t\t\t" + str(self.hop_response[hop_index-1]) + "\t" + self.hop_location_list[hop_index-1]["country_name"] + ", " + self.hop_location_list[hop_index-1]["city"] + "\t\t" + self.hop_name_list[hop_index-1]
            hop_index+=1

        print ""
        print "----------------------------------------------------------------------"      
        print ""
        print "Nodos distinguidos hacia " + str(self.dst_host)
        print "Hop Score\tHop#\tHop IP\t\tHop RTT Acumulado\tHop RTT Incremental\tHop Resp. Type\tHop Location\t\t\t\t\tHop Name"
        hop_index = 1
        for hop in self.hop_ip_list:
            if self.hop_zrtt[hop_index-1] != "*" and self.hop_zrtt[hop_index-1] > self.zscore_threshold:
                print str(self.hop_zrtt[hop_index-1]) + "\t\t" + str(hop_index) + "\t" + str(hop) + "\t" + str(self.hop_rtt_acum[hop_index-1]) + "\t\t\t" + str(self.hop_rtt[hop_index-1]) + "\t\t\t" + str(self.hop_response[hop_index-1]) + "\t" + self.hop_location_list[hop_index-1]["country_name"] + ", " + self.hop_location_list[hop_index-1]["city"] + "\t\t" + self.hop_name_list[hop_index-1]
            hop_index+=1
        print "promedio de RTT entre hops: " + str(self.rtt_mean)
        print "stdev de RTT entre hops: " + str(self.rtt_stdev)

    def plot_map(self):
        filename=self.dst_host + "_map_trace"
        idx=0
        titles=[]
        scores=[]
        lats=[]
        lons=[]
        for hop in self.hop_ip_list:
            if self.hop_location_list[idx]["latitude"] != "None" and self.hop_location_list[idx]["latitude"] != None and self.hop_location_list[idx]["latitude"] != 0:
                scores.append(self.hop_zrtt[idx])
                title=hop
                if self.hop_location_list[idx]["country_name"] != "(Unknown Country?)":
                    title=title + "\n" + self.hop_location_list[idx]["country_name"]
                if self.hop_location_list[idx]["city"] != "(Unknown city?)":
                    title=title + "\n" + self.hop_location_list[idx]["city"]
                titles.append(hop)

                lats.append(float(self.hop_location_list[idx]["latitude"]))
                lons.append(float(self.hop_location_list[idx]["longitude"]))
            idx+=1

        print titles
        print scores
        print lats
        print lons
        plot = MapPlotter(lats, lons, titles, scores, filename)
        plot.plot()

    def plot_rtt(self):
        #plot rtt bar chart
        filename=self.dst_host + "_bar_rtt"
        data_rtt=[]
        hop_idx=0
        for hop in self.hop_ip_list:
            if hop != "\t*":
                data_rtt.append((hop, self.hop_rtt[hop_idx]))
            hop_idx+=1

        plot = BarPlotter(filename, "RTT", data_rtt, "Distribucion de RTT")
        plot.plot()

    def plot_rtt_acum(self):
        #plot rtt bar chart
        filename=self.dst_host + "_bar_rtt_acum"
        data_rtt=[]
        hop_idx=0
        for hop in self.hop_ip_list:
            if hop != "\t*":
                data_rtt.append((hop, self.hop_rtt_acum[hop_idx]))
            hop_idx+=1

        plot = BarPlotter(filename, "RTT", data_rtt, "Distribucion de RTT Acumulado")
        plot.plot()

    def plot_zscore(self):
        #plot zscore bar chart
        filename=self.dst_host + "_bar_zscore"
        data_zscore=[]
        hop_idx=0
        for hop in self.hop_ip_list:
            if hop != "\t*":
                data_zscore.append((hop, self.hop_zrtt[hop_idx]))
            hop_idx+=1

        plot = BarPlotter(filename, "ZScore", data_zscore, "Distribucion de ZScore")
        plot.plot()