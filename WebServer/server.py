# Flask imports.
from flask import Flask, render_template
import datetime
import logging
from mainClass import *

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
conveyorPin = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(servoPin, GPIO.OUT)
GPIO.setup(servoPinTwo, GPIO.OUT)
GPIO.setup(photoresistorPin, GPIO.IN)
# GPIO.setup(conveyorPhotoresistorPin, GPIO.IN)
# GPIO.setup(converyorPin, GPIO.OUT)

p = GPIO.PWM(servoPin, 50) # GPIO 11 for PWM with 50Hz
p.start(2.5) # Initialization

p2 = GPIO.PWM(servoPinTwo, 50) # GPIO 7 for PWM with 50Hz
p2.start(2.5) # Initialization

cupsPerBox = 10
restTime = 1.5 # Seconds of rest for the servos.
restJawAngle = 6
engagedJawAngle = 1

stopThread = False



app = Flask(__name__)

@app.route("/")
def index():
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    templateData = {
      'title' : 'HELLO!',
      'time': timeString
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
    templateData = {
        'title' : 'HELLO!',
        'time': timeString
    }
    return render_template('index.html', **templateData)

def servo(self):
    try:
        while True:
            global stopThread
            if (stopThread):
                break
            p.ChangeDutyCycle(engagedJawAngle)
            p2.ChangeDutyCycle(restJawAngle)
            time.sleep(restTime)
            if (stopThread):
                break
            p.ChangeDutyCycle(restJawAngle)
            p2.ChangeDutyCycle(engagedJawAngle)
            time.sleep(restTime)
    except KeyboardInterrupt:
        pass
        # p.stop()
        # p2.stop()
        # GPIO.cleanup()

def photoresistor(self):
    counter = 0
    check = False
    wait = 0.075
    while True:
        if (GPIO.input(photoresistorPin) == GPIO.LOW):
            check = True
            time.sleep(wait)
        if ((GPIO.input(photoresistorPin) == GPIO.HIGH) and check == True):
            counter += 1
            print(f'Cup Number #{counter} Detected.')
            check = False
            time.sleep(wait)
        if (counter >= cupsPerBox):
            counter = 0
            incrementBox()


servoThread = threading.Thread(target=servo, args=())
photoresistorThread = threading.Thread(target=photoresistor, args=())

def incrementBox(self):
    print("Stopping Servos...")
    global stopThread
    stopThread = True # Flag to stop the servos.
    print("Servos stopped. Incrementing Conveyor...")
    time.sleep(2)
    print("Starting up servos...")    
    stopThread = False # Allow thge servos to continue running.
    servoThread = threading.Thread(target=servo, args=())
    servoThread.start()
    print ("Servos back online!")

def main(self):
    servoThread.start()
    photoresistorThread.start()

main()