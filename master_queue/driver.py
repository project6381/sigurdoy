from elevator_interface import ElevatorInterface
from panel_interface import PanelInterface
from constants import N_FLOORS, DIRN_STOP, DIRN_UP, DIRN_DOWN
from threading import Thread, Lock
import time
import pickle
import sys


class Driver:
	def __init__(self):
		self.__elevator_interface = ElevatorInterface()
		self.__panel_interface = PanelInterface()
		self.__elevator_queue_key = Lock()
		self.__floor_panel_queue_key = Lock()
		self.__elevator_queue = [[0 for button in range(0,3)] for floor in range(0,N_FLOORS)]
		self.__floor_panel_queue = []
		self.__position = (0,0,"None")
		self.__stop = False
		self.__thread_run_elevator = Thread(target = self.__run_elevator, args = (),)
		self.__thread_build_queues = Thread(target = self.__build_queues, args = (),)
		self.__thread_set_indicators = Thread(target = self.__set_indicators, args = (),)
		self.__start()


	def queue_elevator_run(self,floor,button):
		with self.__elevator_queue_key:
			self.__elevator_queue[floor][button]=1


	def pop_floor_panel_queue(self):
		with self.__floor_panel_queue_key:
			if self.__floor_panel_queue:
				return self.__floor_panel_queue.pop(0)
			else:
				return (None, None)


	def read_position(self):
		return self.__position

	def stop(self):
		self.__stop = True

	def __start(self):
		self.__startup()
		self.__load_elevator_queue()
		self.__thread_run_elevator.daemon = True
		self.__thread_run_elevator.start()
		self.__thread_build_queues.daemon = True
		self.__thread_build_queues.start()
		self.__thread_set_indicators.daemon = True
		self.__thread_set_indicators.start()

	def __startup(self):
		
		check_floor = self.__elevator_interface.get_floor_sensor_signal()
		turn_time = time.time() + 5
		reset_time = time.time() + 10

		while check_floor < 0:
			if turn_time > time.time():
				self.__elevator_interface.set_motor_direction(DIRN_DOWN)
				pass
			else:
				self.__elevator_interface.set_motor_direction(DIRN_UP)
				if reset_time < time.time():
					turn_time = time.time() + 5
					reset_time = time.time() + 10
			check_floor = self.__elevator_interface.get_floor_sensor_signal()

		self.__elevator_interface.set_motor_direction(DIRN_STOP)


	def __load_elevator_queue(self):
		try:
			queue_file = open("queue_file_1", "rb")
			self.__elevator_queue = pickle.load(queue_file)
			queue_file.close()
		except:
			try:
				queue_file = open("queue_file_2", "rb")
				self.__elevator_queue = pickle.load(queue_file)
				queue_file.close()
			except:
				pass


	def __run_elevator(self):

		last_floor = 0
		next_floor = 0
		next_button = 0
		direction = "None"

		while (self.__stop != True):
			time.sleep(0.01)

			floor_max = 0
			floor_min = N_FLOORS-1

			with self.__elevator_queue_key:
				for floor in range(0,N_FLOORS):
					for button in range(0,3):
							if self.__elevator_queue[floor][button] == 1:
								floor_max = max(floor_max,floor)
								floor_min = min(floor_min,floor)
								if (last_floor == next_floor) and (direction != "DOWN") and (next_floor <= floor_max):
									next_floor = floor
									next_button = button
								elif (last_floor == next_floor) and (direction != "UP") and (next_floor >= floor_min):
									next_floor = floor
									next_button = button
								elif (last_floor > next_floor) and (floor > next_floor) and (floor < last_floor) and (button != 0):
									next_floor = floor
									next_button = button
								elif (last_floor < next_floor) and (floor < next_floor) and (floor > last_floor) and (button != 1):
									next_floor = floor
									next_button = button
			
			if (direction == "DOWN") and (floor_min < N_FLOORS-1) and (next_button == 0):
				next_floor = floor_min
			elif (direction == "UP") and (floor_max > 0) and (next_button == 1):
				next_floor = floor_max

			read_floor = self.__elevator_interface.get_floor_sensor_signal()
			if read_floor >= 0:
				last_floor = read_floor

			if (direction == "UP") and (floor_max <= last_floor):
				direction = "None"
			elif (direction == "DOWN") and (floor_min >= last_floor):
				direction = "None"

			if last_floor == next_floor:
				self.__elevator_interface.set_motor_direction(DIRN_STOP)
				if direction == "None":
					with self.__elevator_queue_key:
						self.__elevator_queue[next_floor][0] = 0
						self.__elevator_queue[next_floor][1] = 0
						self.__elevator_queue[next_floor][2] = 0
				elif direction == "UP":
					with self.__elevator_queue_key:
						self.__elevator_queue[next_floor][0] = 0
						self.__elevator_queue[next_floor][2] = 0
				elif direction == "DOWN":
					with self.__elevator_queue_key:
						self.__elevator_queue[next_floor][1] = 0
						self.__elevator_queue[next_floor][2] = 0
				self.__position = (last_floor,next_floor,direction)
				time.sleep(1)
			elif last_floor < next_floor:
				self.__elevator_interface.set_motor_direction(DIRN_UP)
				direction = "UP"
				self.__position = (last_floor,next_floor,direction)
			elif last_floor > next_floor:
				self.__elevator_interface.set_motor_direction(DIRN_DOWN)
				direction = "DOWN"
				self.__position = (last_floor,next_floor,direction)
			

	def __build_queues(self):
		while (self.__stop != True):
			time.sleep(0.01)
			for floor in range (0,N_FLOORS):
				for button in range(0,3):
					if (floor == 0 and button == 1) or (floor == 3 and button == 0):
						pass
					elif self.__panel_interface.get_button_signal(button,floor):
						if button == 2:	
							with self.__elevator_queue_key:
								self.__elevator_queue[floor][button]=1
						elif (floor,button) not in self.__floor_panel_queue:
							with self.__floor_panel_queue_key:
								self.__floor_panel_queue.append((floor,button))


	def __set_indicators(self):

		saved_elevator_queue = [[0 for button in range(0,3)] for floor in range(0,N_FLOORS)]

		while (self.__stop != True):
			time.sleep(0.01)
			
			with self.__elevator_queue_key:
				if self.__elevator_queue != saved_elevator_queue:
					queue_file = open("queue_file_1", "wb")
					pickle.dump(self.__elevator_queue, queue_file)
					queue_file.close()

					queue_file = open("queue_file_2", "wb")
					pickle.dump(self.__elevator_queue, queue_file)
					queue_file.close()

					try:
						queue_file = open("queue_file_1", "rb")
						saved_elevator_queue = pickle.load(queue_file)
						queue_file.close()
						if saved_elevator_queue != self.__elevator_queue:
							raise
					except:
						queue_file = open("queue_file_2", "rb")
						saved_elevator_queue = pickle.load(queue_file)
						queue_file.close()


					for floor in range(0,N_FLOORS):
							for button in range(0,3):
									if (floor == 0 and button == 1) or (floor == 3 and button == 0):
										pass
									elif saved_elevator_queue[floor][button] == 1:
										self.__panel_interface.set_button_lamp(button,floor,1)
									else:
										self.__panel_interface.set_button_lamp(button,floor,0)
			
			(last_floor, next_floor, direction) = self.__position
			
			if last_floor == next_floor:
				self.__panel_interface.set_door_open_lamp(1)
			else:
				self.__panel_interface.set_door_open_lamp(0)

			self.__panel_interface.set_floor_indicator(last_floor)
