#import panel
from class_panel import Panel
import elevator
import time


def main():
	#floorDestination = int(raw_input("->"))

	

	kok = Panel()
	while True:
		print kok.read_pressed_button()	
		time.sleep(3)
	

	print 'lala'
	#goFloor = 1
	#while True:

#		nextFloor = panel.read_buttons()
#		if nextFloor >= 0:
#			goFloor = nextFloor
#						
#		elevator.go_to_floor(nextFloor)





if __name__ == "__main__":
    main()
