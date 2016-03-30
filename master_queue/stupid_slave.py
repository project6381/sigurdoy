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

	floor_up = [0]*4
	floor_down = [0]*4

	while True:
		
		
		position = driver.read_position()

		(floor,button) = driver.pop_floor_panel_queue()

		if button == 0:
			floor_up[floor] = 1
		elif button == 1: 
			floor_down[floor] = 1 	
	

		master_message = message_handler.receive_from_master()	
		message_handler.send_to_master(floor_up,floor_down,my_id,position[0],position[1],position[2],master_message['queue_id'])





		(run_floor,run_button) = message_handler.get_my_master_order()
		
		

		if run_floor is not None:
			driver.queue_elevator_run(run_floor,run_button)	
		


		
		
		

		print ['floor_up:'] + master_message['master_floor_up'] + ['floor_down:'] + master_message['master_floor_down'] 
		print master_message['queue_id']
				


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