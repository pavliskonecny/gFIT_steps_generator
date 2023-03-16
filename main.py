from gFit import GoogleFit
from datetime import datetime
import json
import others.my_files as my_files
import random
from others.ColoredCommandLine import ColoredCommandLine as ccl

# Get client_secret file from google API console at: https://console.developers.google.com/apis/credentials
# Get refresh token from method GoogleFit.get_refresh_token(CLIENT_SECRET_FILE)
CLIENT_SECRET_FILE = "auth/client_secret.json"
REFRESH_TOKEN_FILE = "auth/refresh_token.txt"


def write_data(data=None):
    j_son = json.dumps(data, ensure_ascii=False, indent=2)
    name = "data.json"
    with open(name, mode='w') as outfile:
        print(j_son, file=outfile)


if __name__ == "__main__":
    print("Getting access to Google Fit account ...")
    # get refresh token
    if not my_files.exist_file(REFRESH_TOKEN_FILE):
        # Not necessary get refresh token every time. Just in case of reauthorization or change SCOPES
        gf_refresh_token = GoogleFit.get_refresh_token(CLIENT_SECRET_FILE)
        my_files.write_file(REFRESH_TOKEN_FILE, gf_refresh_token)
    else:
        gf_refresh_token = my_files.read_file(REFRESH_TOKEN_FILE)

    gf = GoogleFit(CLIENT_SECRET_FILE, gf_refresh_token)

    print("Starting data transfer with Google Fit server ...\n")
    start_time = datetime(year=2022, month=9, day=1, hour=5)
    end_time = datetime(year=2022, month=9, day=1, hour=6)
    steps = random.randint(2500, 3000)

    # print("Reading steps ...")
    # data = gf.get_steps(start_time=start_time, end_time=end_time)

    print(f"{ccl.YELLOW.value}Generating {steps} steps for date {start_time}")
    data = gf.set_steps(start_time=start_time, end_time=end_time, steps=steps)
    write_data(data)

    print(f"\n{ccl.BLUE.value} *** DONE ***")
