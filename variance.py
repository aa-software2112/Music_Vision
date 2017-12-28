import numpy as np
import math

def filter_by_variance(data, window_size=4, var_thresh=10):
	""" Removes values BELOW a certain variance (when data is too stable), this way the "action" is caught"""
	
	intervals = int( math.floor(  len(data)/window_size ) )
	
	j = 0
		
	for i in xrange(intervals):
		 
		 var = np.var(data[i*window_size:(i+1)*window_size])
		 
		 # Steady db
		 if var > var_thresh:
			 
			 j = i*window_size
			 
			 while j < (i+1)*window_size:
				 
				 data[j] = 0
				 
				 j += 1
		
	# Finish remaining data
	var = np.var(data[intervals*window_size: -1])
			 
	 # Steady db
	if var > var_thresh:
		 
		j = intervals*window_size

		while j < (intervals+1)*window_size:
		 
			data[j] = 0

			j += 1
		 
	return data
		 
	
