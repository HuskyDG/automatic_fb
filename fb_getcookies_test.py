from fb_getcookies import get_fb_cookies
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
otp_secret = os.getenv("OTP_SECRET")
alt_account = os.getenv("ATL_ACC")
if alt_account == None or alt_account == "":
    alt_account = 0
else:
    alt_account = int(alt_account)

get_fb_cookies(username, password, otp_secret, alt_account)