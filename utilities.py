#     Utilities for the following scripts     #
#											  #
#		      setlocalxbeebaud.py 		  	  #
#		      setlocalxbeedest.py 		 	  #
#		      setlocalxbeetoapi.py   		  #
#											  #
import os.path
import serial, time, sys
from xbee.backend.base import TimeoutException


def stmatch(var):

	stopbits = {  "0" : "1",
		  		  "1" : "2"  }

	for key, value in stopbits.items():
		if var == value:
			return(key)

def bamatch(var):

	baud = { "0" : "1200",
		  	 "1" : "2400",
		  	 "2" : "4800",
		  	 "3" : "9600", 
		  	 "4" : "19200",
		  	 "5" : "38400",
		  	 "6" : "57600",
		  	 "7" : "115200" }
		  	
	for key, value in baud.items():
		if var == value:
			return(key)


def pamatch(var):

	par = { "0" : "N",
		  	"1" : "E",
		  	"2" : "O",
		  	"3" : "M" }

	for key, value in par.items():
		if var == value:
			return(key)

def match(var):

	par = { 
			serial.PARITY_NONE : "N",
		  	serial.PARITY_EVEN : "E",
		  	serial.PARITY_ODD  : "O",
		  	serial.PARITY_MARK : "M",
		  	serial.PARITY_SPACE: "S",
			serial.FIVEBITS : '5',
			serial.SIXBITS  : '6',
			serial.SEVENBITS: '7',
			serial.EIGHTBITS: '8', 
			serial.STOPBITS_ONE: '1',
			serial.STOPBITS_ONE_POINT_FIVE: '1.5',
			serial.STOPBITS_TWO: '2' 
										   }
	for key, value in par.items():
		if var == value:
			return(key)



def receive(ser):
	#ser.flush()
	EOF = '0d'
	result = ''
	modules = []
	dictionary = {}
	time.sleep(1)
	while ser.inWaiting():
		data = ''
		while True:
			temp = ser.read()
			if temp.encode('hex') == EOF:
				if data == '':
					result += ' '
				break
			else:
				data += temp
				result += temp
		if 'XBEE' in data:
			modules.append(data)
		print data


	print '\nRESULT=' + result

	responses = list(filter(None, result.split(' ')))

	for i in range(0, len(responses)):
		for module in modules:
			if module in responses[i]:
				dictionary.update({module:responses[i]})

	return dictionary


		
def send(ser, data):
	if data == '+++':
		time.sleep(1)
		ser.write(data)
		print (data)
		time.sleep(1.2)
	else:
		time.sleep(0.2)
		ser.write(data)
		print (data)








