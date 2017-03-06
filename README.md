#  Sense HAT to Concert IoT
Register a Sense HAT device on the Concert IoT platform and publish the sensor readings to it.

Clone this repo onto the Sense HAT raspberry pi
## Register Sense HAT
    python register.py

Enter Concert IoT credentials and a name for the new device.
Note the default URLs and device type ID can be configured in config.py

## Publish Sensor Readings to Concert IoT
    python publish.py

Enter the publishing frequency (in seconds) for the sensor readings when prompted (defaults to 10 seconds)
