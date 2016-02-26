import panel_driver
from threading import Thread
from threading import Lock
import time

button_list = []
mutex_key = Lock()	
thread_started = False 



#class Obj:
#
#	__button_list = []
#	mutex_key = Lock()	
#
#	def __init__(self,initData):
#		pass
#
#	def SetButton(index,value):
#		button_list[index] = value


def polling_buttons():
	old_button = -1
	thread_started = True
	while True:
		button = panel_driver.read_buttons()
		if button >= 0 and button != old_button:
			mutex_key.acquire()
			button_list.append(button)	
			mutex_key.release()
			print (button_list)
			old_button = button	

polling_thread = Thread(target = polling_buttons, args = (),)


def read_pressed_button():
	if thread_started is not True:
		start(polling_thread)
	if button_list:
		mutex_key.acquire()
		first_element = button_list.pop(0)
		mutex_key.release()
		print first_element
		return first_element
	return 'no buttons pressed'	
	
def start(thread):
	thread.daemon = True # Terminate thread when "main" is finished
	thread.start()
	#thread.join()

