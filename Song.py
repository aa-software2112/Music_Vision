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
		
		self.fft_thread = threading.Thread(target=self._fft_thread, args=(millis, ))
		self.fft_thread.daemon = True
		self.fft_thread.start()
		
	def _fft_thread(self, millis):
	
		# Get the closest millisecond to millis that allows for power of two bin size
		fft_samples = self.sample_rate*(millis/1000.0) # Number of bins
		fft_samples = int( math.pow(2, math.ceil( math.log(fft_samples)/math.log(2) )) )# Power of two bins
		
		# Start the visualization
		message_Q = Queue()
	
		viz = VisualSimulation(fft_samples/4, message_Q)
		
		viz.start()
		
		
		# Calculate the new milliseconds
		millis = (fft_samples)*(1.0/self.sample_rate)*1000
		
		# Store all samples
		samples = self.left.get_array_of_samples()
		
		# Maximum samples
		max_samples = self.left.frame_count()
		
		# Start sample for the next fft
		start_sample = 0
		
		# Start time of thread
		in_thread = time()
		took_ms = 0
		
		# Last sent
		last_send_time  = time()*1000
		
		# Thread sleep delay in milliseconds
		sleep_delay = 0
		
		# Start playing music
		s = vlc.MediaPlayer(self.song_path)
		
		song_on = False
		
		while (start_sample + fft_samples) < max_samples:
		
			took_ms = self._fft_helper(fft_samples, samples, start_sample, message_Q)
			
			if not song_on:
				s.play()
				song_on = True
				
			if s.get_time() - (start_sample*1.0/self.sample_rate)*1000 > 2:
				pass
				#print "Song Diff wrt Audio {}ms".format(s.get_time() - (start_sample*1.0/self.sample_rate)*1000)
			else:
				sleep((millis - took_ms - sleep_delay)/1000.0)
			
			start_sample += fft_samples
		
			
		# Send done message to visualization
		message_Q.put("DONE")
		s.stop()
		
		print "Took a total of {} seconds".format(int(time() - in_thread))
			
	
	def _fft_helper(self, bin_size, samples, from_samp, message_Q):
		
		# Calculate the fft for a given size
		t_in = time()*1000
		
		message_Q.put(  20*np.log10( abs((   (np.fft.rfft(samples[from_samp:from_samp + bin_size + 1]) - 1e-10)  /bin_size)[1:]) ) )
		
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
	
	song = Song(glob.glob("01 - Prison Song.mp3")[0])
	
	
	song.load()
	
	song.set_properties()
	
	song.start_fft_thread(10)
	
	while song.fft_thread.is_alive():
		#print "Alive"
		
		sleep(5)
	
	#song.display()
	#song.plot(5)
	#song.fft()
	
	
