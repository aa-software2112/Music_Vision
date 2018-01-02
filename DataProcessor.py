import numpy as np


class DProcess(object):
	""" 
	This class takes the number of LEDS, and the size of the FFT output,
	and converts the FFT to 0-255 in order to provide color data for the LEDS.
	
	This class also maintains the previous data, the current data, and a history of the last N data
	for modes 1 and 2 to work properly
	"""
	
	def __init__(self, num_leds, data_size):
		
		# The number of LEDS 
		self.num_leds = num_leds
		 
		# Array of unsigned bytes 0 - 255, previous and current data
		self.prev = np.zeros([self.num_leds], dtype=np.uint8) 
		self.curr = np.zeros([self.num_leds], dtype=np.uint8) 
		
		# History array
		self.history = np.zeros([3, self.num_leds], dtype=np.uint8)
		self.history_weights = [ 0.1, 0.2, 0.7]
		
		self.mode_fns = {1:self._mode_1}
		
	def process(self, data, mode, serial):
		
		# Send data and queue to appropriate mode
		self.mode_fns[mode](data, serial)
		
	def _mode_1(self, data, serial):
		""" This mode sets the entire array to the average db level """
		# Store the current data in the previous one
		self.prev = self.curr
		
		# Overwrite current
		self.curr = data
		
		# Set the average
		self.curr[:] = int(np.sum(self.curr)/self.curr.shape[0])
		
		# Put a copy of the data in the queue
		serial.add_list(["d"] + [int(self.curr[0])])
		

if __name__ == "__main__":
	d = DProcess(144, 256)
	d.process([1,2,3], 1, None)
