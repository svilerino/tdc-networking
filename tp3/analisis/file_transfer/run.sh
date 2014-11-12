#!/bin/bash
IP_DST="127.0.0.1"
PORT_DST="6677"

#delay_values=(0 0.25 0.5 0.75)
#prob_error_values=(0 0.25 0.50 0.75 1)
#alpha_values=(0 0.25 0.50 0.75 1)
#beta_values=(0 0.25 0.50 0.75 1)
delay_values=(0 0.25 0.5 0.75)
prob_error_values=(0)
alpha_values=(0.25)
beta_values=(0.25)

for delay_var in "${delay_values[@]}"
do
   for prob_error_var in "${prob_error_values[@]}"
	do
		for alpha_var in "${alpha_values[@]}"
		do
			for beta_var in "${beta_values[@]}"
			do
			   	echo "Parametros de Experimentacion: $IP_DST" "$PORT_DST" "$delay_var" "$prob_error_var" "$alpha_var" "$beta_var"
				echo -n "Lanzando server en background..."
				(sudo python server.py &)
				echo "Ok!"
				echo -n "Esperando que el servidor escuche..."
				sleep 2
				echo "Ok!"
				echo -n "Lanzando cliente..."
			   	sudo python client.py "$IP_DST" "$PORT_DST" "$delay_var" "$prob_error_var" "$alpha_var" "$beta_var" > "$IP_DST"."$PORT_DST"."$delay_var"."$prob_error_var"."$alpha_var"."$beta_var"."txt"
			   	echo "Ok!"
			   	echo -n "Matando python..."
			   	sudo killall python
			   	echo "Ok!"
			   	echo "---------------------------------------------------------------------------------------------"
			   	echo ""
			done
		done   
	done
done