from socket import *
from threading import Thread, Lock
import time 
import broadcast 
from constants import MASTER_TO_SLAVE_PORT, SLAVE_TO_MASTER_PORT
from socket import *
import random 

class MessageHandler:
	def __init__(self):
		self.__receive_buffer_slave = [] 
		self.__receive_buffer_master = [] 
		self.__receive_buffer_slave_key = Lock()
		self.__receive_buffer_master_key = Lock()
		self.__master_thread_started = False
		self.__slave_thread_started = False
		self.__master_message = [0 for i in range(0,17)]
		self.__slave_message = [0 for i in range(0,17)]
		self.__thread_buffering_master = Thread(target = self.__buffering_master_messages, args = (),)
		self.__thread_buffering_slave = Thread(target = self.__buffering_slave_messages, args = (),)


	def receive_from_slave(self):				
		message = self.__read_message(SLAVE_TO_MASTER_PORT)
		
		if message is not None:
			floor = int(message[0])
			button = int(message[1])
			slave_id = int(message[2:])
			self.__master_message[(floor*4)+2*button] = 1
			self.__master_message[(floor*4)+2*button + 1] = random.randint(1,3)
			self.__master_message[16] = slave_id				
		return self.__master_message


	def send_to_slave(self,master_queue,queue_id):

		message = str()
		queue_id = str(queue_id)
		
		for i in range(0,len(master_queue)):
			message += str(master_queue[i])	


		message += queue_id
		print message
		self.__send(message,MASTER_TO_SLAVE_PORT)
		time.sleep(0.1)



	def receive_from_master(self):
		
		message = self.__read_message(MASTER_TO_SLAVE_PORT)

		if message is not None:
			for i in range (0,4):
					for j in range(0,2):
						self.__slave_message[(i*4)+2*j] = int(message[(i*4)+2*j])
						self.__slave_message[(i*4)+2*j + 1] = int(message[(i*4)+2*j + 1])

		
		return self.__slave_message

	def send_to_master(self,floor,button,slave_id):
		if (floor and button) is not None:
			message = "%i%i%i" % (floor,button,slave_id)
			self.__send(message,SLAVE_TO_MASTER_PORT)


	def __send(self, data, port):
		send = ('<broadcast>', port)
		udp = socket(AF_INET, SOCK_DGRAM)
		udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		message='<%s;%s>' % (str(len(data)), data)
		udp.sendto(message, send)
		udp.close()


	def __read_message(self,port):

		# Check if master or slave thread is already running 
		if port == MASTER_TO_SLAVE_PORT:
			if self.__slave_thread_started is not True:
				self.__start(self.__thread_buffering_slave)
			
			if self.__receive_buffer_slave: 
				with self.__receive_buffer_slave_key:
					return self.__receive_buffer_slave.pop(0)
			else:
				return None

		if port == SLAVE_TO_MASTER_PORT: 
			if self.__master_thread_started is not True:
				self.__start(self.__thread_buffering_master)
			
			if self.__receive_buffer_master: 
				with self.__receive_buffer_master_key:
					return self.__receive_buffer_master.pop(0)
			else:
				return None	




	def __start(self,thread):
			thread.daemon = True # Terminate thread when "main" is finished
			thread.start()

	
	def __buffering_master_messages(self):

		last_master_queue = 'This message will never be heard'
		self.__master_thread_started = True

		port = ('', SLAVE_TO_MASTER_PORT)
		udp = socket(AF_INET, SOCK_DGRAM)
		udp.bind(port)
		udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

		while True:
			data, address = udp.recvfrom(1024)
			master_queue = self.__errorcheck(data)
			if master_queue != last_master_queue:
				if master_queue is not None:
					with self.__receive_buffer_master_key:
						self.__receive_buffer_master.append(master_queue)	
				last_master_queue = master_queue


	def __buffering_slave_messages(self):

		last_message = 'This message will never be heard'
		self.__slave_thread_started = True

		port = ('', MASTER_TO_SLAVE_PORT)
		udp = socket(AF_INET, SOCK_DGRAM)
		udp.bind(port)
		udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
	
		while True:
			data, address = udp.recvfrom(1024)
			message = self.__errorcheck(data)
			if message != last_message:
				if message is not None:
					with self.__receive_buffer_slave_key:
						self.__receive_buffer_slave.append(message)		
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
