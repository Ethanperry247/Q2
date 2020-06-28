# Flask imports.
from flask import Flask, render_template, request, redirect, url_for, session
import datetime
import logging
import csv
from hashlib import pbkdf2_hmac
from base64 import b64encode, b64decode

# Hardware sided imports.
# import RPi.GPIO as GPIO
import time
import threading

# Servos use 5 volts.
servoPin = 11
servoPinTwo = 7

# Photoresistors use 3.3 volts.
photoresistorPin = 13
conveyorPhotoresistorPin = 15

# Conveyor pin is a 3.3 volt logical output.
conveyorPin = 12

# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(servoPin, GPIO.OUT)
# GPIO.setup(servoPinTwo, GPIO.OUT)
# # GPIO.setup(photoresistorPin, GPIO.IN)
# # GPIO.setup(conveyorPhotoresistorPin, GPIO.IN)
# GPIO.setup(conveyorPin, GPIO.OUT)
# print ("Hardware Online.")

cupsPerBox = 10 # Cups to be loaded in each box before incrementing the conveyor.
restTime = 1.5 # Seconds of rest for the servos.
restJawAngle = 6 # Jaw angles. Keep the rest jaw to 6 and engaged jaw to 1 for best performance.
engagedJawAngle = 1

# Global Variables.
stopThread = False # Stops the servo thread.
counter = 0 # Global counter for the number of cups in the current box.
serverOnline = False # Designed to run the main method once.

app = Flask(__name__)
app.secret_key = '\x11>a\xebCh\xe2\xd2\xbe>\x87\rI\x07-\x8b'

# Web page loading.
###############################################################

# Server-wide orders. Will be sent via email each day at a specific time.
class Order:
    def __init__(self, type):
        super().__init__()
        self.type = type # Type of coffee being packaged for the order.
        self.number = 0 # Number of cups fulfilled in the order.
        now = datetime.datetime.now()
        self.startTime = now.strftime("%Y-%m-%d %H:%M") # Time at which this order began production.
        self.endTime = 0

    def end_order(self):
        now = datetime.datetime.now()
        self.endTime = now.strftime("%Y-%m-%d %H:%M")

class DailyOrders:
    def __init__(self):
        super().__init__()
        orders = list() # Server-wide list of cups.

    def add_order(self, type):
        # If there is an order, end the previous order and add a new order.
        if self.orders:
            self.orders[-1].end_order()
        order = Order(type) # creating an order will give it a start time.
        self.orders.append(order)

# User authentication.
def authenticate_password(credentials, password):

    # Pass the user entered password through encryption.
    key = pbkdf2_hmac(
        hash_name='sha256',
        password=password.encode('utf-8'),
        salt=b64decode(credentials[0]),
        iterations=100000,
        dklen=32
    )

    # Check the encrypted password against user credentials.
    if (b64encode(key).decode('utf-8') == credentials[1]):
        print("Authentic Login Credentials.")
        return True
    else:
        return False

def authenticate_user(username, password):
    
    # If the user passes in credentials which throw errors, recover and redirect.
    try:
        # Search through available passwords.
        with open('./passwords/passwords.csv', newline='') as file:
            credentials = dict()
            reader = csv.reader(file, delimiter=',')
            for line in reader:
                credentials[line[0]] = line[1:]
            
            # Check if the user entered a valid username.
            if (username in credentials):
                print("Login with Authentic Username.")

                # If so, use that username to check the user's given password against the system.
                if(authenticate_password(credentials[username], password)):
                    print(f'User: {username} has logged on to the system.')
                    # Log user onto a session.
                    # Session will be used throughout the user's login.
                    # Multiple users can therefore be allowed on the server at once. 
                    session["username"] = username 
                    return True
                else:
                     return False
            else:
                return False
    except RuntimeError as e:
        print(e)
        return False


@app.route("/")
def index():

    # Get the time on the server.
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")

    # Check if the user is already logged in.
    if 'username' in session:
        return redirect(url_for('login'))

    # If not, require a log in.
    else:
        templateData = {
        'title' : 'Please Login',
        'time': timeString
        }
        return render_template('index.html', **templateData)

@app.route("/login", methods=['POST', 'GET'])
def login():

    # Obtain the username and password of the user.
    username = ''
    password = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

    # Check if the user is already logged in.
    # If not, attempt to log the user in with entered credentials.
    if ('username' in session or authenticate_user(username, password)):
        user = session['username']
        types = [
            'Type 1',
            'Type 2',
            'Type 3'
        ]
        return render_template('login.html', types=types, user=user)
    else: # If user fails to enter valid credentials, redirect to the home page.
        return redirect(url_for('index'))


@app.route("/main", methods=['POST', 'GET'])
def main():
    # Check if the user is logged in, and redirect if they are not.
    if (not 'username' in session):
        return redirect(url_for('index'))

    # Get the type of coffee being packaged.
    if request.method == 'POST':
        type = request.form['type']
        user = session['username']
        return render_template('main.html', user=user)
    else:
        return render_template('invalid_request.html')

