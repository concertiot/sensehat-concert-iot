#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  actuator_pub.py
#  
#  Copyright 2017  <pi@stevieGSenseHat>
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

#!/usr/bin/python

import paho.mqtt.client as paho
import os
import socket
import ssl
import json
import time
import config
import requests
import getpass
from time import sleep
#from sense_hat import SenseHat
from pprint import pprint

#sense = SenseHat()
connflag = False

f = open('deviceId', 'r')
deviceId = f.read()
f.close()
f = open('awsHost','r')
awshost = f.read()
f.close()

deviceHeader = ""
LED_SensorType = ""
Switch_Sensor_Type = ""

"""
Function: 
- checkStatusCode
Params: 
- status_code (int): represents the output of a REST call
- Url (string): Url that is being invoked
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


"""
Function: 
- getDeviceHeader
Params: 
- 
Returns:
- 
Purpose:
- user login to get access code for headers for other API calls (sets deviceHeader)
Other:
- Note that the access code will last for c. 5 mins so could make the username and 
password gloabl and call the auth request on a regular basis.
"""
def getDeviceHeader():

	global deviceHeader
	
	authHeaders = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}

	userName = input("Concert username[iotpadminuser]: ") or "iotpadminuser"
	password = getpass.getpass("Password for {0}: ".format(userName))

	try:
		print("authURL: {0}".format(config.authUrl))
	
		response = requests.post(config.authUrl,
	                             headers = authHeaders, 
	                             data = {"client_id" : "ui", 
	                                     "username" : userName, 
	                                     "password" : password, 
	                                     "grant_type" : "password"
								        }
	                        )
		checkStatusCode(response.status_code,config.authUrl)         
		print (response)
	
	except requests.exceptions.ConnectionError as connErr:
		print("Connection Error: {0}".format(str(connErr)))
		exit(1)
	except requests.exceptions.RequestException as e:
		print("Response Exception Raised on auth URL: {0}".format(str(e)))
		print("Address exception: Quitting")
		exit(1)


	#keycloak = response.json()
	#access_token = response.json()['access_token']

	deviceHeader = {"Authorization" : "Bearer " + response.json()['access_token'], 
					"Content-Type" : "application/json"}

"""
Function: 
- getSensorTypeId
Params: 
- sensor (string): sensor name for which we are looking the Id
Returns:
- the sensor typeId (or empty string if not found)
Purpose:
- gets and sets the typeId for the supplied sensor name (for the associated deviceId)
"""

def getSensorTypeID(sensor):
	
	try:
		sensorTypeResp = requests.get(config.sensorTypesUrl,
									  headers = deviceHeader)

		checkStatusCode(sensorTypeResp.status_code,config.sensorTypesUrl)         
	                             
	except requests.exceptions.ConnectionError as connErr:
		print("Connection Error: {0}".format(str(connErr)))
		exit(1)
	except requests.exceptions.RequestException as e:
		print("Response Exception Raised on device Types URL: {0}".format(str(e)))
		print("Address exception: Quitting")
		exit(1)


	typeId = ''
	for s in sensorTypeResp.json():
		if s["name"] == sensor:
			typeId = s["id"]
			break	
	return typeId	


"""
Function: 
- getSnapshotSensorValue
Params: 
- devId (string): deviceId for device
- sensor (string): sensor name for which we are looking the Id
Returns:
- the sensor value for the device
Purpose:
- gets the current snapshot value of the sensor for the device.
- gets the list of sensors for the device and searches for the sensor name sensor.
- returns an empthy string if not found.
"""
def getSnapshotSensorValue(devId, sensor):
	
	try:
		snapshotValues = requests.get(config.devicesUrl + "/" + devId + "/snapshot",
									  headers = deviceHeader)

		checkStatusCode(snapshotValues.status_code,config.devicesUrl + "/" + devId + "/snapshot")         
	                             
	except requests.exceptions.ConnectionError as connErr:
		print("Connection Error: {0}".format(str(connErr)))
		exit(1)
	except requests.exceptions.RequestException as e:
		print("Response Exception Raised on device Snapshot URL: {0}".format(str(e)))
		print("Address exception: Quitting")
		exit(1)


	sense_val = ''
	for s in snapshotValues.json()["sensors"]:
		if s["name"] == sensor:
			sense_val = s["value"]
			break	
	return sense_val
	

"""
Function: 
- buildJSONStrAWS
Params: 
- mess (string): message to send as part of json string
- switch (int): value of switch (0, or 1)
Returns:
- json object
Purpose:
- creates the json object to include in the publish message
"""
def buildJSONStrAWS(mess, switch):
	
	message = {}
	state = {}
	desired = {}
	latest = {} 
	sensors = {}
	
	
	sensors["LED"] = mess
	sensors["Switch"] = switch


	latest['sensors'] = sensors
	latest['timestamp'] = int(time.time() *1000)
	desired['latest'] = latest
	state['desired'] = desired
	message['state'] = state
		
	return json.dumps(message)
	

"""
Function: 
- on_conect
Params: 
- connecing to mqt broker
Returns:
- 
Purpose:
- see paho-mqtt
"""
def on_connect(client, userdata, flags, rc):
    global connflag
    connflag = True
    if rc==0:
        print ("Connection status: successful")
    elif rc==1:
        print ("Connection status: Connection refused")



new_Mess_Display = ""
curr_Mess_Display = ""
curr_Display_Switch = 0
new_Display_Switch = 0

do_publish = 0


def doCurrMessDisplay():
	
	print("Current Message: ""{0}""".format(getSnapshotSensorValue(deviceId,"LED")))
	
