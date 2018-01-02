from pydub import AudioSegment
import glob
import math
import numpy as np
import matplotlib.pyplot as plt
from numpy import fft as fft
import threading
from time import sleep
from time import time
from Queue import Queue
import vlc
import sys


from VisualSimulation import VisualSimulation

AudioSegment.converter = "C:/ffmpeg/bin/ffmpeg.exe"

class Song(object):

	def __init__(self):
		
		self.song_path = None
			
		self.song_data = []
		
		self.left = 0
		self.right = 0
		
		self.sample_rate = 0
		
		self.fft_thread = None
		
		self.song_on = False
	
	def set_song_path(self, song_path):
		
		self.song_path = song_path
	
	def load(self):

		song_data = AudioSegment.from_mp3(self.song_path) # Get song data
		
		# Store left-side audio
		temp = song_data.split_to_mono() # Split into mono
		self.left = temp[0]
		#self.right = temp[1]
		
		self.sample_rate = song_data.frame_rate # Obtain Sample rate
		
		
	def display(self):
		
		print "Sample Rate {}Hz".format(self.sample_rate)
	
	def plot(self, seconds):
		
		time = np.arange(0, float(self.sample_rate*seconds), 1)/self.sample_rate

		# Plot requested seconds of data
		plt.plot(time[:self.sample_rate*seconds], self.left.get_array_of_samples()[:self.sample_rate*seconds] , linewidth=0.05)
		plt.show()
		
	def start_fft_thread(self, millis, serial_q):
		
		if self.song_path:
			
			self.fft_thread = threading.Thread(target=self._fft_thread, args=(millis, serial_q))
			self.fft_thread.daemon = True
			self.fft_thread.start()
	
	def song_is_playing(self):
		
		return self.fft_thread.is_alive()
	
	def _fft_thread(self, millis, serial_q):
	
		# Get the closest millisecond to millis that allows for power of two bin size
		fft_samples = self.sample_rate*(millis/1000.0) # Number of bins
		fft_samples = int( math.pow(2, math.ceil( math.log(fft_samples)/math.log(2) )) ) # Power of two bins
		
		# Start the visualization
		#serial_q = Queue()
	
		#viz = VisualSimulation(fft_samples/4, serial_q)
		
		#viz.start()
		
		# Calculate the new milliseconds
		millis = (fft_samples)*(1.0/self.sample_rate)*1000
		
		# Store all samples
		samples = self.left.get_array_of_samples()
		
		# Maximum samples
		max_samples = self.left.frame_count()
		
		# Start sample for the next fft
		start_sample = 0
		
		# For adjusting delay dynamically
		took_ms = 0
		
		# Thread sleep delay in milliseconds
		sleep_delay = 0
		
		# Start playing music
		s = vlc.MediaPlayer(self.song_path)
		
		while (start_sample + fft_samples) < max_samples:
		
			if not self.song_on:
				s.play()
				self.song_on = True
			
			# Song is ahead of data, push data forward
			if s.get_time() - (start_sample*1.0/self.sample_rate)*1000 > 15:
				took_ms = self._fft_helper(fft_samples, samples, start_sample, serial_q)
				
				start_sample += fft_samples
				
				continue
			else:
				took_ms = self._fft_helper(fft_samples, samples, start_sample, serial_q)
			
				sleep((millis - took_ms - sleep_delay)/1000.0)
				
			
			start_sample += fft_samples
		
			
		# Send done message to visualization
		#serial_q.put("DONE")
		s.stop()
		self.song_on = False
		
	
	def _fft_helper(self, bin_size, samples, from_samp, message_Q):
		
		# Calculate the fft for a given size
		t_in = time()*1000
		
		dout = ((np.fft.rfft(samples[from_samp:from_samp + bin_size + 1]) - 1e-10)  /bin_size)[1:]	
		dout = abs(dout)
		dout = 20*np.log10( dout)
		dout[dout < 0] = 0
		
		message_Q.put(  dout )
		
		return time()*1000 - t_in
		
	def fft(self):
		
		
		size = self.sample_rate
		
		bins = np.arange(0, 512) # This should be the number of LEDs*2
			
		F = np.fft.rfft(self.left.get_array_of_samples()[bins.shape[0]*110:bins.shape[0]*111])/bins.shape[0]
		#F = np.fft.rfft(self.left.get_array_of_samples()[bins.shape[0]*4:bins.shape[0]*5])
		
		print F.shape[0]
		 
		bin_multiplier = (size)/(bins.shape[0])
		
		plt.plot(bins[0:bins.shape[0]/2]*bin_multiplier, 20*np.log10(abs(F[1:])) )	
		#plt.scatter(bins[0:bins.shape[0]/2 + 1]*bin_multiplier,  abs(F))
	
		plt.show()
	
if __name__ == "__main__":
	
	song = Song()

	song.set_song_path(glob.glob("2 - Primus - The Seven.mp3")[0])
	
	song.load()
	
	song.start_fft_thread(10)
	
	while song.fft_thread.is_alive():
		#print "Alive"
		
		sleep(5)
	
	#song.display()
	#song.plot(5)
	#song.fft()
	
	
