#!/usr/bin/python

import paho.mqtt.client as paho
import os
import socket
import ssl
import json
import time
from time import sleep
from sense_hat import SenseHat
from pprint import pprint


connflag = False

f = open('deviceId', 'r')
deviceId = f.read()
f.close()


print ("Publishing sensor readings for device: {0}".format(deviceId))

pubFrequency = float(input("Enter publish frequency in seconds [10]: ") or 10)

def on_connect(client, userdata, flags, rc):
    global connflag
    connflag = True
    if rc==0:
        print ("Connection status: successful")
    elif rc==1:
        print ("Connection status: Connection refused")

sense = SenseHat()

mqttc = paho.Client()
mqttc.on_connect = on_connect

awshost = "a2cg1hqpl5l7ve.iot.eu-west-1.amazonaws.com"
awsport = 8883
clientId = "rpisensehat-publisher"
caPath = "root-CA.crt"
certPath = deviceId + '.cert.pem'
keyPath = deviceId + '.private.key'
green = (0, 255, 0)

mqttc.tls_set(caPath, 
              certfile=certPath, 
              keyfile=keyPath, 
              cert_reqs=ssl.CERT_REQUIRED, 
              tls_version=ssl.PROTOCOL_TLSv1_2, 
              ciphers=None)
              
mqttc.connect(awshost, awsport, keepalive=60)

mqttc.loop_start()

try:

	while True:
		
		message = {}
		state = {}
		reported = {}
		latest = {}
    
		# should not have to do this??? 
		rawo = sense.get_gyroscope()

		orientation = sense.get_accelerometer()
     
		sensors = {}
		sensors['temperature'] = round(float(sense.get_temperature()),2)
		sensors['pressure'] = round(float(sense.get_pressure()),2)
		sensors['humidity'] = round(float(sense.get_humidity()),2)
		sensors['pitch'] = round(float(orientation['pitch']),2)
		sensors['roll'] = round(float(orientation['roll']),2)
		sensors['yaw'] = round(float(orientation['yaw']),2)

		latest['sensors'] = sensors
		latest['timestamp'] = int(time.time()) *1000
		reported['latest'] = latest
		state['reported'] = reported
		message['state'] = state

		jsonData = json.dumps(message)

		if connflag == True:
		#sense.show_message ('x')
			sense.clear(green) 
			mqttc.publish("$aws/things/" + deviceId + "/shadow/update", jsonData, qos=1)
			print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
			pprint(json.loads(jsonData))
			print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")
			sleep(1)
			sense.clear()
			sleep(pubFrequency-1)
		else:
			print("waiting for connection...")
			sleep(5)
			
except KeyboardInterrupt:
	print("Keyboard Interrupt detected: Quitting:")
	exit(1)