def doDisplayMessStatus():
	
	print("Current Message Switch: {0}".format(getSnapshotSensorValue(deviceId,"Switch")))
	
def doChangeMessDisplay():

	global new_Mess_Display
	global curr_Mess_Display
	global do_publish
	
	new_Mess_Display = input("Enter Message for Display: ")
	if new_Mess_Display != getSnapshotSensorValue(deviceId,"LED"):
		do_publish = 1
		curr_Mess_Display = new_Mess_Display
	else:
		do_publish = 0
		
def doSetDisplayStatus():
	
	global new_Display_Switch
	global curr_Display_Switch
	global curr_Mess_Display
	global new_Display_Switch
	global do_publish
	
	while(1):
		new_Display_Switch = input("0 for ""'Off'"", anything else for ""'On'"" : ")
		if new_Display_Switch.isdigit():
			if int(new_Display_Switch) != 0:
				new_Display_Switch = 1
			if new_Display_Switch != getSnapshotSensorValue(deviceId,"Switch"):
				do_publish = 1
				curr_Display_Switch = new_Display_Switch
			elif new_Display_Switch == 1:
				do_publish = 1
			else:
				do_publish = 0
			break
		else:
			print("FFS! For real? Enter a digit!")
		
	

def main():

	global LED_SensorType
	global Switch_Sensor_Type
	global do_publish
	global curr_Display_Switch
	global curr_Mess_Display

	getDeviceHeader()
	
	#LED_SensorType =  getSensorTypeID("LED")
	#Switch_Sensor_Type = getSensorTypeID("Switch")
	
	curr_Display_Switch = getSnapshotSensorValue(deviceId,"Switch")
	curr_Mess_Display = getSnapshotSensorValue(deviceId,"LED")
	
	jmsg = ""
	mqttc = paho.Client()
	mqttc.on_connect = on_connect

	awsport = 8883
	caPath = "root-CA.crt"
	certPath = deviceId + '.cert.pem'
	keyPath = deviceId + '.private.key'

	mqttc.tls_set(caPath, 
				  certfile=certPath, 
                  keyfile=keyPath, 
                  cert_reqs=ssl.CERT_REQUIRED, 
                  tls_version=ssl.PROTOCOL_TLSv1_2, 
                  ciphers=None)
              
	mqttc.connect(awshost, awsport, keepalive=60)

	mqttc.loop_start()
	
	sleep(1)
	
	# Blocking call that processes network traffic, dispatches callbacks and
	# handles reconnecting.
	# Other loop*() functions are available that give a threaded interface and a
	# manual interface.

	
	try:
		while (True):
			while(True):
						
				print("\n\n1. Current Message Display")
				print("2. Display message status?")
				print("3. Set Message to Display")
				print("4. Set display Status")
		
				choice = input("\nEnter choice (1 - 4): ")
		
				if choice.isdigit():
					if int(choice) > 0 and int(choice) < 5:
						if int(choice) == 1:
							doCurrMessDisplay()
							do_publish = 0
						elif int(choice) == 2:
							doDisplayMessStatus()
							do_publish = 0
						elif int(choice) == 3:
							doChangeMessDisplay()
						else:
							doSetDisplayStatus()
						break
					else:
						print("Come on!!!. Between 1 and 4")
				else:
					print("You know what a digit between 1 and 4 is???")
			# while(1) end
		
			if do_publish == 1:
				jmsg = buildJSONStrAWS(curr_Mess_Display,curr_Display_Switch)
			                 

				if connflag == True:
					mqttc.publish("$aws/things/" + deviceId + "/shadow/update", jmsg, qos=1)
			
					print("\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>") 
					pprint(json.loads(jmsg))
					print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")
					sleep(0.1)
				else:
					print("waiting for connection...")
					sleep(5)
		# end while(True)	
	
	except KeyboardInterrupt:
		print("Keyboard Interrupt detected: Quitting:")
		mqttc.loop_stop()
		exit(1)
	
	
	

if __name__ == '__main__':
	main()





