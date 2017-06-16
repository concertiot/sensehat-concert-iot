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
import json

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

deviceName = input("Name for new device: ")

"""
Get the type ID for the device type as named in config.py file
"""
try:
	deviceTypeResp = requests.get(config.deviceTypesUrl,
	                             headers = deviceHeader)

	checkStatusCode(deviceTypeResp.status_code,config.deviceTypesUrl)         
	                             
except requests.exceptions.ConnectionError as connErr:
	print("Connection Error: {0}".format(str(connErr)))
	exit(1)
except requests.exceptions.RequestException as e:
	print("Response Exception Raised on device Types URL: {0}".format(str(e)))
	print("Address exception: Quitting")
	exit(1)


typeId = ''
for d in deviceTypeResp.json():
	print("d: {0}".format(d))
	if d["name"] == config.deviceTypeName:
		typeId = d["id"]
		break

if d == '':
	print("Your type name {0} does not exist: existing".format(config.deviceTypeName))
	exit(1)

"""
Get the account ID for the account as named in config.py file
"""
try:
	accountTypeResp = requests.get(config.accountsUrl,
	                             headers = deviceHeader)
	                             
	checkStatusCode(accountTypeResp.status_code,config.accountsUrl)         
	                       
except requests.exceptions.ConnectionError as connErr:
	print("Connection Error: {0}".format(str(connErr)))
	exit(1)
except requests.exceptions.RequestException as e:
	print("Response Exception Raised on accounts URL: {0}".format(str(e)))
	print("Address exception: Quitting")
	exit(1)

accountId = ''
for a in accountTypeResp.json():
	if a['name'] == config.accountName:
		ownerId = a['id']
		break

if a == '':
	print("Your account name {0} does not exist: existing".format(config.accountName))
	exit(1)
	                             
"""
Register and create the device - get keys and certs and write to file for publish
"""
try:

	createResponse = requests.post(config.devicesUrl, 
	                               headers = deviceHeader, 
	                               json = {"name": deviceName,
	                                       "typeId": typeId,
	                                       "description": "Registered Instance: " + config.deviceTypeName,
	                                       "owner": ownerId,
	                                       "attributes": {},
	                                       "location": {"longitude": -5.918212,
	                                                    "latitude": 54.606314
	                                                    }
	                                      }
	                              )
	                              
	checkStatusCode(createResponse.status_code,config.devicesUrl)         
   
except requests.exceptions.RequestException as e:
	print("Response Exception Raised on device URL: {0}".format(str(e)))
	print("Address Exception: Quitting")
	exit(0)


# print(createResponse.headers())



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

fileName = 'awsHost'
f = open(fileName,'w')
f.write(createdDevice['mqtt']['host'])
f.close()

fileName = deviceId + '.private.key'
f = open(fileName, 'w')
f.write(createdDevice['mqtt']['privateKey'])
f.close()

fileName = deviceId + '.cert.pem'
f = open(fileName, 'w')
f.write(createdDevice['mqtt']['certificate'])
f.close()

fileName = deviceId + '.public.key'
f = open(fileName, 'w')
f.write(createdDevice['mqtt']['publicKey'])
f.close()
