#!/usr/bin/python3
import json
import sys, time
import random
import math
import argparse, os.path
from datetime import datetime
from digi.xbee.util import utils
from digi.xbee.io import IOLine, IOValue
from digi.xbee.models.address import XBee64BitAddress
from digi.xbee.devices import DigiMeshDevice, RemoteDigiMeshDevice


BAUD_RATE = 9600
NOW = datetime.now()

# https://realpython.com/python-rounding/
def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

def round_half_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier



def Output(RemoteXBee, Formed, fmt, nodeid, mode, anapins, digipins, verbosity):

    i = 0
    printListA = ['', '', '', '']
    printListD = ['', '', '', '']
    logBase = NOW.strftime("%Y%m%d;%H:%M;") + nodeid
    jsonBase = '{0} "date": {1},'.format('{',NOW.strftime("%Y%m%d")) + ' "time": {0},'.format(NOW.strftime("%H:%M")) + ' "node": {0},'.format(nodeid)
    jsonAnalog = ''
    logAnalog = ''

    
    
    # User input --readana=anapins
    if anapins:

        if mode == 'log':
            logAnalog = logBase
            for c in anapins.replace(',',''):
                logAnalog = logAnalog + ";ANAIN" + "{0}".format(c) + ";" + str(Formed[i])
                i += 1

        elif mode == 'json':
            jsonAnalog = jsonBase
            for c in anapins.replace(',', ''):
                jsonAnalog = jsonAnalog + ' "ANAIN{0}": {1},'.format(c, Formed[i])
                i += 1

        else:
            if fmt == 'temp':
                for c in anapins.replace(',',''):
                    out = "Analog {0} Temprature:\t{1}".format(c, Formed[i])
                    printListA[int(c)] = out
                    i += 1
            elif fmt == '420':
                for c in anapins.replace(',',''):
                    out = "Analog {0} 4-20mA:\t{1}".format(c, Formed[i])
                    printListA[int(c)] = out
                    i += 1 
            else:
                for c in anapins.replace(',',''):
                    out = "Analog {0} Volts:\t{1}".format(c, Formed[i])
                    printListA[int(c)] = out
                    i += 1


    # User input --readdig=digipins
    if digipins:

        if mode == 'log':
            if anapins:
                logFinal = logAnalog
            else:
                logFinal = logBase

            for c in digipins.replace(',',''):
                logFinal = logFinal + ";DIGIN" + "{0}".format(c) + ";" + str(Formed[i])
                i += 1

        elif mode == 'json':
            if anapins:
                jsonFinal = jsonAnalog
            else:
                jsonFinal = jsonBase

            for c in digipins.replace(',', ''):
                jsonFinal = jsonFinal + ' "DIGIN{0}": {1},'.format(c, Formed[i])
                i += 1

        else:
            for c in digipins.replace(',',''):
                    out = "Digital {0} In:\t{1}".format(c, Formed[i])
                    printListD[int(c)] = out
                    i += 1


    # Append final characters,
    #    output to chosen format
    if mode == 'log':
        if digipins:
            print(logFinal + ';')
        else:
            print(logAnalog + ';')

    elif mode == 'json':
        if digipins:
            print(jsonFinal[:len(jsonFinal)-1] + ' }')
        else:
            print(jsonAnalog[:len(jsonAnalog)-1] + ' }')

    elif mode == 'std' or mode == 'default':
        for out in printListA:
            if out != '':
                print(out)
        for out in printListD:
            if out != '':
                print(out)



def Format(RemoteXBee, values, fmt, anapins, digipins):
    
    i = 0
           
    #######   TempInCelcius = (Vout - 500)/10   #######
    if fmt == 'temp': 
        if anapins:
            for c in anapins.replace(',',''):
                # !Estimated! Per-reading accuracy +/- 0.3°C to 0.5°C (on top of TMP36 accuracy)
                values[i] = round_half_up(float((values[i]/1023)*2.5),3)
                values[i] = truncate((((values[i]*1000)-500)/10),2)
                i += 1

        if digipins:
            for c in digipins.replace(',',''):
                if 'HIGH' in str(values[i]):
                    values[i] = 1
                else:
                    values[i] = 0 
                i += 1
    
    #######   4-20mA = ADC / 1023 * VRef * 10   #######
    elif fmt == '420':
        if anapins:
            for c in anapins.replace(',',''):
                # Per reading accuracy +/- 0.03mA to 0.04mA
                # looks wierd but works 
                values[i] = round_half_up(float((values[i]/1023)*2.5),3)
                values[i] = truncate(values[i]*10,2)
                i += 1

        if digipins:
            for c in digipins.replace(',',''):
                if 'HIGH' in str(values[i]):
                    values[i] = 1
                else:
                    values[i] = 0
                i += 1 
    
    #######   Volts = ADC / 1023 * VRef   #######
    else:
        if anapins:
            for c in anapins.replace(',',''):
                # Per-reading accuracy +/- 3mV to 4mV
                values[i] = round_half_up(float((values[i]/1023)*2.5),3)
                i += 1

        if digipins:
            for c in digipins.replace(',',''):
                if 'HIGH' in str(values[i]):
                    values[i] = 1
                else:
                    values[i] = 0 
                i += 1


    return values



