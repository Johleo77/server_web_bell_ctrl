import json
import os
from flask import Flask, render_template, jsonify
import RPi.GPIO as GPIO
import I2C_LCD_driver

# Configuration file path
CONFIG_FILE = "conf/config.json"

# Initialize LCD display
mylcd = I2C_LCD_driver.lcd()

# Initialize Flask app
app = Flask(__name__)

# Function to read the configuration from a JSON file
def read_config(config_file):
    with open(config_file, "rt") as file:
        return json.load(file)

# Read the initial configuration
config = read_config(config_file=CONFIG_FILE)
cloches = config["cloches"]

# GPIO configuration
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Setup GPIO for each cloche
for cloche in cloches:
    motor_gpio = cloche["motor_gpio"]
    status_gpio = cloche["status_gpio"]
    GPIO.setup(motor_gpio, GPIO.OUT)
    GPIO.setup(status_gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Function to set bell state
def set_bell(motor_gpio, state):
    GPIO.output(motor_gpio, state)
    if state:
        print(f"Opening the bell on GPIO {motor_gpio}")
    else:
        print(f"Closing the bell on GPIO {motor_gpio}")

# Endpoint to serve the main page
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to get the cloche configuration
@app.route('/config')
def get_config():
    return jsonify(cloches=cloches)

# Dynamic routes for each cloche
def create_routes_for_cloche(cloche):
    motor_gpio = cloche["motor_gpio"]
    status_gpio = cloche["status_gpio"]
    nom = cloche["nom"]

    # Define unique function names for each endpoint
    def open_bell_func():
        set_bell(motor_gpio, state=True)
        return jsonify(status="Bell opened")

    def close_bell_func():
        set_bell(motor_gpio, state=False)
        return jsonify(status="Bell closed")

    def get_bell_status_func():
        motor_status = GPIO.input(motor_gpio)
        button_status = GPIO.input(status_gpio)
        pos_status_str = "open" if motor_status == GPIO.LOW else "close"
        move_status_str = "move" if button_status == GPIO.LOW else "stop"
        status = f"{pos_status_str} {move_status_str}"
        mylcd.lcd_display_string(status, 1)
        return jsonify(status=status)

    # Attach routes with unique names based on cloche name
    app.add_url_rule(f'/{nom}/open', endpoint=f'open_bell_{nom}', view_func=open_bell_func, methods=['POST'])
    app.add_url_rule(f'/{nom}/close', endpoint=f'close_bell_{nom}', view_func=close_bell_func, methods=['POST'])
    app.add_url_rule(f'/{nom}/status', endpoint=f'get_bell_status_{nom}', view_func=get_bell_status_func, methods=['GET'])

# Create routes for each cloche
for cloche in cloches:
    create_routes_for_cloche(cloche)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
