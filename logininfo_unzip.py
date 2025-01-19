import sys
from zipfile import ZipFile as z
import os

sys.stdout.reconfigure(encoding='utf-8')

chat_pass = os.getenv("PASSWORD")

cwd = os.getcwd()

filename = cwd + "/logininfo.zip"
print("FILE TO DECRYPT: " + filename)

zf = z(filename)
zf.extractall(pwd=bytes(chat_pass, "utf-8"))

print("DECRYPTED: " + filename)