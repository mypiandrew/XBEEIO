# XBEEIO
XBEE IO Python Data Acquisition Scripts

## Installation

```
apt-get update && apt-get install python3-setuptools python-serial
mkdir digixbee
cd digixbee
wget https://github.com/mypiandrew/xbee-python/archive/1.2.0.zip -O digi-xbee-1.2.0.zip
unzip digi-xbee-1.2.0.zip
cd xbee-python-1.2.0/
python3 setup.py install
cd ..
mkdir xbeeio
wget https://github.com/mypiandrew/XBEEIO/archive/master.zip -O xbeeio.zip
unzip xbeeio.zip
cd XBEEIO-master/
chmod +x *.py 
```


## Sample usage 

Setup local XBEE unit first

```
./configurexbee.py -p XBEE_SERIAL_PORT -b="9600,8,N,1"

+++
OK

RESULT=OK
ATAP=1
OK

RESULT=OK
ATID=2513
OK

RESULT=OK
ATNIXBEEPI
OK

RESULT=OK
ATWR
OK

RESULT=OK
ATAC
OK

RESULT=OK

** Local XBEE Unit Now Configured **

```


```XBEE_SERIAL_PORT``` is the serial port name that the local XBEE unit installed in the Pi Unit is connected to and will be typically one of ```ttyAMA0``` ```ttyS1``` or ```ttyUSB1``` depending on the hardware configuration, see main website page on relevant IO card for further details on this.


***Note : To avoid problems it is important to wait about 60 seconds after power up before doing performing any network activity (either scans or transmissions).***



Run network discovery to discover remote IO nodes

```
# ./xbeeio.py --port ttyUSB1 --discover
Scanning network for devices...
Discovered a network of 1 devices:

XBEE1   |  0013A200415D1518

```

Read back IO from a target remote unit

```
# ./xbeeio.py --port ttyUSB1 --remote XBEE1 --readall
Analog 0 Volts: 0.723
Analog 1 Volts: 0.723
Analog 2 Volts: 0.718
Analog 3 Volts: 0.716
Digital 0 In:   1
Digital 1 In:   1
Digital 2 In:   1
Digital 3 In:   1

```


Read back values from remote unit formatted

```
# ./xbeeio.py --port ttyUSB1 --remote XBEE1 --readall --format temp
Analog 0 Temprature:    22.3
Analog 1 Temprature:    22.6
Analog 2 Temprature:    21.8
Analog 3 Temprature:    21.4
Digital 0 In:   1
Digital 1 In:   1
Digital 2 In:   1
Digital 3 In:   1

```


Set Digital Output Lines

```# ./xbeeio.py --port ttyUSB1 --remote XBEE1 --setdigout 0010
DIGOUT 0 set to 0
DIGOUT 1 set to 0
DIGOUT 2 set to 1
DIGOUT 3 set to 0

```


Readback as log line

```
# ./xbeeio.py --port ttyUSB1 --remote XBEE1 --readall --outputlogline --format volts
20191122;15:09;XBEE1;ANAIN0;0.723;ANAIN1;0.723;ANAIN2;0.718;ANAIN3;0.716;DIGIN0;1;DIGIN1;1;DIGIN2;1;DIGIN3;1;

```


## Command line syntax and examples


```
# ./xbeeio.py -h
usage: xbeeio.py [-h] --port PORT [--discover] [--remote REMOTE] [--readall]
                 [--format FORMAT] [--readadc ANAPINS] [--readdigin DIGIPINS]
                 [--outputstd] [--outputlogline] [--outputjson]
                 [--setdigouts SETDIGOUT] [--quiet]

XBEE-IO Communication Script

optional arguments:
  -h, --help            show this help message and exit
  --port PORT           serial port to connect to
  --discover            discover the digimesh network devices
  --remote REMOTE       specify the target XBee NI identifier to talk to
  --readall             read back all input/output states
  --format FORMAT       printable format : volts|420|temp
  --readadc ANAPINS     read back on or more analog inputs
  --readdigin DIGIPINS  read back one or more digital inputs
  --outputstd           display the output in human readable form (default)
  --outputlogline       display output in single data log format
  --outputjson          display output in JSON format
  --setdigouts SETDIGOUT
                        set digouts as 4bit state <0123>
  --quiet               suppress extra output

Example usage:

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
    
```
