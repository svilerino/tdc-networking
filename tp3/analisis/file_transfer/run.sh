#!/bin/bash
delay_values=( 0 0.25 0.5 0.75 )
prob_error_values=(0 0.25 0.50 0.75 1)
alpha_values=(0 0.25 0.50 0.75 1)
beta_values=(0 0.25 0.50 0.75 1)

for delay_var in "${delay_values[@]}"
do
   for prob_error_var in "${prob_error_values[@]}"
	do
		for alpha_var in "${alpha_values[@]}"
		do
			for beta_var in "${beta_values[@]}"
			do
			   #sudo python client "$IP_DST" "$PORT_DST" "$delay_var" "$prob_error_var" "$alpha_var" "$beta_var"
			   echo "$IP_DST" "$PORT_DST" "$delay_var" "$prob_error_var" "$alpha_var" "$beta_var"
			done
		done   
	done
done