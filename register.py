#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  register.py
# 
# registers a device with Concert of a device type in the config.py file


import requests
import config
import getpass
from pprint import pprint



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
	                        
	print (response)
	
except requests.exceptions.ConnectionError as connErr:
	print("Connection Error: {0}".format(str(connErr)))
	exit(1)
except requests.exceptions.RequestException as e:
	print("Response Exception Raised on auth URL: {0}".format(str(e)))
	print("Address exception: Quitting")
	exit(1)

keycloak = response.json()
access_token = keycloak['access_token']

deviceHeader = {"Authorization" : "Bearer " + access_token, 
                "Content-Type" : "application/json"}

deviceName = input("Name for new device: ")

try:

	createResponse = requests.post(config.devicesUrl, 
	                               headers = deviceHeader, 
	                               json = {"name": deviceName,
	                                       "typeId": config.deviceTypeId,
	                                       "description": "Raspberry Pi with SenseHat",
	                                       "attributes": {},
	                                       "location": {"longitude": -5.918212,
	                                                    "latitude": 54.606314
	                                                    }
	                                      }
	                              )

except requests.exceptions.RequestException as e:
	print("Response Exception Raised on device URL: {0}".format(str(e)))
	print("Address Exception: Quitting")
	exit(0)
	
createdDevice = createResponse.json()

print ("----------------------")
print ("Concert Device Created")
print ("----------------------")
print ("Name      : {0}".format(createdDevice['name']))
print ("ID        : {0}".format(createdDevice['id']))
print ("Cloud URN : {0}".format(createdDevice['cloudUrn']))
print ("----------------------")

deviceId = createdDevice['id']

fileName = 'deviceId'
f = open(fileName, 'w')
f.write(deviceId)
f.close()

fileName = deviceId + '.private.key'
f = open(fileName, 'w')
f.write(createdDevice['privateKey'])
f.close()

fileName = deviceId + '.cert.pem'
f = open(fileName, 'w')
f.write(createdDevice['certificate'])
f.close()

fileName = deviceId + '.public.key'
f = open(fileName, 'w')
f.write(createdDevice['publicKey'])
f.close()

