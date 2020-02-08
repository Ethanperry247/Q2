import RPi.GPIO as GPIO
import time
import threading

servoPin = 11
servoPinTwo = 7
photoresistorPin = 13
conveyorPhotoresistorPin = 15
conveyorPin = 12

GPIO.stemode(GPIO.BOARD)
GPIO.setup(servoPin, GPIO.OUT)
GPIO.setup(servoPinTwo, GPIO.OUT)
GPIO.setup(photoresistorPin, GPIO.IN)
GPIO.setup(conveyorPhotoresistorPin, GPIO.IN)
GPIO.setup(converyorPin, GPIO.OUT)

p = GPIO.PWM(servoPin, 50) # GPIO 17 for PWM with 50Hz
p.start(2.5) # Initialization

cupsPerBox = 40


def servo():
    try:
        while True:
            p.ChangeDutyCycle(4)
            time.sleep(0.1)
            p.ChangeDutyCycle(6)
            time.sleep(1)
    except KeyboardInterrupt:
        p.stop()
        GPIO.cleanup()

def photoresistor():
    counter = 0
    check = False
    wait = 0.05
    while True:
        if (GPIO.input(photoresistorPin) == GPIO.HIGH):
            check = True
            time.sleep(wait)
        if (GPIO.input(photoresistorPin) == GPIO.LOW):
            counter += 1
            print(f'Cup Number #{counter} Detected.')
            check = False
            time.sleep(wait)
        if (Counter >= cupsPerBox):
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