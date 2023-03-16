from gFit import GoogleFit
from datetime import datetime, timedelta
import json
import others.my_files as my_files
import random
from others.ColoredCommandLine import ColoredCommandLine as Ccl

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
    print(f"{Ccl.GREEN.value}*** gFIT steps generator was started ***{Ccl.WHITE.value}")

    # get refresh token
    if not my_files.exist_file(REFRESH_TOKEN_FILE):
        print("Getting access to Google Fit account ...")
        # Not necessary get refresh token every time. Just in case of reauthorization or change SCOPES
        gf_refresh_token = GoogleFit.get_refresh_token(CLIENT_SECRET_FILE)
        my_files.write_file(REFRESH_TOKEN_FILE, gf_refresh_token)
    else:
        gf_refresh_token = my_files.read_file(REFRESH_TOKEN_FILE)

    # get client secret file
    secret_file = json.loads(my_files.read_file(CLIENT_SECRET_FILE))

    print("Starting data transfer with Google Fit server ...")
    # create GoogleFit object and get access token
    gf = GoogleFit(secret_file, gf_refresh_token)

    # prepare actual date
    now = datetime.now()
    req_date = datetime(year=now.year, month=now.month, day=now.day, hour=5)
    if req_date >= now:
        req_date -= timedelta(days=1)

    # read steps
    # data = gf.get_steps(start_time=req_date, end_time=req_date + timedelta(hours=1))
    # write_data(data)

    # Generate steps for every day in this month
    print("Starting generating of steps ...")
    steps_total = 0
    while req_date.month == now.month:
        steps = random.randint(2500, 3000)
        steps_total += steps
        print(f"{Ccl.BLUE.value}Generating {steps} steps for date {req_date}")
        # gf.set_steps(start_time=req_date, end_time=req_date + timedelta(hours=1), steps=steps)
        req_date -= timedelta(days=1)

    # test only
    req_date = datetime(year=2022, month=9, day=1, hour=5)
    data = gf.set_steps(start_time=req_date, end_time=req_date + timedelta(hours=1), steps=1000)
    write_data(data)

    # Done
    print(f"\n{Ccl.GREEN.value}*** DONE ***")
    print(f"{steps_total} steps have been added in total :-)")