def SetDigitalOut(RemoteXBee, digouts, verbosity):

    ### ------ Digital Out ------ ###
    ###                           ###
    ###  P5       DIO15/SPI_MISO  ###
    ###  P6       DIO16/SPI_MOSI  ###
    ###  P7       DIO17/SPI_SSEL  ###
    ###  P8       DIO18/SPI_SCLK  ###
    ###                           ###
    ### ------------------------- ###

    if digouts[0] == '0':
        verbose(verbosity, "DIGOUT 0 set to 0")
        RemoteXBee.set_dio_value(IOLine.DIO18, IOValue.LOW)
    else:
        verbose(verbosity, "DIGOUT 0 set to 1")
        RemoteXBee.set_dio_value(IOLine.DIO18, IOValue.HIGH)

    if digouts[1] == '0':
        verbose(verbosity, "DIGOUT 1 set to 0")
        RemoteXBee.set_dio_value(IOLine.DIO17, IOValue.LOW)
    else:
        verbose(verbosity, "DIGOUT 1 set to 1")
        RemoteXBee.set_dio_value(IOLine.DIO17, IOValue.HIGH)

    if digouts[2] == '0':
        verbose(verbosity, "DIGOUT 2 set to 0")
        RemoteXBee.set_dio_value(IOLine.DIO16, IOValue.LOW)
    else:
        verbose(verbosity, "DIGOUT 2 set to 1")
        RemoteXBee.set_dio_value(IOLine.DIO16, IOValue.HIGH)

    if digouts[3] == '0':
        verbose(verbosity, "DIGOUT 3 set to 0")
        RemoteXBee.set_dio_value(IOLine.DIO15, IOValue.LOW)
    else:
        verbose(verbosity, "DIGOUT 3 set to 1")
        RemoteXBee.set_dio_value(IOLine.DIO15, IOValue.HIGH)      


def ReadDigital(RemoteXBee, digipins, verbosity):

    ### ------ Digital In ------ ###
    ###                          ###
    ###  Digital 0    DIO4       ###
    ###  Digital 1    DIO6/RTS   ###
    ###  Digital 2    DIO7/CTS   ###
    ###  Digital 3    DIO11/PWM1 ###
    ###                          ###
    ### ------------------------ ### 

    DigitalList = [] 
    for c in digipins:

        if c == '0':
            DigitalList.append(RemoteXBee.get_dio_value(IOLine.DIO4_AD4))
        elif c == '1':
            DigitalList.append(RemoteXBee.get_dio_value(IOLine.DIO6))
        elif c == '2':
            DigitalList.append(RemoteXBee.get_dio_value(IOLine.DIO7))
        elif c == '3':
            DigitalList.append(RemoteXBee.get_dio_value(IOLine.DIO11_PWM1))
    
    return DigitalList


def ReadAnalog(RemoteXBee, anapins, verbosity):
    
    ### ------- Analog In ------- ###
    ###                           ###
    ###   Analog 0     DIO0_AD0   ###
    ###   Analog 1     DIO1_AD1   ###
    ###   Analog 2     DIO2_AD2   ###
    ###   Analog 3     DIO3_AD3   ###
    ###                           ###
    ### ------------------------- ###

    AnalogList = []
    
    for c in anapins:

        if c == '0':
            AnalogList.append(RemoteXBee.get_adc_value(IOLine.DIO0_AD0))
        elif c == '1':
            AnalogList.append(RemoteXBee.get_adc_value(IOLine.DIO1_AD1))
        elif c == '2':
            AnalogList.append(RemoteXBee.get_adc_value(IOLine.DIO2_AD2))
        elif c == '3':
            AnalogList.append(RemoteXBee.get_adc_value(IOLine.DIO3_AD3))
        
    return AnalogList



