from elevator_driver import ElevatorDriver 
from message_handler import MessageHandler
from constants import SLAVE_TO_MASTER_PORT, MASTER_TO_SLAVE_PORT
import elevator
import time
import broadcast
import random 

def main():
	message_handler = MessageHandler()
	old_message = "this message will never be sent"
	master_queue = [0 for i in range(0,16)]

	while True:
		


		message = message_handler.read_message(SLAVE_TO_MASTER_PORT)
		
	
		if message is not None:
			floor = message[0]
			button = message[2]

		#if (floor and button) is not None:
			
			floor = int(floor)
			button = int(button)
			for i in range (0,4):
				for j in range(0,2):
					if (floor == i) and (button == j): 
						master_queue[(i*4)+2*j] = 1
						master_queue[(i*4)+2*j + 1] = random.randint(1,3)
						
		print master_queue
		
		message = str()

		for i in range(0,len(master_queue)):
			message += str(master_queue[i])

		broadcast.send(message,MASTER_TO_SLAVE_PORT)
		time.sleep(0.1)
		'''
		message = "%s,%s" % (floor,button) 
		if message != old_message:
			pass
			#broadcast.send(message,MASTER_TO_SLAVE_PORT)
		'''
if __name__ == "__main__":
    main()