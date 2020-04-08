# Flask imports.
from flask import Flask, render_template
import datetime
import logging
# from mainClass import *

# Hardware sided imports.
import RPi.GPIO as GPIO
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

GPIO.setmode(GPIO.BOARD)
GPIO.setup(servoPin, GPIO.OUT)
GPIO.setup(servoPinTwo, GPIO.OUT)
# GPIO.setup(photoresistorPin, GPIO.IN)
# GPIO.setup(conveyorPhotoresistorPin, GPIO.IN)
GPIO.setup(conveyorPin, GPIO.OUT)
print ("Hardware Online.")

cupsPerBox = 10 # Cups to be loaded in each box before incrementing the conveyor.
restTime = 1.5 # Seconds of rest for the servos.
restJawAngle = 6 # Jaw angles. Keep the rest jaw to 6 and engaged jaw to 1 for best performance.
engagedJawAngle = 1

# Global Variables.
stopThread = False # Stops the servo thread.
counter = 0 # Global counter for the number of cups in the current box.
serverOnline = False # Designed to run the main method once.

app = Flask(__name__)

# Web page loading.
###############################################################
@app.route("/")
def index():
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    global counter
    templateData = {
      'title' : 'HELLO!',
      'time': timeString,
      'cups': counter
      }
    return render_template('index.html', **templateData)

@app.route("/<action>")
def action(action):
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    if (action == 'ON'):
        print("Clicked on!")
    if (action == 'OFF'):
        print("Clicked Off!")
    if (action == 'PAUSE'):
        pause()
    if (action == 'RESUME'):
        resume()
    templateData = {
        'title' : 'HELLO!',
        'time': timeString
    }
    return render_template('index.html', **templateData)
###############################################################

# Hardware sided code.
###############################################################
if (not serverOnline):
    p = GPIO.PWM(servoPin, 50) # GPIO 11 for PWM with 50Hz
    p.start(2.5) # Initialization

    p2 = GPIO.PWM(servoPinTwo, 50) # GPIO 7 for PWM with 50Hz
    p2.start(2.5) # Initialization

def servo():
    print("Beginning servos...")    

    try:
        while True:
            global stopThread # If a global thread stop is detected, shut down.
            if (stopThread):
                break
            p.ChangeDutyCycle(engagedJawAngle)
            p2.ChangeDutyCycle(restJawAngle)
            time.sleep(restTime) # Rest between the next cup release.
            if (stopThread):
                break
            p.ChangeDutyCycle(restJawAngle)
            p2.ChangeDutyCycle(engagedJawAngle)
            time.sleep(restTime) # Rest between the next cup release.
    except KeyboardInterrupt:
        p.stop() # Clean up.
        p2.stop()

def photoresistor():
    global counter # Global counter updated in this method.
    check = False
    wait = 0.075 # Wait this much time for the cup to fall.
    # Loop this block to detect falling cups.
    while True:
        if (GPIO.input(photoresistorPin) == GPIO.LOW):
            check = True
            time.sleep(wait)
        if ((GPIO.input(photoresistorPin) == GPIO.HIGH) and check == True):
            counter += 1
            print(f'Cup Number #{counter} Detected.') # For debugging purposes, print # of cups.
            check = False
            time.sleep(wait)
        if (counter >= cupsPerBox):
            counter = 0
            incrementBox()

# If a box has reached its max number of cups, increment the conveyor. 
def incrementBox():
    print("Stopping Servos...")
    global stopThread
    stopThread = True # Flag to stop the servos.
    print("Servos stopped. Incrementing Conveyor...")
    time.sleep(2) # Wait for the conveyor to increment.
    print("Starting up servos...")    
    stopThread = False # Allow thge servos to continue running.
    servoThread = threading.Thread(target=servo, args=()) # Start a new thred to get the servos running.
    servoThread.start()
    print ("Servos back online!")

def pause():
    global stopThread
    stopThread = True # Flag to stop the servos.
    print("Servos stopped.")

def resume():
    global stopThread
    stopThread = False # Flag to start the servos.
    servoThread = threading.Thread(target=servo, args=()) # Start a new thred to get the servos running.
    servoThread.start()
    print ("Servos back online!")

# Called with the assumption that a filled box is in place.
def signalConveyor():
    newBoxFlag = False # True if a new box is in place.
    noBox = False # True if no box is in place.
    GPIO.output(conveyorPin, GPIO.HIGH) # Set the output voltage to 3.3 volts on the conveyor pin.
    while (not newBoxFlag):
        if (GPIO.input(conveyorPhotoresistorPin) == GPIO.HIGH and noBox):
            GPIO.output(conveyorPin, GPIO.LOW) # Set the output voltage to 0 volts on the conveyor pin.
            newBoxFlag = True
        if (GPIO.input(conveyorPhotoresistorPin) == GPIO.LOW):
            noBox = True

# If a box is in place, then ignore. Otherwise, increment the conveyor until a new box is in place.
def initialize():
    newBoxFlag = False # True if a new box is in place.
    if (GPIO.input(conveyorPhotoresistorPin) == GPIO.LOW):
        GPIO.output(conveyorPin, GPIO.HIGH) # Set the output voltage to 3.3 volts on the conveyor pin.
        while (not newBoxFlag):
            if (GPIO.input(conveyorPhotoresistorPin) == GPIO.HIGH):
                GPIO.output(conveyorPin, GPIO.LOW) # Set the output voltage to 0 volts on the conveyor pin.
                newBoxFlag = True
            

def main():
    servoThread = threading.Thread(target=servo, args=())
    photoresistorThread = threading.Thread(target=photoresistor, args=())
    initialize()
    servoThread.start()
    photoresistorThread.start()

# At the start of the server, run the main method once.
if (not serverOnline):
    main()
    serverOnline = True
###############################################################