def NetworkDiscovery(MainHub, verbosity):
    # Network Discovery 
    NodeID   = []
    Address  = []
    XBeeNetwork = MainHub.get_network()
    XBeeNetwork.clear()
    XBeeNetwork.set_discovery_timeout(4)
    XBeeNetwork.start_discovery_process()
    loading = loading_cursor()

    verbose(verbosity, "Scanning network for devices...")

    while XBeeNetwork.is_discovery_running():
        sys.stdout.write(next(loading))
        sys.stdout.flush()
        time.sleep(1)
        sys.stdout.write('\b')

    Devices = XBeeNetwork.get_devices()
    for dev in Devices:
        NodeID.append(dev.get_node_id())
        Address.append(str(dev.get_64bit_addr()))
        
    DevList = dict(zip(NodeID, Address))

    return DevList


def ShowRemote(MainHub, verbosity):
    # Similar to NetworkDiscovery() with extra shell output
    NodeID   = []
    Address  = []
    XBeeNetwork = MainHub.get_network()
    XBeeNetwork.clear()
    XBeeNetwork.set_discovery_timeout(4)
    XBeeNetwork.start_discovery_process()
    loading = loading_cursor()
    
    verbose(verbosity, "Scanning network for devices...")

    while XBeeNetwork.is_discovery_running():
        sys.stdout.write(next(loading))
        sys.stdout.flush()
        time.sleep(1)
        sys.stdout.write('\b')

    Devices = XBeeNetwork.get_devices()
    for dev in Devices:
        NodeID.append(dev.get_node_id())
        Address.append(str(dev.get_64bit_addr()))
        
    DevList = dict(zip(NodeID, Address))

    print("Discovered a network of %d devices:\n" % len(Devices))
    for key,value in DevList.items():
        print("{0}\t|  {1}".format(key, value))

    return DevList

def verbose(verbosity, output):
    if verbosity:
        pass
    else:
        print(output)


def loading_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

class ArgParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def main():
    

    DevList       = {}
    FormedAll     = []  # Ana Dig values after passing through Format()
    FormedAnalog  = []  # Ana values after passing through Format()
    FormedDigital = []  # Dig values after passing through Format()

    example_text = '''Example usage:

    # Run discovery process on nework to find XBEE-IO devices
    ./xbeeio.py --port ttyUSB1 --discover
     
    # Readback all IO in default format and output style
    ./xbeeio.py --port ttyUSB1 --remote XBEE1 --readall

    # Read all IO and format analogue readings as rounded up voltages
    ./xbeeio.py --port ttyUSB1 --remote XBEE1 --readall --format volts

    # Read ADC inputs 0,1 & 3 and format readings as rounded up (TMP36) temperatures 
    ./xbeeio.py --port ttyUSB1 --remote XBEE1 --readadc 031 --format temp

    # Read ADC input 2 and format reading as rounded up 4-20mA 
    ./xbeeio.py --port ttyUSB1 --remote XBEE1 --readadc 2  --format 420

    # Read Dig Ins 0,1,2 & 3 
    ./xbeeio.py --port ttyUSB1 --remote XBEE1 --readdigin 0321

    # Read Dig In 0 
    ./xbeeio.py --port ttyUSB1 --remote XBEE1 --readdigin 0

    # Set Dig Out 0,1 & 3 Enabled
    ./xbeeio.py --port ttyUSB1 --remote XBEE1 --setdigouts 1101

    # Set Dig out 1 & 3 Enabled
    ./xbeeio.py --port ttyUSB1 --remote XBEE1 --setdigouts 0101

    # Set Dig Out 0 = Enabled
    ./xbeeio.py --port ttyUSB1 --remote XBEE1 --setdigouts 1000

    # Read all inputs and output in a logline format with analog voltage formatted as rounded up volts
    ./xbeeio.py --port ttyUSB1 --remote XBEE1 --readall --outputlogline --format volts

    '''
    ap = ArgParser(description='XBEE-IO Communication Script', epilog=example_text, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", action='store', dest='port', help="serial port to connect to", required=True)
    ap.add_argument("--discover", action='store_true', dest='show', help="discover the digimesh network devices")
    ap.add_argument("--remote", action='store', dest='remote', help="specify the target XBee NI identifier to talk to")
    ap.add_argument("--readall", action='store_true', dest='readall', help="read back all input/output states")
    ap.add_argument("--format", action='store', dest='format', help="printable format : volts|420|temp")
    ap.add_argument("--readadc", action='store', dest='anapins', help="read back on or more analog inputs")
    ap.add_argument("--readdigin", action='store', dest='digipins', help="read back one or more digital inputs")
    ap.add_argument("--outputstd", action='store_true', dest='std', help="display the output in human readable form (default)")
    ap.add_argument("--outputlogline", action='store_true', dest='log', help="display output in single data log format")
    ap.add_argument("--outputjson", action='store_true', dest='json', help="display output in JSON format")
    ap.add_argument("--setdigouts", action='store', dest='setdigout', help="set digouts as 4bit state 0123>")
    ap.add_argument("--quiet", action='store_true', dest='quiet', help="suppress extra output")

    if len(sys.argv)==1:
        ap.print_help(sys.stderr)
        sys.exit(1)
    args = ap.parse_args()
    
    PORT = '/dev/' + args.port

    try:
        
        if args.show:
            # Instatiate RPi Main Hub
            RPi = DigiMeshDevice(PORT, BAUD_RATE)
            RPi.open()
            
            DevList = ShowRemote(RPi, args.quiet)

            # Export network devices to file
            with open('network.conf', 'w+') as f:
                f.truncate(0) # Reset file contents
                for node, address in DevList.items():
                    f.write(node + '|' + address + '\n')

        elif args.remote:

            # Instatiate RPi Main Hub
            RPi = DigiMeshDevice(PORT, BAUD_RATE)
            RPi.open()

            # Scan and save network if it does not exist
            if not os.path.exists('network.conf'):

                DevList = NetworkDiscovery(RPi, args.quiet)
                with open('network.conf', 'w+') as f:
                    for node, address in DevList.items():
                        f.write(node + '|' + address + '\n')

            # Repopulate dictionary for practicality
            with open("network.conf") as f:
                for line in f:
                    (node, address) = line.strip().split('|')
                    DevList.update({node:address})

            # Make sure target NodeID exists in network 
            if args.remote in DevList.keys():
                RemoteXBee = RemoteDigiMeshDevice(RPi, XBee64BitAddress.from_hex_string(str(DevList.get(args.remote))))
                #print("\n")
            else:
                print("Target NodeID: " + args.remote + " not found in network.conf, try rescan first.")
                exit()

        if args.setdigout:
            SetDigitalOut(RemoteXBee, args.setdigout, args.quiet)

        # Either --readall
        if args.readall:
            args.anapins = '0,1,2,3'
            args.digipins = '0,1,2,3' 
            readall = '0,1,2,3'
        
            ReadInputs = ReadAnalog(RemoteXBee, readall, args.quiet) + ReadDigital(RemoteXBee, readall, args.quiet)
            FormedAll = Format(RemoteXBee, ReadInputs, args.format, args.anapins, args.digipins)
        
        # Or read specific
        else:
            if args.anapins:
            
                ReadInputs = ReadAnalog(RemoteXBee, args.anapins, args.quiet)
                FormedAnalog = Format(RemoteXBee, ReadInputs, args.format, args.anapins, '') # No digital ''

            if args.digipins:

                ReadInputs = ReadDigital(RemoteXBee, args.digipins, args.quiet)
                FormedDigital = Format(RemoteXBee, ReadInputs, args.format, '', args.digipins) # No analog ''
        

        if args.std:

            if FormedAll:
                Output(RemoteXBee, FormedAll, args.format, args.remote, 'std', args.anapins, args.digipins, args.quiet)
            else:
                Output(RemoteXBee, FormedAnalog + FormedDigital, args.format, args.remote, 'std', args.anapins, args.digipins, args.quiet)

        elif args.json:
            
            if FormedAll:
                Output(RemoteXBee, FormedAll, args.format, args.remote, 'json', args.anapins, args.digipins, args.quiet)
            else:
                Output(RemoteXBee, FormedAnalog + FormedDigital, args.format, args.remote, 'json', args.anapins, args.digipins, args.quiet)

        elif args.log:

            if FormedAll:
                Output(RemoteXBee, FormedAll, args.format, args.remote, 'log', args.anapins, args.digipins, args.quiet)
            else:
                Output(RemoteXBee, FormedAnalog + FormedDigital, args.format, args.remote, 'log', args.anapins, args.digipins, args.quiet)

        else:
            
            if not args.show:
                if FormedAll:
                    Output(RemoteXBee, FormedAll, args.format, args.remote, 'default', args.anapins, args.digipins, args.quiet)
                else:
                    Output(RemoteXBee, FormedAnalog + FormedDigital, args.format, args.remote, 'default', args.anapins, args.digipins, args.quiet)

        

    finally:
        if RPi is not None and RPi.is_open():
            RPi.close()


if __name__ == '__main__':
    main()
