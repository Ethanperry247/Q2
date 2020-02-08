from flask import Flask, render_template
import datetime
import logging


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