from elevator_interface import ElevatorInterface
from panel_interface import PanelInterface
from constants import N_FLOORS, DIRN_STOP, DIRN_UP, DIRN_DOWN, BUTTON_CALL_UP, BUTTON_CALL_DOWN
from threading import Thread, Lock
from thread import interrupt_main
import time
import pickle


class Driver:
	def __init__(self):
		self.__elevator_interface = ElevatorInterface()
		self.__panel_interface = PanelInterface()
		self.__elevator_queue_key = Lock()
		self.__floor_panel_queue_key = Lock()
		self.__elevator_queue = [[0 for button in range(0,3)] for floor in range(0,N_FLOORS)]
		self.__floor_panel_queue = []
		self.__position = (0,0,DIRN_STOP)
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


	def __start(self):
		try:
			self.__startup()
			self.__load_elevator_queue()
			self.__thread_run_elevator.daemon = True
			self.__thread_run_elevator.start()
			self.__thread_build_queues.daemon = True
			self.__thread_build_queues.start()
			self.__thread_set_indicators.daemon = True
			self.__thread_set_indicators.start()
		except StandardError as error:
			print error
			print "Driver.__start"
			interrupt_main()

	def __startup(self):
		try:
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

		except StandardError as error:
			print error
			print "Driver.__startup"
			interrupt_main()


	def __load_elevator_queue(self):
		try:
			with open("queue_file_1", "rb") as queue_file:
				self.__elevator_queue = pickle.load(queue_file)
		except StandardError as error:
			print error
			print "Driver.__load_elevator_queue"
			try:
				with open("queue_file_2", "rb") as queue_file:
					self.__elevator_queue = pickle.load(queue_file)
			except StandardError as error:
				print error
				print "Driver.__load_elevator_queue"


	def __run_elevator(self):
		try:

			last_floor = 0
			next_floor = 0
			next_button = 0
			direction = DIRN_STOP

			while True:
				time.sleep(0.01)

				floor_max = 0
				floor_min = N_FLOORS-1

				with self.__elevator_queue_key:
					for floor in range(0,N_FLOORS):
						for button in range(0,3):
								if self.__elevator_queue[floor][button] == 1:
									floor_max = max(floor_max,floor)
									floor_min = min(floor_min,floor)
									if (last_floor == next_floor) and (direction != DIRN_DOWN) and (next_floor <= floor_max):
										next_floor = floor
										next_button = button
									elif (last_floor == next_floor) and (direction != DIRN_UP) and (next_floor >= floor_min):
										next_floor = floor
										next_button = button
									elif (last_floor < next_floor) and (floor < next_floor) and (floor > last_floor) and (button != BUTTON_CALL_DOWN):
										next_floor = floor
										next_button = button
									elif (last_floor > next_floor) and (floor > next_floor) and (floor < last_floor) and (button != BUTTON_CALL_UP):
										next_floor = floor
										next_button = button
				
				if (direction == DIRN_UP) and (floor_max > 0) and (next_button == BUTTON_CALL_DOWN):
					next_floor = floor_max
				elif (direction == DIRN_DOWN) and (floor_min < N_FLOORS-1) and (next_button == BUTTON_CALL_UP):
					next_floor = floor_min

				read_floor = self.__elevator_interface.get_floor_sensor_signal()
				if read_floor >= 0:
					last_floor = read_floor

				if (direction == DIRN_UP) and (floor_max <= last_floor):
					direction = DIRN_STOP
				elif (direction == DIRN_DOWN) and (floor_min >= last_floor):
					direction = DIRN_STOP

				if last_floor == next_floor:
					self.__elevator_interface.set_motor_direction(DIRN_STOP)
					if direction == DIRN_STOP:
						with self.__elevator_queue_key:
							self.__elevator_queue[next_floor][0] = 0
							self.__elevator_queue[next_floor][1] = 0
							self.__elevator_queue[next_floor][2] = 0
					elif direction == DIRN_UP:
						with self.__elevator_queue_key:
							self.__elevator_queue[next_floor][0] = 0
							self.__elevator_queue[next_floor][2] = 0
					elif direction == DIRN_DOWN:
						with self.__elevator_queue_key:
							self.__elevator_queue[next_floor][1] = 0
							self.__elevator_queue[next_floor][2] = 0
					self.__position = (last_floor,next_floor,direction)
					time.sleep(1)
				elif last_floor < next_floor:
					self.__elevator_interface.set_motor_direction(DIRN_UP)
					direction = DIRN_UP
					self.__position = (last_floor,next_floor,direction)
				elif last_floor > next_floor:
					self.__elevator_interface.set_motor_direction(DIRN_DOWN)
					direction = DIRN_DOWN
					self.__position = (last_floor,next_floor,direction)

		except StandardError as error:
			print error
			print "Driver.__run_elevator"
			interrupt_main()
			

	def __build_queues(self):
		try:

			while True:
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

		except StandardError as error:
			print error
			print "Driver.__build_queues"
			interrupt_main()


	def __set_indicators(self):
		try:

			saved_elevator_queue = [[0 for button in range(0,3)] for floor in range(0,N_FLOORS)]

			while True:
				time.sleep(0.01)
				
				with self.__elevator_queue_key:
					if self.__elevator_queue != saved_elevator_queue:
						with open("queue_file_1", "wb") as queue_file:
							pickle.dump(self.__elevator_queue, queue_file)

						with open("queue_file_2", "wb") as queue_file: 
							pickle.dump(self.__elevator_queue, queue_file)

						try:
							with open("queue_file_1", "rb") as queue_file:
								saved_elevator_queue = pickle.load(queue_file)
							assert saved_elevator_queue == self.__elevator_queue, "unknown error loading queue_file_1"
						except StandardError as error:
							print error
							with open("queue_file_2", "rb") as queue_file: 
								saved_elevator_queue = pickle.load(queue_file)
							assert saved_elevator_queue == self.__elevator_queue, "unknown error loading queue_file_2"

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

		except StandardError as error:
			print error
			print "Driver.__set_indicators"
			interrupt_main()

