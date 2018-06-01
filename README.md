Frankenfridge Controller

So, I started a new hobby to create a charcuterie curing chamber (a fridge where I could cure tasty meat snacks). I built two controllers using InkBird components I bought from Amazon and wired them into outlet boxes.  One device controlled the cycling the fridge on/off to keep temperature at a predetermined temperature; while the other controller would cycle on/off the humidifier that was placed inside the fridge to keep the humidy at a predetermined dew point.

After making several batches of tasty meat snacks, I was curious to find out how often the fridge and the humidifier had cycled on/off.

Enter the Frankenfridge Controller - it is a Raspberry Pi 3 with the following hardware:

Real Time Clock (model DS1307)
2 PowerTail II power controllers (model 80135 or 80136 - Normally Closed or NC version)
AOSong AM2302 temperature and humidity sensor

Install the real time clock (which covers pins 1-10)

The AM2302 is connected to the Raspberry Pi via pins 1,5,11 (3v3, GPIO3, GPIO17)

One PowerSwitch Tail II is used for cooling is connected to pins 12,14 (CPIO18,Ground)
and the other PowerSwitch Tail II used for humidity is connected to pins 16,20 (CPIO23,Ground)

Prior to running the script, you will need to install the following:

i2c-dev module and the rtc-ds1307 module
mysql server

Once complete, install the following python libraries:

Adafruit_DHT
os
time
datetime
RPi.GPIO
argparse
sys
MySQLdb

Once these are installed, you will need to create the MySQL database:

CREATE TABLE `actions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `actiontime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `mode` varchar(25) DEFAULT NULL,
  `action` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
);
  
CREATE TABLE `controls` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entrytime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `temp` tinyint(4) DEFAULT NULL,
  `humid` tinyint(4) DEFAULT NULL,
  `heat` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `temperatures` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `entrytime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `internal_temp` varchar(11) DEFAULT NULL,
  `internal_humid` varchar(11) DEFAULT NULL,
  `external_temp` varchar(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

You can now run the frankenfridge.pl script from the command line:

./frankenfridge -t XX -hu YY

Where XX is the warmest (maximum) temperature that you want in the curing cabinet; while YY is the lowest (minimum) humidity percentage you want in the curing cabinet.

To set the curing temperature to 65ºF with 80% humidity: ./frankenfridge -t 65 -hu 80

If the curing chamber temperature drops below 65ºF, the PowerTail circuit will power up the fridge and let it run for 1 minute.  If after that minute, the temperature is still not under your minimum temperature, it will continue to run in 1 minute intervals until the temperature is under your maximum temperature.

This script will run with the parameters you set until you break out of the script with Ctrl-C.
