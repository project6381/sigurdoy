from class_panel import Panel
from class_message_handler import MessageHandler 
import elevator
import time
import broadcast

def main():
	#floorDestination = int(raw_input("->"))

	panel1 = Panel()
	message_handler1 = MessageHandler()
	order_list = []

	panel1.read_button()
	message_handler1.read_message()

	time.sleep(1)


	broadcast.send('hei, dette er heis1')
	broadcast.send('heis1 er sulten')

	

	time.sleep(1)
	Pukk = 1
	while Pukk < 100:
		message = message_handler1.read_message()
		button = panel1.read_button()
		if message is not None:
			order_list.append(message)
		if button is not None:
			order_list.append(button)
			broadcast.send(button)
		Pukk += 1



	
	print order_list	
	#time.sleep(10)

if __name__ == "__main__":
    main()
