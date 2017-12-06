from pydub import AudioSegment
import glob
import math
import numpy as np
import matplotlib.pyplot as plt
from numpy import fft as fft
import threading
from time import sleep
from time import time

AudioSegment.converter = "C:/ffmpeg/bin/ffmpeg.exe"

class Song(object):

	def __init__(self, song_path):
		
		self.song_path = song_path
		
		self.song_data = []
		
		self.left = 0
		self.right = 0
		
		self.fft_length = 256
		
		self.sample_rate = 0
		
		self.total_samples = 0
		
		self.num_fft = 0
		
		self.fft_thread = None
	
	def load(self):

		self.song_data = AudioSegment.from_mp3(self.song_path)
		temp = self.song_data.split_to_mono()
		self.left = temp[0]
		#self.right = temp[1]
	
	def set_properties(self):
		
		self.sample_rate = self.song_data.frame_rate
		self.total_samples = self.song_data.frame_count()
		self.num_fft = (self.total_samples / self.fft_length) - 2
		
	def display(self):
		
		print "Sample Rate {}Hz".format(self.sample_rate)
		print "Total Samples {}".format(self.total_samples)
		print "Total Seconds {}".format(self.total_samples/self.sample_rate)
	
	def plot(self, seconds):
		
		time = np.arange(0, float(self.sample_rate*seconds), 1)/self.sample_rate

		# Plot requested seconds of data
		plt.plot(time[:self.sample_rate*seconds], self.left.get_array_of_samples()[:self.sample_rate*seconds] , linewidth=0.05)
		plt.show()
		
	def start_fft_thread(self, millis):
		
		self.fft_thread = threading.Thread(target=self._fft_thread, args=(millis,))
		self.fft_thread.daemon = True
		self.fft_thread.start()
		
	def _fft_thread(self, millis):
	
		# Get the closest millisecond to millis that allows for power of two bin size
		fft_samples = self.sample_rate*(millis/1000.0) # Number of bins
		fft_samples = int( math.pow(2, math.ceil( math.log(fft_samples)/math.log(2) )) )# Power of two bins
		
		# Calculate the new milliseconds
		millis = int((fft_samples)*(1.0/self.sample_rate)*1000)
		
		# Store all samples
		samples = self.left.get_array_of_samples()
		
		# Maximum samples
		max_samples = self.left.frame_count()
		
		# Start sample for the next fft
		start_sample = 0
		
		# Start time of thread
		in_thread = time()
		
		# Sleep time in
		in_sleep = 0
		
		# Thread sleep delay in milliseconds
		sleep_delay = 0
		
		while (start_sample + fft_samples) < max_samples:
		
			took_ms = self._fft_helper(fft_samples, samples, start_sample)
			
			start_sample += fft_samples
			
			sleep((millis - took_ms - sleep_delay)/1000.0)
			
		print "Took a total of {} seconds".format(int(time() - in_thread))
			
	
	def _fft_helper(self, bin_size, samples, from_samp):
		
		# Calculate the fft for a given size
		t_in = time()
		
		F = np.fft.rfft(samples[from_samp:from_samp + bin_size + 1])/bin_size
		
		return int( math.ceil((time() - t_in)*1000) )
		
	def fft(self):
		
		size = self.sample_rate
		
		bins = np.arange(0, 256) # This should be the number of LEDs
		
		F = np.fft.rfft(self.left.get_array_of_samples()[bins.shape[0]*5:bins.shape[0]*6])/bins.shape[0]
		
		bin_multiplier = (size)/(bins.shape[0])
		
		plt.scatter(bins[0:bins.shape[0]/2 + 1]*bin_multiplier, 10*np.log(F))
	
		plt.show()
	
if __name__ == "__main__":
	
	song = Song(glob.glob("flock-of-seagulls_daniel-simion.mp3")[0])
	
	song.load()
	
	song.set_properties()
	
	song.start_fft_thread(10)
	
	while song.fft_thread.is_alive():
		print "Alive"
		sleep(5)
	
	#song.display()
	#song.plot(5)
	#song.fft()
	
	