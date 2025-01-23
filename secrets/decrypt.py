import sys
from zipfile import ZipFile as z
import os

sys.stdout.reconfigure(encoding='utf-8')

password = os.getenv("PASSWORD")

cwd = os.getcwd()

def decrypt_zip(filename, pwd):
    print("FILE TO DECRYPT: " + filename)
    zf = z(filename)
    zf.extractall(pwd=bytes(pwd, "utf-8"))
    print("DECRYPTED: " + filename)

decrypt_zip(cwd + "/secrets/one-time-code.zip", password)
decrypt_zip(cwd + "/secrets/logininfo.zip", password)