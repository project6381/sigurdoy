from driver import Driver 
from elevator_driver import ElevatorDriver 
from message_handler import MessageHandler
from constants import SLAVE_TO_MASTER_PORT, MASTER_TO_SLAVE_PORT
import elevator
import time



def main():
	message_handler = MessageHandler()
	driver = Driver()

	
	while True:
		
		

		(floor, button) = driver.pop_floor_panel_queue()

		message_handler.send_floor_panel_to_master(floor,button,SLAVE_TO_MASTER_PORT)

			
		


		master_queue = message_handler.receive_queue_from_master()

		print master_queue
		


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