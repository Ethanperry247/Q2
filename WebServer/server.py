# Flask imports.
from flask import Flask, render_template, request, redirect, url_for, session
import datetime
import logging
import csv
from hashlib import pbkdf2_hmac
from base64 import b64encode, b64decode
from datetime import datetime, timedelta
import threading
import time
from email_server import EmailServer
from orders import DailyOrders, OrderManager
import json as JSON
from hardware_interface import Interface

# Daily orders and order manager are used to keep track of cups produced throughout the day.
daily_orders = DailyOrders()
order_manager = OrderManager()
interface = Interface('COM3', 9600)

# A global variable used for shutting down the email messenger. 
stop_messenger = False

app = Flask(__name__)
app.secret_key = '\x11>a\xebCh\xe2\xd2\xbe>\x87\rI\x07-\x8b'

# Manual control over hardware
def manual_control():
    while True:
        send = input('Enter: ')
        interface.send_message(send)

# The hardware listener listens for hardware communication with the main controller.
# Changing the global stop_listener will end hardware to main controller communication.
stop_listener = False
def hardware_listener():
    global stop_listener
    while (not stop_listener):
        message = interface.listen()
        if (message):
            print(f'\n * Message from hardware controller: {message}')
        # time.sleep(0.15)
        if ('+' in message):
            daily_orders.add_cup()

def establish_hardware_connection():
    print(" * Establishing Hardware Connection...")
    while ("READY" not in interface.listen()):
        interface.send_message("START")
    print(" * Connection Established.")
    listener = threading.Thread(target=hardware_listener)
    listener.start() # Start the hardware listener.
    manual = threading.Thread(target=manual_control)
    manual.start() # Start the manual control.

establish_hardware_connection()

# A boolean for manual sending of a message. If a message is sent manually, do not send the message at 7.
message_sent_manually = False

# The purpose of this method is to send an email with data collected over the day.
# Emails will be sent at 7PM MST every night.
def send_message():

    # Create a new email server which will send emails to the desired destination.
    email = EmailServer(["ethanperry247@gmail.com"])

    # Boolean used to affirm that a message is only sent once.
    message_sent = False

    # 19:00, or 7:00 PM MST is when the email will be sent.
    scheduled_time = 19

    # At 11:00 PM MST, all data will be reset for the following day.
    scheduled_reset = 23

    while True:
        # Global flag to stop the messenger.
        global stop_messenger
        if stop_messenger:
            exit(0)
            
        global message_sent_manually
        if message_sent_manually:
            message_sent = True

        print(" * Current Time is: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
        # If it is time to send a message, and a message hasn't been sent yet, send out the message.
        if (int(datetime.now().strftime("%H")) == scheduled_time and message_sent == False):
            email.send_message("Hello World.") # Input the message to be sent here.
            message_sent = True
        # Reset the boolean so that the server is ready to send a message the next day.
        if (int(datetime.now().strftime("%H")) == scheduled_reset and message_sent == True):
            if not message_sent_manually:
                daily_orders.end_orders()
                order_manager.condense_report(daily_orders)
            message_sent = False
            message_sent_manually = False
        
        # Every five minutes, check to see if it's time to send data via email.
        time.sleep(300)

timer = threading.Thread(target=send_message)
timer.start()

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
    now = datetime.now()
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
            'Donut Blend',
            'Breakfast Blend',
            'Colombian Molina',
            'Screaming Monkey',
            'Kenya AA - Medium Roast',
            'Costa Rican - Medium Roast',
            'Kona Island Blend',
            'Colombian Supremo',
            'Dark Estate',
            'Kenya AA - Dark Roast',
            'Costa Rican - Dark Roast',
            'Italian Roast',
            'French Roast',
            'Sumatra Mandeling',
            'Colombian Decaf',
            'French Vanilla',
            'Jamaican Me Nuts',
            'Salted Caramel',
            'Hazelnut'
        ]
        types.sort()
        return render_template('login.html', types=types, user=user)
    else: # If user fails to enter valid credentials, redirect to the home page.
        return redirect(url_for('index'))

