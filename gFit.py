"""
To start playing with Google Fit API visit: https://developers.google.com/fit/rest/v1/get-started
"""
from google_auth_oauthlib.flow import InstalledAppFlow


class _gFitAuth:
    # Additional scopes to apply when generating the refresh token
    # Check all available scopes at https://developers.google.com/fit/rest/v1/reference/users/dataSources/datasets/get
    _SCOPES = "https://www.googleapis.com/auth/fitness.activity.read",\
        "https://www.googleapis.com/auth/fitness.location.read", \
        "https://www.googleapis.com/auth/fitness.body.read",\
        "https://www.googleapis.com/auth/fitness.activity.write"

    @staticmethod
    def get_tokens_old(oauth_client_id, oauth_client_secret):
        """
        Method to get Access + Refresh token. It makes sense only one time. Then store the token for reconnection.
        In case you change some SCOPE you need new tokens.
        :return: Refresh token and Refresh token for Google Fit API
        """
        client_config = {
            "installed": {
                "client_id": oauth_client_id,
                "client_secret": oauth_client_secret,
                "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token"
            }
        }
        flow = InstalledAppFlow.from_client_config(client_config, _gFitAuth._SCOPES)
        flow.run_local_server(host='localhost', port=8080,
                              authorization_prompt_message='Please visit this URL: {url}',
                              success_message='The auth flow is complete; you may close this window.',
                              open_browser=False)

        print("Access token: %s" % flow.credentials.token)
        refresh_token = flow.credentials.refresh_token
        print('\033[94m' + "GOOGLE FIT API REFRESH TOKEN: %s" % refresh_token + '\033[0m')
        return refresh_token

    @staticmethod
    def get_refresh_token(client_secret_file_name: str):
        """
        Refresh token makes sense to get only one time. Then store it and later change it for Access token.
        In case you change some SCOPE you need new token.
        :return: Refresh token for Google Fit API
        """
        flow = InstalledAppFlow.from_client_secrets_file(client_secret_file_name, _gFitAuth._SCOPES)
        credentials = flow.run_local_server(host='localhost',
                                            port=8080,
                                            authorization_prompt_message='Please visit this URL: {url}',
                                            success_message='The auth flow is complete; you may close this window.',
                                            open_browser=False)
        access_token = credentials.token  # also in flow.credentials.token
        refresh_token = credentials.refresh_token  # also in flow.credentials.refresh_token
        print(f"\033[94m GOOGLE FIT API REFRESH TOKEN: {refresh_token} \033[0m")
        return refresh_token


import requests
import json
import time
import datetime
import others.my_files as my_files
from typing import Tuple


