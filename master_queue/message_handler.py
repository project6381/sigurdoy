from socket import *
from threading import Thread, Lock
import time 
import broadcast 
from constants import MASTER_TO_SLAVE_PORT, SLAVE_TO_MASTER_PORT, MASTER_TO_MASTER_PORT, N_ELEVATORS
from socket import *
import random 


class MessageHandler:

	def __init__(self):
		self.__receive_buffer_slave = [] 
		self.__receive_buffer_master = [] 
		self.__active_masters = [0]*N_ELEVATORS
		#self.__receive_buffer_master_alive = [] 		
		self.__receive_buffer_slave_key = Lock()
		self.__receive_buffer_master_key = Lock()
		#self.__receive_buffer_master_alive_key = Lock()
		self.__active_masters_key = Lock()
		self.__master_thread_started = False
		self.__slave_thread_started = False
		self.__master_alive_thread_started = False
		

		self.__slave_message = {'slave_floor_up': [0]*4,
								'slave_floor_down': [0]*4,
								'slave_id': 0,
								'last_floor': 0,
								'next_floor': 0,
								'direction': 0,
								'queue_id': 0}

		self.__master_message = {'master_floor_up': [0]*4,
								'master_floor_down': [0]*4,
								'executer_id': [0]*8,
								'floor':[],
								'button':[],
								'execute_queue': 0,
								'queue_id': 0}
		self.__last_master_floor_up = [0]*4
		self.__last_master_floor_down = [0]*4

		
		self.__slave_queue_id = 0

		self.__thread_buffering_master = Thread(target = self.__buffering_master_messages, args = (),)
		self.__thread_buffering_slave = Thread(target = self.__buffering_slave_messages, args = (),)
		self.__thread_buffering_master_alive = Thread(target = self.__buffering_master_alive_messages, args = (),)
	

	def send_to_master(self,slave_floor_up,slave_floor_down,slave_id,last_floor,next_floor,direction,queue_id):
		
		floor_up = str()
		floor_down = str()

		for i in range(0,len(slave_floor_up)):
			floor_up += str(slave_floor_up[i])

		for i in range(0,len(slave_floor_down)):
			floor_down += str(slave_floor_down[i])

		message = "%s%s%i%i%i%i%i" % (floor_up,floor_down,slave_id,last_floor,next_floor,direction,queue_id)
		self.__send(message,SLAVE_TO_MASTER_PORT)


	def send_to_slave(self,master_floor_up,master_floor_down,executer_id,execute_queue,queue_id):

		message = str()

		execute_queue = str(execute_queue)
		queue_id = str(queue_id)
		
		for i in range(0,len(master_floor_up)):
			message += str(master_floor_up[i])

		for i in range(0,len(master_floor_down)):
			message += str(master_floor_down[i])	


		for i in range(0,len(executer_id)):
			message += str(executer_id[i])


		message += execute_queue
		message += queue_id
		
		for _ in range(0,3):
			self.__send(message,MASTER_TO_SLAVE_PORT)
			time.sleep(0.001)


	def receive_from_master(self):
		
		message = self.__read_message(MASTER_TO_SLAVE_PORT)

		if message is not None:

			for i in range (0,4):
				self.__master_message['master_floor_up'][i] = int(message[i])
				self.__master_message['master_floor_down'][i] = int(message[4+i]) 
			
			for i in range (0,8):
				self.__master_message['executer_id'][i] = int(message[8+i])
			
			self.__master_message['queue_id'] = int(message[17])
			


			for i in range (0,4):
				if self.__last_master_floor_up[i] != self.__master_message['master_floor_up'][i]: # and id == my_id
					if self.__master_message['master_floor_up'][i] == 1:
						self.__master_message['floor'].append(i) 
						self.__master_message['button'].append(0)
					self.__last_master_floor_up[i] = self.__master_message['master_floor_up'][i]
				
				if self.__last_master_floor_down[i] != self.__master_message['master_floor_down'][i]:
					if self.__master_message['master_floor_down'][i] == 1:					
						self.__master_message['floor'].append(i) 
						self.__master_message['button'].append(1)
					self.__last_master_floor_down[i] = self.__master_message['master_floor_down'][i]


			self.__master_message['execute_queue'] = int(message[16])
			self.__master_message['queue_id'] = int(message[17:])
			
		
		return self.__master_message


	def receive_from_slave(self):				
		message = self.__read_message(SLAVE_TO_MASTER_PORT)
		
		if message is not None:

			for i in range (0,4):
					self.__slave_message['slave_floor_up'][i] = int(message[i])
					self.__slave_message['slave_floor_down'][i] = int(message[4+i]) 	

			self.__slave_message['slave_id'] = int(message[8])
			self.__slave_message['last_floor'] = int(message[9])
			self.__slave_message['next_floor'] = int(message[10])
			self.__slave_message['direction'] = int(message[11])
			self.__slave_message['queue_id'] = int(message[12:])

		return self.__slave_message


	def get_my_master_order(self):
		

		print self.__master_message['floor']
		print self.__master_message['button']
		if self.__master_message['floor'] and self.__master_message['button']:
			return (self.__master_message['floor'].pop(0),self.__master_message['button'].pop(0))

		else: 
			return (None,None)


	def update_master_alive(self, elevator_id):
		self.__send(str(elevator_id),MASTER_TO_MASTER_PORT)

		print self.__active_masters

	def check_master_alive(self):	

		if self.__master_alive_thread_started is not True:
			self.__start(self.__thread_buffering_master_alive)

		for i in range(0,N_ELEVATORS):
			if self.__active_masters[i] == 1:
				return i+1
		return -1 



	def __send(self, data, port):
		send = ('<broadcast>', port)
		udp = socket(AF_INET, SOCK_DGRAM)
		udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
		message='<%s;%s>' % (str(len(data)), data)
		udp.sendto(message, send)
		udp.close()


	def __read_message(self,port):

		# Check if buffering messages threads is already running 
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

		last_message = 'This message will never be heard'
		self.__master_thread_started = True

		port = ('', SLAVE_TO_MASTER_PORT)
		udp = socket(AF_INET, SOCK_DGRAM)
		udp.bind(port)
		udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

		while True:
			data, address = udp.recvfrom(1024)
			message = self.__errorcheck(data)
			if message != last_message:
				if message is not None:
					with self.__receive_buffer_master_key:
						self.__receive_buffer_master.append(message)	
				last_message = message

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

	def __buffering_master_alive_messages(self):

		last_message = 'This message will never be heard'
		self.__master_alive_thread_started = True

		port = ('', MASTER_TO_MASTER_PORT)
		udp = socket(AF_INET, SOCK_DGRAM)
		udp.bind(port)
		udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

		downtime = [time.time() + 3]*N_ELEVATORS
		 

		while True:
			data, address = udp.recvfrom(1024)
			message = self.__errorcheck(data)
			if message is not None:
				with self.__active_masters_key:
					self.__active_masters[int(message)-1] = 1		
					downtime[int(message)-1] = time.time() + 3
			
			
			for i in range(0,N_ELEVATORS):
				if downtime[i] < time.time():
					self.__active_masters[i] = 0





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
