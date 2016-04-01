from message_handler import MessageHandler
from constants import SLAVE_TO_MASTER_PORT, MASTER_TO_SLAVE_PORT, DIRN_DOWN, DIRN_UP, DIRN_STOP
import time


def main():
	message_handler = MessageHandler()
	queue_id = 1


	active_slaves = 1
	acknowledges = 0
	execute_queue = 0
	arivied = 0
	acknowledged_queue_id = []

	last_direction = 0

	executer_id = [0]*8
	while True:
		


		slave_message = message_handler.receive_from_slave()
		print ['floor_up:'] + slave_message['slave_floor_up'] + ['floor_down:'] + slave_message['slave_floor_down'] 
		print queue_id

		#if slave_message['direction'] is not DIRN_STOP:
		last_direction = slave_message['direction']



		if slave_message['last_floor'] == slave_message['next_floor']:
			arrived = slave_message['last_floor']	
			if (last_direction == DIRN_UP) or (last_direction == DIRN_STOP):
				slave_message['slave_floor_up'][arrived] = 0
			if (last_direction == DIRN_DOWN) or (last_direction == DIRN_STOP):
				slave_message['slave_floor_down'][arrived] = 0
		

		#if queue_id == int(slave_message['queue_id']): 
		#	acknowledges += 1
		#	print '111111111111111111111111111111111111111111111111111111111'

		#if acknowledges == active_slaves:
		#	execute_queue = 1
		#	print '12222222222222222222222222222222222222222222222222222'
		#	message_handler.send_to_slave(slave_message['slave_floor_up'],slave_message['slave_floor_down'],executer_id,execute_queue,queue_id)
		#	execute_queue = 0
		#	acknowledges = 0
		#	queue_id += 1
		#else: 
		#	message_handler.send_to_slave(slave_message['slave_floor_up'],slave_message['slave_floor_down'],executer_id,execute_queue,queue_id)
		
		message_handler.send_to_slave(slave_message['slave_floor_up'],slave_message['slave_floor_down'],executer_id,execute_queue,queue_id)
		
		time.sleep(0.1)


if __name__ == "__main__":
    main()