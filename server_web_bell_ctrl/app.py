#######################################################################################################################
# Module informations
#######################################################################################################################
__project__ = "ECOTRON IDF - Ouverture et fermeture d'une cloche"
__author__ = "Johan Leonard (johanleonard77@gmail.com)"
__modifiers__ = ""
__history__ = """
    - Revision 1.0 (2024/06/04) : First Version.
              """
__date__ = "2024/06/06"
__version__ = "1.0.2"


#######################################################################################################################
import RPi.GPIO as GPIO
import time
import json
import os
from flask import Flask, render_template, jsonify

import I2C_LCD_driver

# Configuration file path
CONFIG_FILE = "conf/config.json"


# GPIO configuration
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

status = "Unknown"

# Function to read the configuration from a JSON file
def read_config(config_file):
    if os.path.exists(config_file):
        print(config_file)
        with open(config_file, "rt") as file:
            return json.load(file)

# Read the initial configuration
config = read_config(config_file=CONFIG_FILE)
motor_gpio = config["motor_gpio"]
button_gpio = config["status_gpio"]

print(f"motor_gpio = {motor_gpio}")

# IN/OUT GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(motor_gpio, GPIO.OUT)
# Definir dans fichier de configuration un etat initial
# de position de cloche
#GPIO.output(motor_gpio, GPIO.HIGH)
GPIO.setup(button_gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
mylcd = I2C_LCD_driver.lcd()

app = Flask(__name__)

# state : True = open, False = close
def set_bell(state):
    GPIO.output(17, state)
    if state:
        print("opening the bell")
        #mylcd.lcd_display_string("opening bell !", 1)
    else:
        print("closing the bell")
        #mylcd.lcd_display_string("opening bell !", 1)


@app.route('/')
def index():
    return render_template('index.html')

# Function to start the engine
@app.route('/open')
def open_bell():
    set_bell(state=True)
    return jsonify(status="Bell closed")

# Function to stop the engine
@app.route('/close')
def close_bell():
    set_bell(state=False)
    return jsonify(status="Bell opened")

# Function to know the position of the bell
@app.route('/status')
def get_bell_status():
    motor_status = GPIO.input(motor_gpio)
    button_status = GPIO.input(button_gpio)
    print(f"motor_status = {motor_status}, button_status = {button_status}")
    
    pos_status_str = "open" if motor_status == GPIO.LOW else "close"
    move_status_str = "move" if button_status == GPIO.LOW else "stop"
    
    status = f"{pos_status_str} {move_status_str}"
    mylcd.lcd_display_string(status, 1)
    return jsonify(status=status)

# Fonction pour gérer la fermeture de l'application
#@app.teardown_appcontext
#def cleanup(exception=None):
#    GPIO.cleanup()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
