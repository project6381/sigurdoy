from socket import *
from threading import Thread, Lock
import time 
import broadcast 
from constants import MASTER_TO_SLAVE_PORT, SLAVE_TO_MASTER_PORT
from socket import *

class MessageHandler:
	def __init__(self):
		self.__message_list = [] 
		self.__message_list_key = Lock()
		self.__master_thread_started = False
		self.__slave_thread_started = False
		self.__polling_master = Thread(target = self.__polling_master_messages, args = (),)
		self.__polling_slave = Thread(target = self.__polling_slave_messages, args = (),)


	def send(self, data, port):
		send = ('<broadcast>', port)
		udp = socket(AF_INET, SOCK_DGRAM)
		udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		message='<%s;%s>' % (str(len(data)), data)
		udp.sendto(message, send)
		udp.close()


	def read_message(self,port):

		# Check if master or slave thread is already running 
		if port == MASTER_TO_SLAVE_PORT:
			if self.__master_thread_started is not True:
				self.__start(self.__polling_master)

		if port == SLAVE_TO_MASTER_PORT: 
			if self.__slave_thread_started is not True:
				self.__start(self.__polling_slave)	

		if self.__message_list: 
			with self.__message_list_key:
				first_element = self.__message_list.pop(0)
			return first_element
		else:
			return None


	def __start(self,thread):
			thread.daemon = True # Terminate thread when "main" is finished
			thread.start()

	
	def __polling_master_messages(self):

		last_master_queue = 'denne beskjeden vil aldri bli hort'
		self.__master_thread_started = True

		port = ('', MASTER_TO_SLAVE_PORT)
		udp = socket(AF_INET, SOCK_DGRAM)
		udp.bind(port)
		udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

		while True:
			data, address = udp.recvfrom(1024)
			master_queue = self.__errorcheck(data)
			if master_queue != last_master_queue:
				if master_queue is not None:
					with self.__message_list_key:
						self.__message_list.append(master_queue)	
				last_master_queue = master_queue


	def __polling_slave_messages(self):

		last_message = 'denne beskjeden vil aldri bli hort'
		self.__slave_thread_started = True

		port = ('', SLAVE_TO_MASTER_PORT)
		udp = socket(AF_INET, SOCK_DGRAM)
		udp.bind(port)
		udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
	
		while True:
			data, address = udp.recvfrom(1024)
			message = self.__errorcheck(data)
			if message != last_message:
				if message is not None:
					with self.__message_list_key:
						self.__message_list.append(message)		
				last_message = message


	def __errorcheck(self,data):
		if data[0]=='<' and data[len(data)-1]=='>':

			counter=1
			separator=False
			separator_pos=0
			for char in data:
				if char == ";" and separator==False:
					separator_pos=counter
					separator=True
				counter+=1

			message_length=str(len(data)-separator_pos-1)
			test_length=str()
			for n in range(1,separator_pos-1):
				test_length+=data[n]

			if test_length==message_length and separator==True:
				message=str()
				for n in range(separator_pos,len(data)-1):
					message+=data[n]
				return message
			else:
				return None
		else:
			return None