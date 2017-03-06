import requests
import config

authHeaders = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}

userName = raw_input("Concert username[iotpadminuser]: ") or "iotpadminuser"
password = raw_input("Concert password: ")

response = requests.post(config.authUrl, headers = authHeaders, data = {"client_id" : "ui", "username" : userName,"password" : password, "grant_type" : "password"})
keycloak = response.json()
access_token = keycloak['access_token']

deviceHeader = {"Authorization" : "Bearer " + access_token, "Content-Type" : "application/json"}

deviceName = raw_input("Name for new device: ")

createResponse = requests.post(config.devicesUrl, headers = deviceHeader, json = {"name" : deviceName, "typeId" : config.deviceTypeId})

createdDevice = createResponse.json()

print "----------------------"
print "Concert Device Created"
print "----------------------"
print "Name      : %s" % createdDevice['name']
print "ID        : %s" % createdDevice['id']
print "Cloud URN : %s" % createdDevice['cloudUrn']
print "----------------------"

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

