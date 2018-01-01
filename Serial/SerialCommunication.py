from serial.tools import list_ports
import sys
import os
import Queue
import threading
from time import sleep

def list_to_string(lst):
	
	return ",".join([str(x) for x in lst]) + "$"
	
class InvalidSerial(Exception):
	pass

class Serial(object):
	""" 
	This is a threaded serial class, which sends and receives data in "parallel" with
	any running process
	"""


	def __init__(self, msg_format_fn, port=None, baud=115200, timeout=1, write_timeout=1):
		
		self.baud = baud
		self.port = None
		
		self._set_port(port)
		
		# Boolean that can be controlled externally to end the thread
		self.end_thread = False
		
		# Will store the outbound messages
		self.outbound = Queue.Queue()
		
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
		
		self.outbound.put(self.format_fn(lst))
		
	def _serial_thread(self):
		""" This is the main thread that excutes the send and receives """	
		
		while not self.end_thread:
			
			sleep(3)
			print "Thread"
	
	def start_serial_thread(self):
		""" This starts the actual thread """
		
		t = threading.Thread(target=self._serial_thread)
		t.daemon = True
		t.start()
		
		
if __name__ == "__main__":
	s =Serial(list_to_string, port='COM3')
	s.start_serial_thread()
			
			
