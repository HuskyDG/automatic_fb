from fb_getcookies import get_fb_cookies
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
otp_secret = os.getenv("OTP_SECRET")

get_fb_cookies(username, password, otp_secret)