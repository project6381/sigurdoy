from driver import Driver 
from message_handler import MessageHandler
from constants import SLAVE_TO_MASTER_PORT, MASTER_TO_SLAVE_PORT
import elevator
import time



def main():
	message_handler = MessageHandler()
	driver = Driver()

	#my_id = get IP address on this computer
	my_id = 3
	acknowledge = 4
	run_floor = 0
	run_button = 0

	while True:
		
		

		(floor,button) = driver.pop_floor_panel_queue()

		master_message = message_handler.receive_from_master()
		#floor = master_message['floor']
		#button = master_message['button']
		#execute_queue = master_message['execute_queue']
		#queue_id = master_message['queue_id']


		message_handler.send_to_master(floor,button,my_id,master_message['queue_id'])


		for i in range (0,4):
			if master_message['floor'][i] == 1:
				run_floor = i
			if master_message['button'][i] == 1:
				run_button = i



		driver.queue_elevator_run(run_floor,run_button)	
		


		

		

		print ['floor:'] + master_message['master_queue_floor'] + ['button:'] + master_message['master_queue_button'] 

				


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