@app.route("/create_order", methods=['POST', 'GET'])
def create_order():
    if request.method == 'POST':
        # Obtain the type of cup in production.
        type = request.form['type']

        # Pass that info into the daily orders.
        daily_orders.add_order(type)

    # Redirect the user to the main page.
    return redirect(url_for('main'))


@app.route("/main", methods=['POST', 'GET'])
def main():
    # Check if the user is logged in, and redirect if they are not.
    if (not 'username' in session):
        return redirect(url_for('index'))

    if (not daily_orders.orders):
        return redirect(url_for('login')) 

    
    template_data = {
        # Pass in all six observable stats.
        'total' : daily_orders.number,
        'current' : daily_orders.get_current_order().number,
        'current_type' : daily_orders.get_current_order().order_type,
        'current_box' : daily_orders.get_current_box_cups(),
        'current_box_count' : daily_orders.box_count,
        'total_boxes' : daily_orders.num_boxes,
        # Pass in the user of the current session into the main template.
        'user' : session['username']
    }

    return render_template('main.html', **template_data)

@app.route("/change_box_count", methods=['POST', 'GET'])
def change_box_count():
    if request.method == 'POST':
        try:
            count = int(request.form["count"])
            if (int(count) > 0):
                daily_orders.alter_box_count(count)
                interface.change_box_count(int(count))
            else:
                print(" * Invalid Box Count Entered.")
        except:
            print(" * Invalid Box Count Entered.")
    return redirect(url_for('main'))

@app.route("/change_box_count/<count>")
def change_box_count_by_url(count):
    try:
        if (int(count) > 0):
            daily_orders.alter_box_count(int(count))
            interface.change_box_count(int(count))
        else:
            print(" * Invalid Box Count Entered.")
    except:
        print(" * Invalid Box Count Entered.")
    return redirect(url_for('main'))

@app.route("/main/<action>")
def action(action):
    if (not daily_orders.orders):
        return redirect(url_for('login'))

    if (action == 'OPEN'):
        interface.open_cover()
    if (action == 'CLOSE'):
        interface.close_cover()
    if (action == 'STARTCONVEYOR'):
        interface.run_conveyor()
    if (action == 'STOPCONVEYOR'):
        interface.stop_conveyor()
    if (action == 'ADD'):
        daily_orders.add_cup()

    templateData = {
        'title' : 'HELLO!',
    }
    return redirect(url_for('main'))

@app.route("/send_report")
def send_report():
    global message_sent_manually
    message_sent_manually = True
    print(" * Closing daily orders and condensing daily report...")
    daily_orders.end_orders()
    order_manager.condense_report(daily_orders)
    print(" * Sending daily report...")
    email = EmailServer(["ethanperry247@gmail.com"])
    email.send_message(order_manager.generate_report(daily_orders))
    print(" * Progress report sent.")
    return redirect(url_for('main'))


# Refreshes statistics on the main page. Front end makes a call every five seconds.
@app.route("/AJAX")
def ajax():
    updatedData: dict() = {
        # Pass in all six observable stats.
        'totalCups' : daily_orders.number,
        'currentTypeTotal' : daily_orders.get_current_order().number,
        'currentBoxCount' : daily_orders.box_count,
        'currentBox' : daily_orders.get_current_box_cups(),
        'totalBoxes' : daily_orders.num_boxes,
    }
    return JSON.dumps(updatedData)

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

def exit_email_messenger():
    global stop_messenger
    stop_messenger = True
    while (timer.isAlive()):
        pass
    return True

@app.route("/exit")
def exit_server():
    print(" * Server shutting down...")
    print(" * Closing daily orders and condensing daily report...")
    daily_orders.end_orders()
    order_manager.condense_report(daily_orders)
    print(" * Sending daily report...")
    email = EmailServer(["ethanperry247@gmail.com"])
    email.send_message(order_manager.generate_report(daily_orders))
    print(" * Shutting down email messenger...")
    print(" * WARNING: Email messenger may take as long as 5 minutes to shut down.")
    if (exit_email_messenger()):
        print(" * Email messenger has stopped.")
    print(" * Shutdown complete.")
    exit(0)
