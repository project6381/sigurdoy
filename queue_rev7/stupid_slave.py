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
	while True:

		(master_floor, master_button) = elevator_driver.pop_button_queue()
		if (master_floor and master_button) is not None:
			message = "%i,%i" % (master_floor,master_button)
			if message != old_message:
				broadcast.send(message,SLAVE_TO_MASTER_PORT)
			time.sleep(0.001)

		(floor, button) = message_handler.read_message(MASTER_TO_SLAVE_PORT)
		if (floor and button) is not None:
			floor = int(floor)
			button = int(button)
			elevator_driver.queue_floor_button_run(floor, button)


if __name__ == "__main__":
    main()