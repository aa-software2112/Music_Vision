import math
import matplotlib.pyplot as plt
import numpy as np

def filter_by_bool(old_value, new_value, include):
	
	if include:
		return new_value
	return old_value - 1

def expand_peaks(p_ind, arr_size, data, log_factor=1.25):
	"""Expands peaks by decreasing around them logarithmically in the array"""
	
	# No peaks to process
	if len(p_ind) == 0:
		return map(lambda a: int(a), data)
		
	epeaks = [0 for x in range(arr_size)] # Expanded peaks
	i = p_ind[0] # Index for general use
	
	# Expand leftward from first peak to start of list
	epeaks[i] = data[i]
	i -= 1

	while i >= 0:
		
		epeaks[i] = epeaks[i+1]/log_factor
		i -= 1
		
	i = 0
	
	# Expand between subsequent peaks
	while i <= len(p_ind) - 2:
		p1 = p_ind[i]
		p2 = p_ind[i+1]
		ptr = p1
		epeaks[ptr] = data[ptr]
		next_peak = epeaks[ptr]/log_factor
		ptr += 1
		
		# Go from p1 to p2 until p1 reaches a height of <= 1 OR reaches p2
		while ptr < p2 and next_peak > 1:
			epeaks[ptr] = next_peak
			next_peak/=log_factor
			ptr += 1
			
		# Go from p2 to p1 until p2 reaches a height <= epeaks[ptr] OR reaches p1
		ptr = p2
		epeaks[ptr] = data[ptr]
		next_peak = epeaks[ptr]/log_factor
		ptr -= 1
		
		while ptr > p1 and next_peak > epeaks[ptr]:
			epeaks[ptr] = next_peak
			next_peak/=log_factor
			ptr -= 1 
		
		i+=1
		
	# Go from last peak to the end of the array
	i = p_ind[-1]
	epeaks[i] = data[i]
	i+=1
	
	while i < arr_size:
		epeaks[i] = epeaks[i -1]/log_factor
		i += 1
		
	return map(lambda a: int(a), epeaks)
	
	
def OR_peaks(old, new, size, decrement_by=1):
	""" The function returns the ORing of the peaks max(old - 1, new),
	given that if an old peak is > a new peak, the output is old peak - decrement_by,
	otherwise it is the new peak"""
	
	#print type(old)
	#print type(list(new))
	
	#print len(old)
	#print len(new)
	return np.array(map(lambda o, n: int(max((o - decrement_by), n)), old, list(new)))
	
def peak_energy(peaks, size, largest_value):
	""" Returns a peak energy from 0 ->1.0, inclusive """
	
	total_energy = largest_value*size
	
	# Sum all values in list
	actual_energy = reduce(lambda a, b: a + b, peaks)
	
	return float(actual_energy)/total_energy
	
def peak_diff(old, new):
	""" This returns the difference new db - old db to get the decibel attack"""
	return  map(lambda o, n: max(n - o, 0), old, new)
	
		
def peak_moving_average(data, weights):
	
	# Preserve the data lost in the convolution
	lost = data[ len(data) - len(weights) + 1: len(data)]
	
	weights = np.flip(np.array(weights), 0)

	conv = np.convolve(data, weights, mode='valid')
	
	return np.append(np.divide(conv, np.sum(weights)), lost).astype(dtype=np.int32)
		
if __name__ == "__main__":
	#d = [5,25,50,70]
	#arr_size = 144
	#data = [0 for x in range(arr_size)]
	
	## The peak decibel levels
	#data[5] = 50
	#data[25] = 90
	#data[50] = 20
	#data[70] = 100
	
	#expand_peaks(d, arr_size, data, log_factor=1.15)
	
	print OR_peaks([1,2,3,4], [5,6,7, 1], 4, 1)
	
