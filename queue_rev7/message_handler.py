from socket import *
from threading import Thread, Lock
import time 
import broadcast 
from constants import MASTER_TO_SLAVE_PORT, SLAVE_TO_MASTER_PORT


class MessageHandler:
	def __init__(self):
		self.message_list = [] 
		self.message_list_key = Lock()
		self.master_thread_started = False
		self.slave_thread_started = False
		self.polling_master = Thread(target = self.polling_master_messages, args = (),)
		self.polling_slave = Thread(target = self.polling_slave_messages, args = (),)

	def read_message(self,port):

		# Check if master or slave thread is already running 
		if port == MASTER_TO_SLAVE_PORT:
			if self.master_thread_started is not True:
				self.start(self.polling_master)

		if port == SLAVE_TO_MASTER_PORT: 
			if self.slave_thread_started is not True:
				self.start(self.polling_slave)	

		if self.message_list: 
			self.message_list_key.acquire()
			first_element = self.message_list.pop(0)
			self.message_list_key.release()
			return first_element
		else:
			#pass
			return (None,None)


	def start(self,thread):
			thread.daemon = True # Terminate thread when "main" is finished
			thread.start()
			#thread.join()




	def polling_master_messages(self):

		old_message = 'denne beskjeden vil aldri bli hort'
		self.master_thread_started = True

		# Setup udp
		port = ('', MASTER_TO_SLAVE_PORT)
		udp = socket(AF_INET, SOCK_DGRAM)
		udp.bind(port)
		udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

		
		# Fetching data
		while True:
			data, address = udp.recvfrom(1024)
			message = broadcast.errorcheck(data)
			if message != old_message:
				if message is not None:
					floor = message[0]
					button = message[2]
					with self.message_list_key:
						self.message_list.append((floor,button))
				#print (self.message_list)		
				old_message = message
		#udp.close() 


	def polling_slave_messages(self):

		old_message = 'denne beskjeden vil aldri bli hort'
		self.slave_thread_started = True

		# Setup udp
		port = ('', SLAVE_TO_MASTER_PORT)
		udp = socket(AF_INET, SOCK_DGRAM)
		udp.bind(port)
		udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

		
		# Fetching data
		while True:
			data, address = udp.recvfrom(1024)
			message = broadcast.errorcheck(data)
			if message != old_message:
				if message is not None:
					floor = message[0]
					button = message[2]
					with self.message_list_key:
						self.message_list.append((floor,button))
				#print (self.message_list)		
				old_message = message
		#udp.close() 




