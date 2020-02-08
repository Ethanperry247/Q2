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

cupsPerBox = 40
restTime = 0.25 # Seconds of rest.
restJawAngle = 6
engagedJawAngle = 1


def servo():
    try:
        while True:
            p.ChangeDutyCycle(engagedJawAngle)
            p2.ChangeDutyCycle(restJawAngle)
            time.sleep(1.5)
            p.ChangeDutyCycle(restJawAngle)
            p2.ChangeDutyCycle(engagedJawAngle)
            time.sleep(1.5)
    except KeyboardInterrupt:
        p.stop()
        p2.stop()
        GPIO.cleanup()

def photoresistor():
    counter = 0
    check = False
    wait = 0.05
    while True:
        if (GPIO.input(photoresistorPin) == GPIO.LOW):
            check = True
            time.sleep(wait)
        if ((GPIO.input(photoresistorPin) == GPIO.HIGH)):
            counter += 1
            print(f'Cup Number #{counter} Detected.')
            check = False
            time.sleep(wait)
        if (counter >= cupsPerBox):
            counter = 0
            incrementBox()

def incrementBox():
    pass

def main():
    servoThread = threading.Thread(target=servo, args=())
    photoresistorThread = threading.Thread(target=photoresistor, args=())

    servoThread.start()
    photoresistorThread.start()



main()
