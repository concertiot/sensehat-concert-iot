#  Sense HAT to Concert IoT
Register a Sense HAT device on the Concert IoT platform and publish the sensor readings to it.
Can also use the Pi to demonstrate actuator settings

### Prerequisites
Concert IoT stack should be available with the Sense Hat device type(s) created.
Ensure you have a user account on the Concert instance and belong to the relevant account type

## Instructions

Clone this repo onto the Sense HAT raspberry pi
The actuator_pub/py can be run from anywhere (move it to another machione that can run python3)

### Configuration

The URLs and the device type id should be configured in the config.py file

Should only need to set the main Url (eg.  "https://path.toConcert.com")
Also, provide the deviceTypeName and the account name to which this device belongs.

The apis and urls to be used are auto derived.

### Register Sense HAT
    python3 register.py

Enter Concert IoT credentials and a name for the new device.
Note the default URLs and device type ID can be configured in config.py

### Publish Sensor Readings to Concert IoT
    python3 publish.py

Enter the publishing frequency (in seconds) for the sensor readings when prompted (defaults to 10 seconds)

### Subscribe to Actuator readings
    python3 actuator_sub.py

Needs to run on the device in the same directory as the register.py script (it reads from a number of files created at registration)
This will listen for messages and act - sets a swtich to display a message on the LEDs

### Publish to Actuator readings
    python3 actuator_pub.py

Can be run from anywhere with a network connection.
Needs the config.py and awshost and deviceId files created at registration, so these need ot be in the same directory as the python script
Simple menu to read switch and message settings, and an ability to adjust these.

