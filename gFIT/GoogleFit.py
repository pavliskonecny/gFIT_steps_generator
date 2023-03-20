import requests
import json
import time
import datetime
from typing import Tuple
from gFIT.GoogleFitAuth import GoogleFitAuth


class GoogleFit:

    def __init__(self, client_secret_file: dict, refresh_token: str):
        # client_secret_file -> Credentials from the Google Developers Console
        access_token = GoogleFitAuth.get_access_token(client_secret_file, refresh_token)
        if not access_token.startswith("ya29."):
            raise Exception(f"It wasn't possible to get access token:\n{access_token}")
        self._ACCESS_TOKEN = access_token

        # get data stream id
        ok, data_stream_id = self._get_data_stream_id()
        if not ok:
            raise Exception(f"It wasn't possible to get data stream id:\n{data_stream_id}")
        self._DATA_STREAM_ID = data_stream_id

    @staticmethod
    def get_refresh_token(client_secret_file_name: str):
        """
        Refresh token makes sense to get only one time. Then store it and later change it for Access token.
        In case you change some SCOPE you need new token.
        :return: Refresh token for Google Fit API
        """
        refresh_token = GoogleFitAuth.get_refresh_token(client_secret_file_name)
        return refresh_token

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
            "Authorization": f"Bearer {self._ACCESS_TOKEN}",
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

        url = f"https://www.googleapis.com/fitness/v1/users/me/dataSources/{self._DATA_STREAM_ID}/datasets/{start_time_milli}-{end_time_milli}"

        headers = {
            "Authorization": f"Bearer {self._ACCESS_TOKEN}",
            "Content-Type": "application/json;encoding=utf-8"
        }

        data = {
            "dataSourceId": self._DATA_STREAM_ID,
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
        if not response.ok:
            raise Exception(f"Not possible to set steps - response NOK\n{response.text}")
        if not ("point" in response.json()) or response.json()["point"][0]["value"][0]["intVal"] != steps:
            raise Exception(f"Not possible to set steps - wrong result\n{response.text}")
        return response.json()  # return json.loads(response.text)

    def _get_data_stream_id(self) -> Tuple[bool, str]:
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
            "Authorization": f"Bearer {self._ACCESS_TOKEN}",
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
