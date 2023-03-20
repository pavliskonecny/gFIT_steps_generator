from gFIT.GoogleFit import GoogleFit
from datetime import datetime, timedelta
import json
from mytoolbox import my_files
import random
from colorama import init as colorama_init, Fore

# Get client_secret file from google API console at: https://console.developers.google.com/apis/credentials
# Get refresh token from method GoogleFit.get_refresh_token(CLIENT_SECRET_FILE)
CLIENT_SECRET_FILE = f"{my_files.get_internal_path()}\\gFIT\\client_secret.json"
REFRESH_TOKEN_FILE = f"{my_files.get_external_path()}\\refresh_token.txt"

if __name__ == "__main__":
    colorama_init()
    print(f"{Fore.GREEN}*** gFIT steps generator was started ***{Fore.RESET}")

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
    # create GoogleFit object and get access token + data stream id
    gf = GoogleFit(secret_file, gf_refresh_token)

    # prepare actual date
    now = datetime.now()
    req_date = datetime(year=now.year, month=now.month, day=now.day, hour=5)
    if req_date >= now:
        req_date -= timedelta(days=1)

    # Generate steps for every day in this month
    print("Starting generating of steps ...\n")
    steps_total = 0
    while req_date.month == now.month:
        steps = random.randint(2500, 3100)
        steps_total += steps
        print(f"{Fore.LIGHTBLUE_EX}Generating {steps} steps for date {req_date}")
        gf.set_steps(start_time=req_date, end_time=req_date + timedelta(hours=1), steps=steps)
        req_date -= timedelta(days=1)

    # Done
    print(f"\n{Fore.GREEN}*** DONE ***\n{steps_total} steps have been added in total :-){Fore.RESET}")
    input("Press Enter to EXIT")

    # TEST ONLY
    # req_date = datetime(year=2022, month=8, day=1, hour=5)
    # data = gf.get_steps(start_time=req_date, end_time=req_date + timedelta(hours=1))  # read steps
    # data = gf.set_steps(start_time=req_date, end_time=req_date + timedelta(hours=1), steps=2000)  # write steps
    # my_files.write_json("data.json", data)