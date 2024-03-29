import cv2
import numpy as np
from time import sleep
import math
import threading
from Queue import Queue
from time import sleep
from time import time
from peakutils.peak import indexes
import peaks
import variance
import random

class VisualSimulation(object):
	
	""" Bin pixel dimensions"""
	BIN_WIDTH = 5
	BIN_HEIGHT = 60
	BIN_SPACING = 0
	
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
		
		self.prev_display = np.array([110 for x in range(bins)])
		
		self.curr_display = np.array([0 for x in range(bins)])
		
		self.largest_value = 1
		
		self.prev_data = np.array([0 for x in range(bins)])
		
		self.normalize = VisualSimulation.MAX_FRAME_HEIGHT - 10
		
		self.history = np.zeros([3, self.bins], dtype=np.int32)
		self.history_weights = [ 0.1, 0.2, 0.7]
		
		self.history_ptr = 0
		
	def _set_window(self):
		
		
		total_bin_width = (self.bins*VisualSimulation.BIN_WIDTH + (self.bins - 1)*(VisualSimulation.BIN_SPACING))
		
		rows_of_bins = int(math.ceil(float(total_bin_width)/(VisualSimulation.MAX_FRAME_WIDTH - 2*VisualSimulation.FRAME_BAR_THICKNESS)))
		
		self.rows_of_bins = rows_of_bins # Store for use later
		
		# Create a blank window
		self.frame = np.zeros((VisualSimulation.MAX_FRAME_HEIGHT,VisualSimulation.MAX_FRAME_WIDTH, 3), np.uint8)
		
	def _clear_window(self):
		
		self.frame[:] = 0
	
	def _db_to_color(self, db):
		
		# color format is BGR
		return (0, 255, 0)
		
		if db <= 15:
			return (0, 0, 255)
			
		if db <= 50:
			return (0, 255, 255)
		
		return (0, 255, 0)
		
	def _convert_db_to(self, data, mode=1, decrement_by=2):
		""" This function takes an array of decibel data and returns the output visualization based on the requested mode"""
		
		
		# Follow the average noise
		if mode == 1:
			
			data = np.array(data)
			
			avg_db = np.sum(data)/data.shape[0]
			
			self.curr_display[:] = avg_db
			
		
		# Regular db display mode
		elif mode == 2:	
		
			# Add data to the history, fill it first
			if self.history_ptr < self.history.shape[0]:
				
				self.history[self.history_ptr] = data
				self.history_ptr += 1
			
			# History is full, get average, roll, and add new data to it
			else:
				
				data = np.array(data)
				
				# Get average of the last N samples (before the current data)
				#avg_old = np.sum(self.history, axis=0)/self.history.shape[0] # Average array of size bins
				avg_old = np.zeros([self.history.shape[1], ])
				
				# Old Weighted Average
				for idx, row in enumerate(self.history):
					avg_old += row*self.history_weights[idx]
				
				# Get the boolean index of difference between the current data and the old average that meets threshold requirements
				difference = np.abs(np.subtract(data, avg_old)) > 30
				
				self.history = np.roll(self.history, self.history.shape[0]-1, axis=0) # Shift all data 
				
				# Insert new data 
				self.history[self.history_ptr - 1] = data
				
				#avg_new = np.sum(self.history, axis=0)/self.history.shape[0] # Average array of size bins
				avg_new = np.zeros([self.history.shape[1], ])
				
				# New Weighted Average
				for idx, row in enumerate(self.history):
					avg_new += row*self.history_weights[idx]
					
				data = avg_new
				self.curr_display[ difference ] = ( ((avg_new[difference])/float(100))*self.normalize ).astype(np.int32)
				self.curr_display[ ~difference ] = ( (avg_new[~difference]/float(100))*self.normalize).astype(np.int32)
				
				#self.curr_display = map(lambda db: ( int((float(db)/float(100))*(VisualSimulation.MAX_FRAME_HEIGHT - 10))), data)
				self.curr_display = np.array(self.curr_display)
				
				# Get average
				self.curr_display = peaks.peak_moving_average(self.curr_display, [1, 1, 1, 1])
				
				centile = np.percentile(self.curr_display, 65)
				# Damp and peak
				if centile > 0:
					# Damp
					self.curr_display[self.curr_display < centile] = self.curr_display[self.curr_display < centile] - decrement_by
					self.curr_display[self.curr_display < 0] = 0
					
					## Peak
					#self.curr_display[self.curr_display >= centile] = self.curr_display[self.curr_display >= centile] + 10
				
				#self.curr_display = peaks.OR_peaks(self.prev_display, self.curr_display, len(self.curr_display), decrement_by=decrement_by)
		
		# Using max and rebuilding exponential around it
		elif mode ==3:
			
			# Ignore the first value, which is the max of all signals
			max_idx = np.argmax(np.array(data[10:])) + 10
			max_height = data[max_idx]
			
			temp = np.zeros([data.shape[0],], dtype=np.uint8)
			
			# Center point
			max_idx = data.shape[0]/2
			temp[max_idx] = max_height
			
			# Exponential base, larger (quicker cutoff) when quiter, smaller (slower cutoff) when louder
			self.largest_value = max(self.largest_value, max_height)
			base = 1 + (float(self.largest_value - max_height)/self.largest_value)*0.25
			#base = 1.10
			
			# Remove negatives
			right_of_max = -1*np.power(base, [x - max_idx for x in range(max_idx+1, data.shape[0])]) + max_height
			right_of_max[right_of_max < 0] = 0
			
			temp[max_idx + 1:] = right_of_max
			
			left_of_max = -1*np.power(base, [-x + max_idx for x in range(0, max_idx)]) + max_height
			left_of_max[left_of_max <0 ] = 0
			
			temp[0 : max_idx] = left_of_max
			
			data = temp
			self.curr_display = data
		
	def _draw_bins(self, data):	
		
		decrement = (type(data) == type(None))
		
		if type(data) == type(None):
			#print "Data is None {}".format(data)
			data = self.prev_data[:]
		
		elif data[0] < -254:
			self._clear_window()
			self._display_window()
			return
		
		data = abs(np.array(data))
		
		# Remove high data
		data[ data > 100] = 100
			
		data = data[:self.bins]
		
		self.largest_value = max( max(data), self.largest_value)
		
		# Get the number of bins per row
		bins_per_row = int(math.ceil((VisualSimulation.MAX_FRAME_WIDTH - 2*VisualSimulation.FRAME_BAR_THICKNESS + VisualSimulation.BIN_SPACING)/(VisualSimulation.BIN_WIDTH + VisualSimulation.BIN_SPACING)))
	
		if bins_per_row > self.bins:
			bins_per_row = self.bins
	
		# Clear the previous plot
		self._clear_window()
		#self._display_window()
		
		px = py = 0 # Pixel pointers for x and y
		
		# Start at bottom
		py = VisualSimulation.MAX_FRAME_HEIGHT - VisualSimulation.FRAME_BAR_THICKNESS - VisualSimulation.BIN_HEIGHT
		
			#temp = self._convert_db_to(data, mode=4)
			
			#if not type(temp) == type(None):
				#data = temp
				
		self.normalize = 100
		
		#else:
		#if decrement:
			#self._convert_db_to(data, mode=2, decrement_by=0.25)
		#else:
		self._convert_db_to(data, mode=3, decrement_by=0.5)
			
		color_percent = map(lambda c: float(c)/100, self.curr_display) 
		
		# Uncomment sorting to have regular ascending frequency display
		#temp = sorted(self.curr_display)
		
		#right_idx = len(temp)/2
		#left_idx =  right_idx - 1
		#temp_idx = len(temp) - 1
		
		#while left_idx > -1:
			
			#self.curr_display[right_idx] = temp[temp_idx]
			#right_idx += 1
			#temp_idx -= 1
			
			#if temp_idx == -1:
				#break
			
			#self.curr_display[left_idx] = temp[temp_idx]
			#left_idx -= 1
			#temp_idx -= 1
		
		
		intensity_idx = 0
		
		# Each row
		for row in range(self.rows_of_bins):
			
			# Move to first bin
			px = VisualSimulation.FRAME_BAR_THICKNESS
			
			# Each bin per row
			for bn in range(bins_per_row):
					
				# Colored boxes
				cv2.rectangle(self.frame, (px, py), (px + VisualSimulation.BIN_WIDTH, py + VisualSimulation.BIN_HEIGHT),  (0, 255*(color_percent[intensity_idx]), 0),  thickness=-1)
				
				#cv2.rectangle(self.frame, (px, py), (px + VisualSimulation.BIN_WIDTH, py + VisualSimulation.BIN_HEIGHT),  intensity[intensity_idx],  thickness=-1)
				
				# vertical movement
				#cv2.rectangle(self.frame, (px, py-self.curr_display[intensity_idx]), (px + VisualSimulation.BIN_WIDTH, py),  (44,255,131),  thickness=1)
				
				intensity_idx += 1
				
				if intensity_idx >= len(self.curr_display):
					break
				
				px += VisualSimulation.BIN_WIDTH + VisualSimulation.BIN_SPACING
						
			# Move down one row
			py -= (VisualSimulation.BIN_HEIGHT + VisualSimulation.FRAME_BAR_THICKNESS/2)
			
		# Store the current frame as previous
		self.prev_display = self.curr_display[:]
		self.prev_data = data[:]
		

	def _display_thread(self):
		
		msg = None
		
		last_display_time = time()*1000
		
		# Display Interval (only update every few milliseconds)
		display_interval = -1
		
		while True:
			
				if not self.Q.empty():

					# Clear all due to delay
					while self.Q.qsize() > 1:
						#print self.Q.qsize()
						self.Q.get()
						
					#print self.Q.qsize()
					
					msg = self.Q.get()
					
					if type(msg) == type(""): # Is a string
						
						if msg == "DONE": # Song is done, terminate thread
							break
							
					else: # Is a row of bin data
						
						# Update every interval time
						if time()*1000 - last_display_time >= display_interval:
							self._draw_bins(msg) # Draw the data
							self._display_window()
							last_display_time = time()*1000
						## Lower the waves
						#else:
							#self._draw_bins(None) # Draw the data
							#self._display_window()
				# Is empty
				else:
					self._draw_bins(None) # Draw the data
					self._display_window()
				
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
