import sys
from zipfile import ZipFile as z
import os

sys.stdout.reconfigure(encoding='utf-8')

chat_pass = os.getenv("PASSWORD")

cwd = os.getcwd()

print("FILE TO DECRYPT: " + cwd + "/scoped_dir.zip")

zf = z(cwd + "/scoped_dir.zip")
zf.extractall(pwd=bytes(chat_pass, "utf-8"))

print("DECRYPTED: " + cwd + "/scoped_dir.zip")