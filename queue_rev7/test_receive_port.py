from elevator_driver import ElevatorDriver 
from message_handler import MessageHandler 
import elevator
import time
import broadcast
from constants import SLAVE_TO_MASTER_PORT, MASTER_TO_SLAVE_PORT
	

def main():

	message_handler1 = MessageHandler()
	message_handler1.read_message(SLAVE_PORT)
	time.sleep(1)
	broadcast.send('hei, dette er heis1',SLAVE_PORT)
	broadcast.send('heis1 er sulten',SLAVE_PORT)
	time.sleep(1)
	print message_handler1.read_message(SLAVE_PORT)
	print message_handler1.read_message(SLAVE_PORT)


if __name__ == "__main__":
    main()