@app.route("/main/<action>")
def action(action):
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    if (action == 'ON'):
        print("Clicked on!")
    if (action == 'OFF'):
        print("Clicked Off!")
    if (action == 'PAUSE'):
        # pause()
        pass
    if (action == 'RESUME'):
        # resume()
        pass
    templateData = {
        'title' : 'HELLO!',
        'time': timeString
    }
    return render_template('main.html', **templateData)

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))
###############################################################



# Hardware sided code.
###############################################################
# if (not serverOnline):
#     p = GPIO.PWM(servoPin, 50) # GPIO 11 for PWM with 50Hz
#     p.start(2.5) # Initialization

#     p2 = GPIO.PWM(servoPinTwo, 50) # GPIO 7 for PWM with 50Hz
#     p2.start(2.5) # Initialization

# def servo():
#     print("Beginning servos...")    

#     try:
#         while True:
#             global stopThread # If a global thread stop is detected, shut down.
#             if (stopThread):
#                 break
#             p.ChangeDutyCycle(engagedJawAngle)
#             p2.ChangeDutyCycle(restJawAngle)
#             time.sleep(restTime) # Rest between the next cup release.
#             if (stopThread):
#                 break
#             p.ChangeDutyCycle(restJawAngle)
#             p2.ChangeDutyCycle(engagedJawAngle)
#             time.sleep(restTime) # Rest between the next cup release.
#     except KeyboardInterrupt:
#         p.stop() # Clean up.
#         p2.stop()

# def photoresistor():
#     global counter # Global counter updated in this method.
#     check = False
#     wait = 0.075 # Wait this much time for the cup to fall.
#     # Loop this block to detect falling cups.
#     while True:
#         if (GPIO.input(photoresistorPin) == GPIO.LOW):
#             check = True
#             time.sleep(wait)
#         if ((GPIO.input(photoresistorPin) == GPIO.HIGH) and check == True):
#             counter += 1
#             print(f'Cup Number #{counter} Detected.') # For debugging purposes, print # of cups.
#             check = False
#             time.sleep(wait)
#         if (counter >= cupsPerBox):
#             counter = 0
#             incrementBox()

# # If a box has reached its max number of cups, increment the conveyor. 
# def incrementBox():
#     print("Stopping Servos...")
#     global stopThread
#     stopThread = True # Flag to stop the servos.
#     print("Servos stopped. Incrementing Conveyor...")
#     time.sleep(2) # Wait for the conveyor to increment.
#     print("Starting up servos...")    
#     stopThread = False # Allow thge servos to continue running.
#     servoThread = threading.Thread(target=servo, args=()) # Start a new thred to get the servos running.
#     servoThread.start()
#     print ("Servos back online!")

# def pause():
#     global stopThread
#     stopThread = True # Flag to stop the servos.
#     print("Servos stopped.")

# def resume():
#     global stopThread
#     stopThread = False # Flag to start the servos.
#     servoThread = threading.Thread(target=servo, args=()) # Start a new thred to get the servos running.
#     servoThread.start()
#     print ("Servos back online!")

# # Called with the assumption that a filled box is in place.
# def signalConveyor():
#     newBoxFlag = False # True if a new box is in place.
#     noBox = False # True if no box is in place.
#     GPIO.output(conveyorPin, GPIO.HIGH) # Set the output voltage to 3.3 volts on the conveyor pin.
#     while (not newBoxFlag):
#         if (GPIO.input(conveyorPhotoresistorPin) == GPIO.HIGH and noBox):
#             GPIO.output(conveyorPin, GPIO.LOW) # Set the output voltage to 0 volts on the conveyor pin.
#             newBoxFlag = True
#         if (GPIO.input(conveyorPhotoresistorPin) == GPIO.LOW):
#             noBox = True

# # If a box is in place, then ignore. Otherwise, increment the conveyor until a new box is in place.
# def initialize():
#     newBoxFlag = False # True if a new box is in place.
#     if (GPIO.input(conveyorPhotoresistorPin) == GPIO.LOW):
#         GPIO.output(conveyorPin, GPIO.HIGH) # Set the output voltage to 3.3 volts on the conveyor pin.
#         while (not newBoxFlag):
#             if (GPIO.input(conveyorPhotoresistorPin) == GPIO.HIGH):
#                 GPIO.output(conveyorPin, GPIO.LOW) # Set the output voltage to 0 volts on the conveyor pin.
#                 newBoxFlag = True
            

# def main():
#     servoThread = threading.Thread(target=servo, args=())
#     photoresistorThread = threading.Thread(target=photoresistor, args=())
#     initialize()
#     servoThread.start()
#     photoresistorThread.start()

# # At the start of the server, run the main method once.
# if (not serverOnline):
#     main()
#     serverOnline = True
# ###############################################################
