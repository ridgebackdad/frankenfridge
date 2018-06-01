#!/usr/bin/python
#
# SalamiPi
#
# Author: Rick Highness
# Version: 2.0
# Updated: 2017-06-06
#
# sql = "insert into actions VALUES(null, '%s', '%s', '%s')" % (str(datetime.now()), 'heat', 0)
#    mysql_query(sql);

import Adafruit_DHT
import os
from time import sleep
from datetime import datetime
import RPi.GPIO as GPIO
import argparse
import sys
import MySQLdb

# Actions Table
#+------------+-------------+------+-----+-------------------+-----------------------------+
#| Field      | Type        | Null | Key | Default           | Extra                       |
#+------------+-------------+------+-----+-------------------+-----------------------------+
#| id         | int(11)     | NO   | PRI | NULL              | auto_increment              |
#| actiontime | timestamp   | NO   |     | CURRENT_TIMESTAMP | on update CURRENT_TIMESTAMP |
#| mode       | varchar(25) | YES  |     | NULL              |                             |
#| action     | tinyint(1)  | YES  |     | NULL              |                             |
#+------------+-------------+------+-----+-------------------+-----------------------------+
#
# Control Table
#+-----------+------------+------+-----+-------------------+-----------------------------+
#| Field     | Type       | Null | Key | Default           | Extra                       |
#+-----------+------------+------+-----+-------------------+-----------------------------+
#| id        | int(11)    | NO   | PRI | NULL              | auto_increment              |
#| entrytime | timestamp  | NO   |     | CURRENT_TIMESTAMP | on update CURRENT_TIMESTAMP |
#| temp      | tinyint(4) | YES  |     | NULL              |                             |
#| humid     | tinyint(4) | YES  |     | NULL              |                             |
#| heat      | tinyint(4) | YES  |     | NULL              |                             |
#+-----------+------------+------+-----+-------------------+-----------------------------+


#
# These are the GPIO pins that correspond to the devices connected
#
humid = 23
cooler = 18
sensor = 17

Mode = "Run"
naptime = 60

parser = argparse.ArgumentParser(description='This is a demo script by Rick')
parser.add_argument('-t','--tmax', help='Temperature maximum',required=True)
parser.add_argument('-hu','--hmax', help='Humidity maximum',required=True)
args = parser.parse_args()

print ("Max Temp: %s" % args.tmax)
print ("Max Hum: %s" % args.hmax)
tmax = int(args.tmax)
hmax = int(args.hmax)


def checksensor(whichone):
    "function_checksensor"
    Hu, Temp = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, sensor)
    ext_temp = 0

    if Temp > 0:
        Temp = Temp * 9/5 +32

    if Temp > 3000:
      Temp = -999

    if Hu > 3000:
      Hu = -999

    Hu = round(Hu,2)
    Temp = round(Temp,2)
    mysql_query("insert into temperatures VALUES(null, '%s', '%s', '%s', '%s')" % (str(datetime.now()), str(Temp), str(Hu), str(ext_temp)))

    if whichone == 'TEMP':
      return Temp
    else:
      return Hu


#def checksensorhumid():
#    "function_hmumidity"
#    Hu, Temp = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, sensor)
#
#    if Hu > 3000:
#      Hu = -999
#
#    return Hu


def mysql_query(sql):
    import MySQLdb
    db = MySQLdb.connect(host="localhost",
                         user="root",
                         passwd="root",
                         db="cabinet")
    cursor = db.cursor()
    print ("Passed query: %s" % sql)
    number_of_rows = cursor.execute(sql)
    db.commit()
    db.close()


def writelog(entry):
  text_file = open("salamipi.log", "a")
  text_file.write(entry)
  text_file.close()
  return

def switch(mode, pin):
    "function_switch"
    #
    # This function allows us to turn a switch ON or OFF
    # by specifying the mode and the GPIO pin #
    #
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, mode == 'on') # if state is on, connect the circuit, otherwise break the circuit
    Hu, Temp = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, sensor)
    if Temp > 0:
        Temp = Temp * 9/5 +32

    if pin == 18:
       sqlmode = "cool"
    else:
       sqlmode = "humid"

    if mode == 'on':
       onmode = 1
    else:
       onmode = 0
    
    mysql_query("insert into actions VALUES(null, '%s', '%s', '%s')" % (str(datetime.now()), sqlmode, onmode))
    writelog(str(datetime.now()) + " - " + str(int(float(Temp))) + "F - " + str(int(float(Hu))) + "% - " + str(mode) + " - " + str(pin) + "\n")
    return


def checkstate(pin):
    "function_checkstate"
    #
    # Is the pin already on / off?
    #
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(pin, GPIO.OUT)
    return GPIO.input(pin)



def checkthetemp():
    Temp = checksensor('TEMP')

    state = checkstate(cooler)
    print ""
    print str(datetime.now())
    print ""
    print ("---TEMPERATURE: %3.2fF" % (Temp))
    print ""


    if Temp > 3000:
      print "SKIP-READING SPIKE"
      print ""

    elif Temp > tmax and Temp < 3000:
      if (checkstate(cooler) == 1):
        print "COOLER ALREADY ON"
      else:
        print "Turning cooler ON"
        switch('on', cooler)
        print ""

    elif Temp < tmax:
      #
      # This is our temperature sweet spot
      #
      if (checkstate(cooler) == 0):
        print "COOLER ALREADY OFF"
      else:
        print "Turning cooler OFF"
        switch('off', cooler)

    elif Temp < tmin and Temp > 0:
      if (checkstate(cooler) == 0):
        print "COOLER ALREADY OFF"
      else:
        print "Turning cooler OFF"
        switch('off', cooler)

    else:
      print "SKIP - TEMP READING FAILED"
      #switch('off', cooler)

    sleep(naptime)
    return



def checkthehumidity():
    Hu = checksensor('HUMID')

    print str(datetime.now())
    print ""
    print ("---HUMIDITY: %4.2f%%" % (Hu))
    print ""
    #print "CHECKSTATE = " + str(checkstate(humid))

    if Hu > 3000:
      print "SKIP-READING SPIKE"
      print ""

    elif Hu > hmax and Hu < 3000:
      if (checkstate(humid) == 0):
        print "Humidity already OFF"
      else:
        print "Turning humidity OFF"
        switch('off', humid)

    elif Hu > hmax:
      #
      # This is our humidity sweet spot
      #
      if (checkstate(humid) == 0):
         print "HUMIDITY ALREADY OFF (SS)"
      else:
        print "Turning humidy OFF"
        switch('off', humid)

    elif Hu < hmax and Hu > 0:
      if (checkstate(humid) == 1):
        print "HUMIDITY ALREADY ON (LOW)"
      else:
        print "Turning humidity ON"
        switch('on', humid)

    else:
      print "SKIP - HUMID READING FAILED"
      print ("HUMID = %f" % (Hu))
      print ("HUMID MAX = %f" % (hmax))
      #switch('off', humid)

    sleep(naptime)
    return


try:
    mysql_query("insert into actions VALUES(null, '%s', '%s', '%s')" % (str(datetime.now()), 'start', 0))
    switch('off', cooler)
    switch('off', humid)

    while Mode == "Run" :
      checkthetemp()
      checkthehumidity()
except KeyboardInterrupt:
    print('Program terminated.')
    GPIO.cleanup()
    mysql_query("insert into actions VALUES(null, '%s', '%s', '%s')" % (str(datetime.now()), 'exit', 0))
