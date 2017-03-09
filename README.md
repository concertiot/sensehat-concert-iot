#  Sense HAT to Concert IoT
Register a Sense HAT device on the Concert IoT platform and publish the sensor readings to it.

### Prerequisites
Concert IoT stack should be available with the Sense Hat device type created.

## Instructions

Clone this repo onto the Sense HAT raspberry pi

### Configuration

The URLs and the device type id should be configured in the config.py file, e.g.

     authUrl = 'https://sso.concert.iotpdev.com/auth/realms/myRealm/protocol/openid-connect/token'
     devicesUrl='https://api.concert.iotpdev.com/api/1/devices'
     deviceTypeId='b5a9078d-3651-4c45-84c7-f3aad60962d1'
### Register Sense HAT
    python register.py

Enter Concert IoT credentials and a name for the new device.
Note the default URLs and device type ID can be configured in config.py

### Publish Sensor Readings to Concert IoT
    python publish.py

Enter the publishing frequency (in seconds) for the sensor readings when prompted (defaults to 10 seconds)
