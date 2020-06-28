import serial
import time
import threading

# Machine Codes:
# AC - Add Cup (Manually add a cup in the logic of the hardware)
# BC - Box Count (Change the box count from its default of 24)
# IC - Increment Conveyor (moves conveyor to the next box)
# RC - Run Conveyor (Moves the conveyor continuously)
# SC - Stop Conveyor (Steops the conveyor if it is moving)
# OC - Open Cover (Opens the cover by a quarter turn)
# CC - Close Cover (Closes the cover by a quarter turn)
# MC[+/-][steps] - (Moves the cover by forward or backward by the specified number of steps)
# CBC - Change Box Count (changes the number of cups which should be added to each box)

class Interface:

    def __init__(self, port, baud):
        super().__init__()
        self.com = serial.Serial(port, baud)
        time.sleep(1) # Give the device a moment to establish a connection.

    def send_message(self, message):
        self.com.write((message + "\n").encode())

    def listen(self) -> str:
        message = self.com.read(self.com.inWaiting())
        return message.decode("utf-8")

    def move_cover(self, steps):
        message = "MC"
        if (steps > 0):
            message += f'+{steps}'
        else:
            message += f'-{steps}'
        self.send_message(message)

    def increment_conveyor(self):
        self.send_message("IC")

    def run_conveyor(self):
        self.send_message("RC")
    
    def stop_conveyor(self):
        self.send_message("SC")

    def open_cover(self):
        self.send_message("OC")

    def close_cover(self):
        self.send_message("CC")

    def add_cup(self):
        self.send_message("AC")

    def change_box_count(self, count):
        self.send_message(f'CBC{count}')

stop_listener = False

# interface = Interface('COM3', 9600)
# def lets_listen():
#     global stop_listener
#     while (not stop_listener):
#         message = interface.listen()
#         if (message):
#             print(f'\n * Message from hardware controller: {message}')
#         time.sleep(0.2)

# listener = threading.Thread(target=lets_listen)
# listener.start()

# while True:
    # send = input('Enter: ')
    # interface.send_message(send)