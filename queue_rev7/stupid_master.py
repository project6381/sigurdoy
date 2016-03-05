from elevator_driver import ElevatorDriver 
from message_handler import MessageHandler
from constants import SLAVE_TO_MASTER_PORT, MASTER_TO_SLAVE_PORT
import elevator
import time
import broadcast

def main():
	message_handler = MessageHandler()
	old_message = "this message will never be sent"
	while True:
		(floor,button) = message_handler.read_message(SLAVE_TO_MASTER_PORT)

		time.sleep(0.01) 
		'''
		Do some massive shit and calculations

		'''

		if (floor and button) is not None:
			message = "%s,%s" % (floor,button) 
			if message != old_message:
				broadcast.send(message,MASTER_TO_SLAVE_PORT)

if __name__ == "__main__":
    main()