class GoogleFit:
    _CLIENT_ID = ""
    _CLIENT_SECRET = ""
    _REFRESH_TOKEN = ""

    def __init__(self, client_secret_file_name: str, refresh_token: str):
        # Credentials from the Google Developers Console
        sec_file = json.loads(my_files.read_file(client_secret_file_name))
        self._CLIENT_ID = sec_file["installed"]["client_id"]
        self._CLIENT_SECRET = sec_file["installed"]["client_secret"]
        self._REFRESH_TOKEN = refresh_token

    def _get_access_token(self):
        """
        This function creates a new Access Token using the Refresh Token
        and also refreshes the ID Token (see comment below).
        :return: Access Token
        """
        url = "https://www.googleapis.com/oauth2/v4/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": self._CLIENT_ID,
            "client_secret": self._CLIENT_SECRET,
            "refresh_token": self._REFRESH_TOKEN
        }

        response = requests.post(url, data=data)

        if response.ok:
            return response.json()['access_token']
        else:
            return None

    def get_steps(self, start_time: datetime, end_time: datetime) -> dict:
        """
            Available dataType are at: https://developers.google.com/fit/datatypes/activity
            for better results for steps you can replace dataSourceId by:
            derived:com.google.step_count.delta:com.google.android.gms:merge_step_deltas
            Also somebody recommend to remove value and key "dataSourceID".
            To specify the request visit: https://developers.google.com/fit/rest/v1/reference/users/dataset/aggregate
        """
        url = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json;encoding=utf-8"
        }

        data = {
            "aggregateBy": [
                {
                    "dataTypeName": "com.google.step_count.delta",  # steps
                    "dataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
                },
            ],
            "bucketByTime": {"durationMillis": 86400000},  # it is one day exactly
            "startTimeMillis": GoogleFit.human_to_milli(start_time),
            "endTimeMillis": GoogleFit.human_to_milli(end_time)
        }

        response = requests.post(url, data=json.dumps(data), headers=headers)
        return response.json()  # return json.loads(response.text)

    def set_steps(self, start_time: datetime, end_time: datetime, steps: int) -> dict:
        """
            Example is at: https://developers.google.com/fit/rest/v1/datasets
        :param start_time:
        :param end_time:
        :param steps:
        :return:
        """
        start_time_milli = GoogleFit.human_to_milli(start_time)
        end_time_milli = GoogleFit.human_to_milli(end_time)
        one_mill = 1000000

        ok, data_stream_id = self.get_data_stream_id()
        if not ok:
            raise Exception(f"Not possible to get data stream id:\n{data_stream_id}")

        url = f"https://www.googleapis.com/fitness/v1/users/me/dataSources/{data_stream_id}/datasets/{start_time_milli}-{end_time_milli}"

        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json;encoding=utf-8"
        }

        data = {
            "dataSourceId": data_stream_id,
            "maxEndTimeNs": end_time_milli * one_mill,
            "minStartTimeNs": start_time_milli * one_mill,
            "point": [
                {
                    "dataTypeName": "com.google.step_count.delta",
                    "endTimeNanos": end_time_milli * one_mill,
                    "originDataSourceId": "",
                    "startTimeNanos": start_time_milli * one_mill,
                    "value": [
                        {
                            "intVal": steps
                        }
                    ]
                }
            ]
        }

        response = requests.patch(url, data=json.dumps(data), headers=headers)
        return response.json()  # return json.loads(response.text)

    def get_data_stream_id(self) -> Tuple[bool, str]:
        """
            data_stream_id example:
            "derived:com.google.step_count.delta:1099052750196:Example Manufacturer:ExampleTablet:1000001:MyDataSource"
        :return:
        """
        data = self._create_data_source()

        # source was created, get stream ID
        if "dataStreamId" in data:
            return True, data["dataStreamId"]
        # data source already exists
        elif "error" in data:
            if "code" in data["error"] and data["error"]["code"] == 409:
                if "status" in data["error"] and data["error"]["status"] == "ALREADY_EXISTS":
                    stream_id = str(data["error"]["message"])
                    stream_id = stream_id.removeprefix("Data Source: ")
                    stream_id = stream_id.removesuffix(" already exists")
                    return True, stream_id
        else:
            return False, str(data)

    def _create_data_source(self) -> dict:
        """
            Example is at: https://developers.google.com/fit/rest/v1/data-sources
        :return:
        """
        url = "https://www.googleapis.com/fitness/v1/users/me/dataSources"
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json;encoding=utf-8"
        }

        data = {
          "dataStreamName": "MyDataSource",
          "type": "derived",
          "application": {
            "detailsUrl": "http://example.com",
            "name": "gFit stepper",
            "version": "1"
          },
          "dataType": {
            "field": [
              {
                "name": "steps",
                "format": "integer"
              }
            ],
            "name": "com.google.step_count.delta"
          },
          "device": {
            "manufacturer": "Pavlis",
            "model": "gFit stepper",
            "type": "tablet",
            "uid": "1000001",
            "version": "1.0"
          }
        }

        response = requests.post(url, data=json.dumps(data), headers=headers)
        return response.json()  # return json.loads(response.text)

    @staticmethod
    def get_refresh_token(client_secret_file_name: str):
        """
        Refresh token makes sense to get only one time. Then store it and later change it for Access token.
        In case you change some SCOPE you need new token.
        :return: Refresh token for Google Fit API
        """
        refresh_token = _gFitAuth.get_refresh_token(client_secret_file_name)
        return refresh_token

    @staticmethod
    def human_to_milli(date_time):
        """
        Convert human-readable time to milliseconds.
        """
        return int(time.mktime(date_time.timetuple()) * 1000)

    @staticmethod
    def milli_to_human(duration_in_ms: int):
        """
        Convert human-readable time to milliseconds.
        """
        return datetime.datetime.fromtimestamp(duration_in_ms / 1000.0).strftime('%D %H:%M:%S.%f')[:-3]
