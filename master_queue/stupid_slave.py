from elevator_driver import ElevatorDriver 
from message_handler import MessageHandler
from constants import SLAVE_TO_MASTER_PORT, MASTER_TO_SLAVE_PORT
import elevator
import time
import broadcast


def main():
	message_handler = MessageHandler()
	elevator_driver = ElevatorDriver()
	elevator_driver.start()
	old_message = 12345678
	master_queue = [0 for i in range(0,16)]
	old_master_queue = [0 for i in range(0,16)]
	my_id = 1

	
	while True:




		
		(master_floor, master_button) = elevator_driver.pop_button_queue()
		if (master_floor and master_button) is not None:
			message = "%i,%i" % (master_floor,master_button)
			if message != old_message:
				broadcast.send(message,SLAVE_TO_MASTER_PORT)
			time.sleep(0.001)
		
		message = message_handler.read_message(MASTER_TO_SLAVE_PORT)
		print message
		if message is not None:
			for i in range (0,4):
					for j in range(0,2):
						master_queue[(i*4)+2*j] = int(message[(i*4)+2*j])
						master_queue[(i*4)+2*j + 1] = int(message[(i*4)+2*j + 1])



		#if master_queue != old_master_queue:
		
		print master_queue
			


		#	elevator_driver.queue_floor_button_run(floor, button)
		#	old_master_queue = master_queue


		time.sleep(0.5)

		'''
		(floor, button) = message_handler.read_message(MASTER_TO_SLAVE_PORT)
		if (floor and button) is not None:
			floor = int(floor)
			button = int(button)
			elevator_driver.queue_floor_button_run(floor, button)
		'''

if __name__ == "__main__":
    main()