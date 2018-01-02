from serial.tools import list_ports
import serial
import sys
import os
import Queue
import threading
from time import sleep
import time

def list_to_bytes(lst):
	
	return bytearray( lst )
	
class InvalidSerial(Exception):
	pass

class Serial(object):
	""" 
	This is a threaded serial class, which sends and receives data in "parallel" with
	any running process
	"""

	HANDSHAKE_CHAR = chr(254)
	
	def __init__(self, msg_format_fn, port=None, baud=115200, timeout=1, write_timeout=1, serial_q=None):
		
		self.baud = baud
		self.port = None
		
		self._set_port(port)
		
		# Open serial port
		try:
			self.serial = serial.Serial(port=self.port, baudrate=self.baud, timeout=timeout, write_timeout=write_timeout)
			sleep(3)
		except (ValueError, serial.SerialException) as err:
			print err
			sys.exit(0)
			
		# Boolean that can be controlled externally to end the thread
		self.end_thread = False
		
		# Will store the outbound messages
		self.outbound = serial_q if serial_q else Queue.Queue() 
		
		# Message Formatter function pointer
		self.format_fn = msg_format_fn
		
	def _set_port(self, port):
		""" Set the port """
		# Get all possible serial ports on OS
		ports = list_ports.comports()
				
		# No ports available
		if len(ports) == 0:
			print "No ports available... Exiting"
			sys.exit(0)
		
		# Port is invalid
		if not port:
			
			choice = -1
			choice_made = False
			
			# Display possible ports for user to choose from
			while not choice_made:
				
				if os.name == 'nt':
					os.system('cls')
				elif os.name == 'posix':
					os.system('clear')
					
				print "q + enter to quit"
				
				for idx, port in enumerate(ports):
					print "[{}] {}".format(idx+1, port)
				
				choice = raw_input("Select a port --> ")
					
				# User wants to quit
				if choice == 'q':
					sys.exit(0)
				
				try:
					
					# Check if user selected a valid port
					choice = int(choice) - 1
					ports[choice]
					choice_made = True
					
				except:
					print "Invalid choice, try again"
			
			self.port = ports[choice].device.encode('ascii', 'ignore')
			
			return
		
		# port is possibly valid
		elif port:
			
			# Check if the port is valid among the available options
			if port in [p.device.encode('ascii', 'ignore') for p in ports]:
				self.port = port
				
			else:
				raise InvalidSerial("Invalid Serial Port @ {}".format(port))
				
	def add_list(self, lst):
		""" 
		This function takes a list, converts it to a string of elements separated 
		by the delimeter specified in the format function, and ends with a closing 
		byte also specified by the format function
		""" 
		
		self.outbound.put(lst)
		
	def _serial_thread(self):
		""" This is the main thread that excutes the send and receives """	
		count = 1
		
		self.serial.flushInput()
		
		t_in = time.time()*1000
		
		# Ends when external module sets end_thread to true
		while not self.end_thread:
			
			# Waits until there is data in the queue, assumes it is a list of integers
			if self.outbound.qsize() > 0:
				
				# Format the integers as bytes (they will be between 0 and 255)
				out = self.format_fn(self.outbound.get())
				#print out
				res = self.serial.write( out )
				
				self._handshake()
			
		print "Took {} ms".format(time.time()*1000 - t_in)
			
	def _handshake(self):
		""" This function waits for the handshake """
		
		val = '0'
		string = ""
		
		# Keep reading until the handshake is read
		while not val == Serial.HANDSHAKE_CHAR:
			
			val = self.serial.read(size=1)
			string += val
			
			
		print string
		
	def start_serial_thread(self):
		""" This starts the actual thread """
		
		t = threading.Thread(target=self._serial_thread)
		t.daemon = True
		t.start()
		
		
if __name__ == "__main__":
	s =Serial(list_to_bytes, port='COM3')
	s.start_serial_thread()
			
	while True:
		
		# Change mode
		s.add_list( ["m", 2])
		
		# Tell Arduino to take in data
		# Send the data to take in 
		s.add_list( ["d"] + [x for x in range(144)] )
		
		sleep(0.25)
			
