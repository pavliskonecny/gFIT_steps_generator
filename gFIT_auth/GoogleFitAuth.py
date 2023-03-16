from google_auth_oauthlib.flow import InstalledAppFlow
import requests


class GoogleFitAuth:
    """
    To start playing with Google Fit API visit: https://developers.google.com/fit/rest/v1/get-started
    """
    # Additional scopes to apply when generating the refresh token
    # Check all available scopes at https://developers.google.com/fit/rest/v1/reference/users/dataSources/datasets/get
    _SCOPES = "https://www.googleapis.com/auth/fitness.activity.read", \
        "https://www.googleapis.com/auth/fitness.location.read", \
        "https://www.googleapis.com/auth/fitness.body.read", \
        "https://www.googleapis.com/auth/fitness.activity.write"

    @staticmethod
    def get_refresh_token_old(oauth_client_id, oauth_client_secret):
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
        flow = InstalledAppFlow.from_client_config(client_config, GoogleFitAuth._SCOPES)
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
        flow = InstalledAppFlow.from_client_secrets_file(client_secret_file_name, GoogleFitAuth._SCOPES)
        credentials = flow.run_local_server(host='localhost',
                                            port=8080,
                                            authorization_prompt_message='Please visit this URL: {url}',
                                            success_message='The auth flow is complete, you may close this window.',
                                            open_browser=False)
        access_token = credentials.token  # also in flow.credentials.token
        refresh_token = credentials.refresh_token  # also in flow.credentials.refresh_token
        print(f"\033[94m GOOGLE FIT API REFRESH TOKEN: {refresh_token} \033[0m")
        return refresh_token

    @staticmethod
    def get_access_token(client_secret_file: dict, refresh_token) -> str:
        """
        This function creates a new Access Token using the Refresh Token
        :return: Access Token
        """
        url = "https://www.googleapis.com/oauth2/v4/token"
        client_id = client_secret_file["installed"]["client_id"],
        client_secret = client_secret_file["installed"]["client_secret"],

        data = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token
        }

        response = requests.post(url, data=data)

        if response.ok:
            return response.json()['access_token']
        else:
            return response.text
