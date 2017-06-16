concertURL = 'demo.concert-iot.com'
realm = 'authenticate'

authTokenAPI = '/auth/realms/' + realm +'/protocol/openid-connect/token'

devicesAPI = '/api/1/devices'
deviceSnapshotAPI = '/api/1/devices/snapshot'
deviceTypesAPI = '/api/1/device-types'
sensorTypesAPI = '/api/1/sensor-types'
accountsAPI = '/api/1/accounts'

APIUrl = 'https://api.' + concertURL

authUrl = 'https://sso.' + concertURL + authTokenAPI
devicesUrl= APIUrl + devicesAPI
deviceSnapshotUrl = APIUrl + deviceSnapshotAPI
deviceTypesUrl = APIUrl + deviceTypesAPI
sensorTypesUrl = APIUrl + sensorTypesAPI
accountsUrl = APIUrl + accountsAPI


deviceTypeName = 'Pi SenseHat Actuator'
accountName = 'Account 2'

