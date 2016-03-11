from message_handler import MessageHandler
from constants import SLAVE_TO_MASTER_PORT, MASTER_TO_SLAVE_PORT
import time


def main():
	message_handler = MessageHandler()

	while True:
		
		master_queue = message_handler.receive_queue_from_slave()

		message_handler.send_queue_to_slave(master_queue,MASTER_TO_SLAVE_PORT)
		time.sleep(0.1)
		print master_queue
		

if __name__ == "__main__":
    main()