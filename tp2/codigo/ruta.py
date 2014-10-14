class Ruta:
    def __init__(self, dst_host, max_hops):
        self.dst_host = dst_host    
        self.max_hops = max_hops    
        self.hop_list = []
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

    def add_hop(self, ip, rtt, response_type):
        #agrego informacion sobre el salto
        self.hop_list.append(ip)
        self.hop_response.append(response_type)

        self.hop_rtt_acum.append(rtt)

        if len(self.hop_list) == 1:
            #hay un solo hop, el rtt acumulado, es igual al rtt entre 2 hosts
            self.hop_rtt.append(rtt)
        else:            
            if response_type == "Time exceeded" or response_type == "Echo reply":
                #calcular hop entre i y i-1
                current_hop_index = len(self.hop_list)-1#ultimo indice de la lista de hops
                nearest_hop_behind = self.calculate_nearest_hop_behind(current_hop_index)
                print "nearest hop behind " + self.hop_list[current_hop_index] + " is " + self.hop_list[nearest_hop_behind]
                calculated_rtt=self.hop_rtt_acum[current_hop_index]-self.hop_rtt_acum[nearest_hop_behind]
                self.hop_rtt.append(calculated_rtt)
            else:
                self.hop_rtt.append(0)

    def display_trace(self):
        #imprimimos la lista de hops
        print ""
        print "----------------------------------------------------------------------"      
        print ""
        print "Traceroute a " + str(self.dst_host) + " (max " + str(self.max_hops) + " hops)"
        print "Hop#\tHop IP\t\tHop RTT Acumulado\tHop RTT Incremental\tHop Resp. Type"
        hop_index = 1
        for hop in self.hop_list:
            print str(hop_index) + "\t" + str(hop) + "\t" + str(self.hop_rtt_acum[hop_index-1]) + "\t\t\t" + str(self.hop_rtt[hop_index-1]) + "\t\t\t" + str(self.hop_response[hop_index-1])
            hop_index+=1