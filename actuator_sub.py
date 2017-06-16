#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  actuator_sub.py
#  
#  Copyright 2017  <pi@raspberrypi>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import paho.mqtt.client as mqtt
from random import randint
import json
from pprint import pprint
from sense_hat import SenseHat
import ssl
import time

red = (255,0,0)
blue = (0,0,255)


def getRGB():
	
	rgbArray = [0,0,0]
	for i in range(0,2):
		rgbArray[i] = randint(0,255)
	return rgbArray

"""	
Returns:
- Only if REST call is OK
Purpose:
- General purpose catchall for REST APIs.
- Will exit program if call to URL fails
"""
def checkStatusCode(status_code, Url):
	
	if status_code == 200 or status_code == 201:
		return
	else:
		print("Call to URL {0} failed with status code {1}".format(Url,status_code))
		print("Exiting")
		exit(1)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code:  {0:2d}".format(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_TOPIC1)
    
    #client.subscribe(MQTT_TOPIC2)
    #client.subscribe(MQTT_TOPIC3)
    #client.subscribe(MQTT_TOPIC4)


sense = SenseHat()

connflag = False

f = open('deviceId', 'r')
deviceId = f.read()
f.close()
f = open('awsHost','r')
awshost = f.read()
f.close()

mqttc = mqtt.Client()
mqttc.on_connect = on_connect

awsport = 8883
#clientId = "rpisensehat-publisher"
caPath = "root-CA.crt"
certPath = deviceId + '.cert.pem'
keyPath = deviceId + '.private.key'
mess_led = "Change me"

mqttc.tls_set(caPath, 
              certfile=certPath, 
              keyfile=keyPath, 
              cert_reqs=ssl.CERT_REQUIRED, 
              tls_version=ssl.PROTOCOL_TLSv1_2, 
              ciphers=None)

MQTT_BROKER = awshost
MQTT_TOPIC1 = "$aws/things/" + deviceId + "/shadow/update/accepted"
MQTT_TOPIC2 = "$aws/things/" + deviceId + "/shadow/update"
#MQTT_TOPIC3 = "SENSOR/SHOCK"
#MQTT_TOPIC4 = "SENSOR/SND/SMALL"

def buildJSONStrAWS(mess, switch):
	
	message = {}
	state = {}
	reported = {}
	latest = {} 
	sensors = {}
	
	
	sensors["LED"] = mess
	sensors["Switch"] = switch


	latest['sensors'] = sensors
	latest['timestamp'] = int(time.time() *1000)
	reported['latest'] = latest
	state['reported'] = reported
	message['state'] = state
		
	return json.dumps(message)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
	print("Topic:      " + msg.topic)
	jmsg = json.loads(msg.payload.decode("utf-8"))
	print("QOS:       {0:2d}".format(msg.qos))
	pprint(jmsg)
	print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")
	if "desired" in jmsg["state"]:
		if "LED" in jmsg["state"]["desired"]["latest"]["sensors"]:
			msg = jmsg["state"]["desired"]["latest"]["sensors"]["LED"]
			if jmsg["state"]["desired"]["latest"]["sensors"]["Switch"] == 1:
				sense.show_message(msg,scroll_speed = 0.05,text_colour = getRGB())
				
			jmsg = buildJSONStrAWS(msg,jmsg["state"]["desired"]["latest"]["sensors"]["Switch"])
			client.publish("$aws/things/" + deviceId + "/shadow/update", jmsg, qos=1)
			print("\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>") 
			pprint(json.loads(jmsg))
			print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")
			time.sleep(0.1)


def main():

	#client = mqtt.Client()
	#client.on_connect = on_connect
	
	
	mqttc.on_message = on_message
	print("About to connect\n")
	mqttc.connect(MQTT_BROKER, awsport, 60)
	print("After connect\n") 

	# Blocking call that processes network traffic, dispatches callbacks and
	# handles reconnecting.
	# Other loop*() functions are available that give a threaded interface and a
	# manual interface.
	
	mqttc.loop_start()
	input("After loop thread: Any Key\n")
	mqttc.loop_stop()
	
	return 0

if __name__ == '__main__':
	main()

