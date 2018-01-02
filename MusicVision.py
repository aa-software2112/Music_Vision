from Song import Song
import Queue
from time import sleep
import glob
from DataProcessor import DProcess
from Serial.SerialCommunication import *

class MusicVision(object):
	""" This class controls the master logic for MusicVision, 
	everything from the song, to FFT, to processing the FFT, and finally 
	to sending data over serial """
	
	FFT_INTERVAL = 10 # Milliseconds interval for FFT
	LEDS = 144 # The number of LEDs
	
	def __init__(self):
		# Initialize Song object
		self.song = Song()
		
		# Queue for storing data to be processed
		self.process_q = Queue.Queue()
		
		# Serial Queue for message trading
		self.serial_q = Queue.Queue()
		
		# Serial communication object
		self.serial = None
		
		# Mode for MusicVision
		self.mode = 1
		
		# Keeps track of processing
		self.processing = False
		
	def open_song(self, path):
		""" This sets the song to be played next and loads its data """
		self.song.set_song_path(path) 
		self.song.load()
		
	def play(self):
		""" This starts playing the song AND begins FFT """
		
		# Start the serial object
		self.serial = Serial(list_to_bytes, port='COM3', serial_q=self.serial_q)
		self.serial.start_serial_thread()
	
		# Set the mode
		self._set_mode(self.mode)
	
		# Start the song + FFT (FFT output is stored in serial_q). This is non-blocking (threaded)
		self.song.start_fft_thread(MusicVision.FFT_INTERVAL, self.process_q)
		
		self.processing = True
		
		# Go and process incoming FFT data
		self._processor()
		
		self.processing = False
		
	def song_in_progress(self):
		return self.processing
		
	def _set_mode(self, mode):
		""" Sends the mode to serial """
		
		self.serial.add_list(["m", mode])
				
	def _processor(self):
		""" This waits for FFT data from the song and process it when available """
		
		# Initialize processor object.
		
		# Wait for song to start
		while not self.song.song_is_playing():
			sleep(0.05)
			
		#Wait for first FFT to be inserted into queue
		while self.process_q.qsize() == 0:
			sleep(0.05)
		
		# Grab the first data and get its size	
		proc = DProcess(144, self.process_q.get().shape[0])
		
		# While the song thread is alive, process available data...
		while self.song.song_is_playing():
			
			# Process any available data and add it to the serial object
			if self.process_q.qsize() > 0:
				proc.process(self.process_q.get(), 1, self.serial)
				
		print "Song is done"
		
		self.serial.shutdown()
		
		print "Serial shutdown"
		
		
		
if __name__ == "__main__":
	m = MusicVision()
	m.open_song(glob.glob("100Hz_44100Hz_16bit_05sec.mp3")[0])
	m.play()
	
	while m.song_in_progress():
		sleep(3)
		
	print "Exiting..."
