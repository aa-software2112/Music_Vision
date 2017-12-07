import cv2
import numpy as np
from time import sleep
import math
import threading
from Queue import Queue
from time import time

class VisualSimulation(object):
	
	""" Bin pixel dimensions"""
	BIN_WIDTH = 3
	BIN_HEIGHT = 20 
	BIN_SPACING = 3
	
	""" Image Thresholds """
	MAX_FRAME_WIDTH = 1700
	MAX_FRAME_HEIGHT = 200
	
	""" Frame thickness """
	FRAME_BAR_THICKNESS = 15
	
	

	def __init__(self, bins, message_Q=None):
	
		self.bins = bins
		
		self.Q = message_Q # Contains the messages from the song
		
		self.frame= None
		
		self.rows_of_bins = 0
		
	def _set_window(self):
		
		
		total_bin_width = (self.bins*VisualSimulation.BIN_WIDTH + (self.bins - 1)*(VisualSimulation.BIN_SPACING))
		rows_of_bins = int(math.ceil(float(total_bin_width)/(VisualSimulation.MAX_FRAME_WIDTH - 2*VisualSimulation.FRAME_BAR_THICKNESS)))
		
		#height = rows_of_bins*VisualSimulation.BIN_HEIGHT + (rows_of_bins - 1)*VisualSimulation.FRAME_BAR_THICKNESS/2 + 2*VisualSimulation.FRAME_BAR_THICKNESS
		
		self.rows_of_bins = rows_of_bins # Store for use later
		
		# Create a blank window
		self.frame = np.zeros((VisualSimulation.MAX_FRAME_HEIGHT,VisualSimulation.MAX_FRAME_WIDTH), np.uint8)
		
	def _clear_window(self):
		
		self.frame[:] = 0
		
	def _draw_bins(self, data):	
	
		bins_per_row = int(math.ceil((VisualSimulation.MAX_FRAME_WIDTH - 2*VisualSimulation.FRAME_BAR_THICKNESS + VisualSimulation.BIN_SPACING)/(VisualSimulation.BIN_WIDTH + VisualSimulation.BIN_SPACING)))
	
		if bins_per_row > 256:
			bins_per_row = 256
	
		# Clear the previous plot
		self._clear_window()
	
		px = py = 0 # Pixel pointers for x and y
		
		# Start at bottom
		py = VisualSimulation.MAX_FRAME_HEIGHT - VisualSimulation.FRAME_BAR_THICKNESS
		
		# intensity = []
		heights = []
		
		# Ceiling data to 100
		if not type(data) == type(None):
			data[data > 100] = 100 
		
			#intensity = list(map(lambda db: int( (db/100.0)*255), data))
			heights = list(map(lambda db: int( (db/100.0)*(VisualSimulation.MAX_FRAME_HEIGHT - 20)), data))
		else:
			
			#intensity = [255 for x in range(256)]
			heights = [VisualSimulation.MAX_FRAME_HEIGHT - 20 for x in range(256)]
		
		#print heights[:10]
		#print "Rows {}".format(self.rows_of_bins)
		#print "Bins Per Row {}".format(bins_per_row)
		
		intensity_idx = 0
		
		# Each row
		for row in range(self.rows_of_bins):
			
			# Move to first bin
			px = VisualSimulation.FRAME_BAR_THICKNESS
			
			# Each bin per row
			for bn in range(bins_per_row):
					
				#cv2.rectangle(self.frame, (px, py), (px + VisualSimulation.BIN_WIDTH, py + VisualSimulation.BIN_HEIGHT),  intensity[intensity_idx],  thickness=-1)
				cv2.rectangle(self.frame, (px, py-heights[intensity_idx]), (px + VisualSimulation.BIN_WIDTH, py),  255,  thickness=1)
				
				intensity_idx += 1
				
				if intensity_idx >= len(heights):
					break
				
				px += VisualSimulation.BIN_WIDTH + VisualSimulation.BIN_SPACING
						
			# Move down one row
			py -= (VisualSimulation.BIN_HEIGHT + VisualSimulation.FRAME_BAR_THICKNESS/2)

	def _display_thread(self):
		
		msg = None
		
		last_display_time = int(time()*1000)
		
		# Display Interval (only update every few milliseconds)
		display_interval = -1
		
		while True:
			
				if not self.Q.empty():
					
					if self.Q.qsize() > 1:
						print self.Q.qsize()
					
					msg = self.Q.get()
					
					if type(msg) == type(""): # Is a string
						
						if msg == "DONE": # Song is done, terminate thread
							break
					else: # Is a row of bin data
						
						if int(time()*1000) - last_display_time >= display_interval:
							self._draw_bins(msg) # Draw the data
							self._display_window()
							last_display_time = int(time()*1000)
						
				if cv2.waitKey(1) == ord('q'):
					break
				
	
	def _display_window(self):
		
		cv2.imshow('LED Visualization', self.frame)

	def start(self):
		self._set_window()
		
		# Start the display thread
		dt = threading.Thread(target=self._display_thread)
		dt.daemon = True
		dt.start()
		
		#self._draw_bins(None)
		#self._display_window()
		
		# If user quits the window, quit the current thread
		
		#while not cv2.waitKey(0) == ord('q'):
					#pass
		
		
if __name__ == "__main__":
	v = VisualSimulation(256, Queue())
	v.start()
