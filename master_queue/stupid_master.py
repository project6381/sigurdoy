from message_handler import MessageHandler
from constants import SLAVE_TO_MASTER_PORT, MASTER_TO_SLAVE_PORT
import time


def main():
	message_handler = MessageHandler()
	queue_id = 1
	while True:
		
		slave_message = message_handler.receive_from_slave()


		master_queue = slave_message[0:-1]
		slave_id = slave_message[16]
		
		

		message_handler.send_to_slave(master_queue,queue_id)
		time.sleep(0.1)



if __name__ == "__main__":
    main()