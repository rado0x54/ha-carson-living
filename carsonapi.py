import json
import logging
import requests
import jwt
import time
import datetime

# from tuyaha.devices.factory import get_tuya_device

_LOGGER = logging.getLogger(__name__)

CARSON_API_VERSION = 'v1.4.0'
CARSON_API_URL = 'https://api.carson.live/api/{}'.format(CARSON_API_VERSION)

# every 12h
REFRESH_TIME = 60 * 60 * 12

RESPONSE_DATA_KEY = 'data'


class CarsonSession:
    username = ''
    password = ''
    accessToken = ''
    accessTokenPayload = None
    refreshToken = ''
    expireTime = 0
    doors = [],
    cameras = []


SESSION = CarsonSession()

TEST_TIME_SPEND = int(60 * 60 * 24 * 29.5)


class CarsonApi:

    def init(self, username, password):
        SESSION.username = username
        SESSION.password = password

        if not username or not password:
            _LOGGER.info('Username and Password not set')
            return None
        else:
            self.get_access_token()
            # self.discover_devices()
            # return SESSION.devices

    def set_access_token(self, accessToken):
        SESSION.accessToken = accessToken
        SESSION.accessTokenPayload = jwt.decode(accessToken, verify=False)
        # Epoch Time
        SESSION.expireTime = SESSION.accessTokenPayload.get('exp')
        _LOGGER.info('Updated access Token for ' + self.get_email())

    @staticmethod
    def get_email():
        return SESSION.accessTokenPayload.get('email', '<no mail found>')

    def get_access_token(self):
        if not SESSION.username or not SESSION.password:
            raise CarsonAPIException('Username or password missing.')

        _LOGGER.info('Getting access Token for ' + SESSION.username)
        response = requests.post(
            (CARSON_API_URL + '/auth/login/'),
            json={
                'username': SESSION.username,
                'password': SESSION.password,
            },
        )
        # Raise exceptions
        response.raise_for_status()
        self.set_access_token(response.json()[RESPONSE_DATA_KEY]['token'])

    def check_access_token(self):
        time_left = SESSION.expireTime - int(time.time())
        if SESSION.accessToken == '':
            self.get_access_token()
        elif time_left <= REFRESH_TIME:
            _LOGGER.info('Current AccessToken will expire in %s (less then %s)',
                         str(datetime.timedelta(seconds=time_left)),
                         str(datetime.timedelta(seconds=REFRESH_TIME)))
            self.get_access_token()
        else:
            _LOGGER.debug('Current Access Token does not need to be refreshed. %s left',
                          str(datetime.timedelta(seconds=time_left)))

    def poll_devices_update(self):
        self.check_access_token()
        return self.discover_devices()

    def discover_devices(self):
        _LOGGER.debug('Discovering Cameras and Doors for %s',
                      self.get_email())
        response = requests.get(CARSON_API_URL + '/me/',
                                headers={
                                    'Authorization': 'JWT ' + SESSION.accessToken
                                })
        try:
            response.raise_for_status();
        except requests.exceptions.HTTPError as e:
            _LOGGER.error('Failure while getting devices: ' + e)
            return None

        response_json = response.json()
        for properties in response_json[RESPONSE_DATA_KEY]['properties']:
            cameras = properties['cameras'];
            doors = properties['doors']

            print(cameras)
            print(doors)

            # Cameras
            for camera in cameras:
                print(camera)

            # Doors
            for door in doors:
                print(door)

    #
    # def get_devices_by_type(self, dev_type):
    #     device_list = []
    #     for device in SESSION.devices:
    #         if device.dev_type() == dev_type:
    #             device_list.append(device)
    #
    # def get_all_devices(self):
    #     return SESSION.devices
    #
    # def get_device_by_id(self, dev_id):
    #     for device in SESSION.devices:
    #         if device.object_id() == dev_id:
    #             return device
    #     return None
    #
    # def device_control(self, devId, action, param=None, namespace='control'):
    #     if param is None:
    #         param = {}
    #     response = self._request(action, namespace, devId, param)
    #     if response and response['header']['code'] == 'SUCCESS':
    #         success = True
    #     else:
    #         success = False
    #     return success,response
    #


class CarsonAPIException(Exception):
    pass
