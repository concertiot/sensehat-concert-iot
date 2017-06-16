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


def buildJSONStrAWS(accel_rawo,accel_rawg,gyro_rawo, gyro_rawg,comp,hum,temp, pressure):
	
	message = {}
	state = {}
	reported = {}
	latest = {} 
	
	sensors = {}
	# Temperature: degrees Celcius
	sensors['temperature'] = round(temp,2)
	# Pressure: current pressure in millibars
	sensors['pressure'] = round(pressure,2)
	# Humidity: percentage of relative humidity - 0 - 100%
	sensors['humidity'] = round(hum,2)
	# Compass: The direction of North - 0 > 360 degrees
	sensors['compass'] = round(comp,2)
	
	# Accelerometer Sensor: Pitch, Roll and Yaw angle of axis - 0 -> 360 degrees
	sensors['accel pitch'] = round(accel_rawo['pitch'],2)
	sensors['accel roll'] = round(accel_rawo['roll'],2)
	sensors['accel yaw'] = round(accel_rawo['yaw'],2)
	
    # Accelerometer Sensor: Raw Y, X, Z axis values describing forces in Gs - -n -> +n 
	sensors["accel Y"] = round(accel_rawg['y'],2)
	sensors["accel X"] = round(accel_rawg['x'],2)
	sensors["accel Z"] = round(accel_rawg['z'],2)
	
	# Gyrometer Sensor: Pitch, Roll and Yaw - angle of the axis - 0 -> 360 degrees
	sensors['Gyro pitch'] = round(gyro_rawo['pitch'],2)
	sensors['Gyro roll'] = round(gyro_rawo['roll'],2)
	sensors['Gyro yaw'] = round(gyro_rawo['yaw'],2)
	
    # Gyrometer Sensor: Raw Y, X, Z axis values in radians per second
    # describing rotational intensity - -n -> +n 
    # Note a radian is the angle made between the centre and points on 
    # the circumference with a distance of the radius (c. 57.3 degrees)
    
	sensors["Gyro Y"] = round(gyro_rawg['y'],2)
	sensors["Gyro X"] = round(gyro_rawg['x'],2)
	sensors["Gyro Z"] = round(gyro_rawg['z'],2)
	
	#sensors["LED"] = "Feck Away Off"
	#sensors["Switch"] = 0


	latest['sensors'] = sensors
	latest['timestamp'] = int(time.time() *1000)
	reported['latest'] = latest
	state['reported'] = reported
	message['state'] = state
	
	return json.dumps(message)
	


connflag = False

f = open('deviceId', 'r')
deviceId = f.read()
f.close()
f = open('awsHost','r')
awshost = f.read()
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

awsport = 8883
#clientId = "rpisensehat-publisher"
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
	sense.set_imu_config(True, True, True) # Compass Gyroscope and Accelerometer
	
	while True:
		gyro_rawo = sense.get_gyroscope()
		gyro_rawg = sense.get_gyroscope_raw()
		accel_rawo = sense.get_accelerometer()
		accel_rawg = sense.get_accelerometer_raw()
		comp_raw = sense.get_compass_raw()
		
		                               
		jmsg = buildJSONStrAWS(accel_rawo,
			                  accel_rawg,
			                  gyro_rawo,
			                  gyro_rawg,
			                  sense.get_compass(),
			                  sense.get_humidity(),
			                  sense.get_temperature(),
			                  sense.get_pressure()
			                 )
			                 

		if connflag == True:
		#sense.show_message ('x')
			sense.clear(green) 
			mqttc.publish("$aws/things/" + deviceId + "/shadow/update", jmsg, qos=1)
			
			print("\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>") 
			pprint(json.loads(jmsg))
			print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n")

			sleep(0.1)
			sense.clear()
			sleep(pubFrequency-0.1)
		else:
			print("waiting for connection...")
			sleep(5)
			
except KeyboardInterrupt:
	print("Keyboard Interrupt detected: Quitting:")
	exit(1)
