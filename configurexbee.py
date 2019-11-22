#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, time, cmd, serial, binascii, argparse
from utilities import match, send, receive

class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

help_text = '''
### Configure Local XBEE Module For Use with XBEE-IO Module ###

Configures :
    - XBEE Operating Mode to API (AP=1)
    - XBEE Network ID (ID=2513)
    - XBEE Node Name (NI=XBEEPI)
Saves Settings
Applies Changes

Example :

   ./configurexbee.py -p ttyUSB1 -b="9600,8,N,1"
   
   
\r\n\r\n
'''

parser = ArgParser(description='Set local XBEE operating mode', epilog=help_text, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("-p", action='store', dest='port', help="serial port to connect to")
parser.add_argument("-b", action='store', dest='baud', help="baud, databits, parity, stopbits")

# If there are no arguments
if len(sys.argv)==1:
    print "\r\n"
    parser.print_help(sys.stderr)
    sys.exit(1)

else:
	args = parser.parse_args()
	try:
		ser = serial.Serial()
		ser.port         = '/dev/' + args.port
		ser.baudrate = args.baud.split(',')[0]
		ser.bytesize = match(args.baud.split(',')[1])
		ser.parity       = match(args.baud.split(',')[2])
		ser.stopbits = match(args.baud.split(',')[3])

		ser.close()
		ser.open()

		send(ser, '+++')
		receive(ser)
		send(ser, 'ATAP=1\r')
		receive(ser)
		send(ser, 'ATID=2513\r')
		receive(ser)
		send(ser, 'ATNIXBEEPI\r')
		receive(ser)
		send(ser, 'ATWR\r')
		receive(ser)
		send(ser, 'ATAC\r')
		receive(ser)				
		print '\r\n** Local XBEE Unit Now Configured **\r\n\r\n'	
			
		ser.close()

	except serial.SerialException as e:
		print 'Serial Exception:' + e
                sys.exit(1)
