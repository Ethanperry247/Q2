# Import for password hasing.
from hashlib import pbkdf2_hmac

# OS import for salting.
import os
from base64 import b64encode, b64decode

# Password entering.
import getpass

# Writing to the password file.
import csv

salt = os.urandom(32)

username = input("Please enter your username: ")
password = getpass.getpass("Please enter your password: ")

key = pbkdf2_hmac(
    hash_name='sha256',
    password=password.encode('utf-8'),
    salt=salt,
    iterations=100000,
    dklen=32
)

with open('./kcup-quality-control-mechanism/Webserver/passwords/passwords.csv', 'a') as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerow([username, b64encode(salt).decode('utf-8'), b64encode(key).decode('utf-8')])

print("Password encrypted and saved.")