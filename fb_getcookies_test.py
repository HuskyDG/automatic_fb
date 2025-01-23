from fb_getcookies import get_fb_cookies
import os
import sys
import json
import time

sys.stdout.reconfigure(encoding='utf-8')


if os.getenv("USE_ENV_SETUP") == "true":
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    otp_secret = os.getenv("OTP_SECRET")
    alt_account = os.getenv("ATL_ACC")
else:
    f = open("logininfo.json", "r")
    login_info = json.load(f)

    username = login_info["username"]
    password = login_info["password"]
    otp_secret = login_info["otp_sec"]
    alt_account = login_info["alt"]

if alt_account == None or alt_account == "":
    alt_account = 0
else:
    alt_account = int(alt_account)

filename = "cookies.json"
for i in range(5):
    cookies = get_fb_cookies(username, password, otp_secret, alt_account)
    if cookies == None:
        time.sleep(5)
        continue
    cookies_file = open(filename, "w")
    json.dump(cookies, cookies_file)
    cookies_file.close()
    break