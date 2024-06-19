#!/usr/bin/python

from flask import Flask
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)  # Sets up the RPi lib to use the Broadcom pin mappings
                        #  for the pin names. This corresponds to the pin names
                        #  given in most documentation of the Pi header
GPIO.setwarnings(False) # Turn off warnings that may crop up if you have the
                        #  GPIO pins exported for use via command line
GPIO.setup(17, GPIO.OUT) # Set GPIO2 as an output

app = Flask(__name__)   # Create an instance of flask called "app"

@app.route("/")         # This is our default handler, if no path is given
def index():
    return "hello"

# The magic happens here. When some http request comes in with a path of
#  gpio/x/y, the Flask app will attempt to parse that as x=pin and y=level.
#  Note that there is no error handling here! Failure to properly specify the
#  route will result in a 404 error.
@app.route('/gpio_on')
def set_gpio_on():
    GPIO.output(17, 1)
    return "GPIO ON"

@app.route('/gpio_off')
def set_gpio_off():
    GPIO.output(17, 0)
    return "GPIO OFF"

# If we're running this script directly, this portion executes. The Flask
#  instance runs with the given parameters. Note that the "host=0.0.0.0" part
#  is essential to telling the system that we want the app visible to the 
#  outside world.
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
