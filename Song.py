from pydub import AudioSegment
import glob
import math
import numpy as np
import matplotlib.pyplot as plt
from numpy import fft as fft

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
		
	def fft(self):
		
		size = self.sample_rate
		
		bins = np.arange(0, 256) # This should be the number of LEDs
		
		F = np.fft.rfft(self.left.get_array_of_samples()[bins.shape[0]*5:bins.shape[0]*6])/bins.shape[0]
		
		bin_multiplier = (size)/(bins.shape[0])
		
		plt.scatter(bins[0:bins.shape[0]/2 + 1]*bin_multiplier, 10*np.log(F))
	
		plt.show()
	
if __name__ == "__main__":
	
	song = Song(glob.glob("1kHz_44100Hz_16bit_30sec.mp3")[0])
	song.load()
	
	song.set_properties()
	song.display()
	#song.plot(5)
	song.fft()
	
	