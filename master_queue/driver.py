from elevator_interface import ElevatorInterface
from panel_interface import PanelInterface
from constants import N_FLOORS, DIRN_STOP, DIRN_UP, DIRN_DOWN
from threading import Thread, Lock
import time
import pickle


class Driver:
	def __init__(self):
		self.__ElevatorInterface = ElevatorInterface()
		self.__PanelInterface = PanelInterface()
		self.__elevator_queue_key = Lock()
		self.__floor_panel_queue_key = Lock()
		self.__elevator_queue = [[0 for button in range(0,3)] for floor in range(0,N_FLOORS)]
		self.__floor_panel_queue = []
		self.__position = (0,0,"None")
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
		self.__startup()
		self.__load_elevator_queue()
		self.__thread_run_elevator.start()
		self.__thread_build_queues.start()
		self.__thread_set_indicators.start()


	def __startup(self):
		
		check_floor = self.__ElevatorInterface.get_floor_sensor_signal()
		turn_time = time.time() + 5
		reset_time = time.time() + 10

		while check_floor < 0:
			if turn_time > time.time():
				self.__ElevatorInterface.set_motor_direction(DIRN_UP)
				pass
			else:
				self.__ElevatorInterface.set_motor_direction(DIRN_DOWN)
				if reset_time < time.time():
					turn_time = time.time() + 5
					reset_time = time.time() + 10
			check_floor = self.__ElevatorInterface.get_floor_sensor_signal()

		self.__ElevatorInterface.set_motor_direction(DIRN_STOP)


	def __load_elevator_queue(self):
		queue_file = open("queue_file", "rb")
		self.__elevator_queue = pickle.load(queue_file)
		queue_file.close()


	def __run_elevator(self):

		last_floor = 0
		next_floor = 0
		direction = "None"

		while True:
			time.sleep(0.001)

			floor_max = 0
			floor_min = N_FLOORS-1

			for floor in range(0,N_FLOORS):
				for button in range(0,3):
					if self.__elevator_queue[floor][button] == 1:
						floor_max = max(floor_max,floor)
						floor_min = min(floor_min,floor)
						if (last_floor == next_floor) and (direction != "DOWN") and (next_floor < floor_max):
							next_floor = floor
						elif (last_floor == next_floor) and (direction != "UP") and (next_floor > floor_min):
							next_floor = floor
						elif (last_floor < next_floor) and (floor < next_floor) and (floor > last_floor) and (button != 1):
							next_floor = floor
						elif (last_floor > next_floor) and (floor > next_floor) and (floor < last_floor) and (button != 0):
							next_floor = floor

			if (direction == "UP") and (floor_max <= last_floor):
				direction = "None"
			elif (direction == "DOWN") and (floor_min >= last_floor):
				direction = "None"

			read_floor = self.__ElevatorInterface.get_floor_sensor_signal()
			if read_floor >= 0:
				last_floor = read_floor

			if last_floor == next_floor:
				self.__ElevatorInterface.set_motor_direction(DIRN_STOP)
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
				self.__ElevatorInterface.set_motor_direction(DIRN_UP)
				direction = "UP"
				self.__position = (last_floor,next_floor,direction)
			elif last_floor > next_floor:
				self.__ElevatorInterface.set_motor_direction(DIRN_DOWN)
				direction = "DOWN"
				self.__position = (last_floor,next_floor,direction)
			

	def __build_queues(self):
		while True:
			time.sleep(0.001)
			for floor in range (0,N_FLOORS):
				for button in range(0,3):
					if (floor == 0 and button == 1) or (floor == 3 and button == 0):
						pass
					elif self.__PanelInterface.get_button_signal(button,floor):
						if button == 2:	
							with self.__elevator_queue_key:
								self.__elevator_queue[floor][button]=1			
						elif (floor,button) not in self.__floor_panel_queue:
							with self.__floor_panel_queue_key:
								self.__floor_panel_queue.append((floor,button))


	def __set_indicators(self):

		saved_elevator_queue = [[0 for button in range(0,3)] for floor in range(0,N_FLOORS)]

		while True:
			time.sleep(0.001)
			
			if self.__elevator_queue != saved_elevator_queue:

				with self.__elevator_queue_key:
					queue_file = open("queue_file", "wb")
					pickle.dump(self.__elevator_queue, queue_file)
					queue_file.close()

				queue_file = open("queue_file", "rb")
				saved_elevator_queue = pickle.load(queue_file)
				queue_file.close()

				for floor in range(0,N_FLOORS):
						for button in range(0,3):
								if (floor == 0 and button == 1) or (floor == 3 and button == 0):
									pass
								elif saved_elevator_queue[floor][button] == 1:
									self.__PanelInterface.set_button_lamp(button,floor,1)
								else:
									self.__PanelInterface.set_button_lamp(button,floor,0)
			
			(last_floor, next_floor, direction) = self.__position
			
			if last_floor == next_floor:
				self.__PanelInterface.set_door_open_lamp(1)
			else:
				self.__PanelInterface.set_door_open_lamp(0)

			self.__PanelInterface.set_floor_indicator(last_floor)
