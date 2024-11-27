from sense_hat import SenseHat
from flask import Flask, jsonify
import time, sys
from datetime import datetime
import logging

app = Flask(__name__)

# Disable Flask logging
app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True

# Initialize SenseHat
sense = SenseHat()


def get_readings():
    # Collect sensor readings and format the data
    temp = round(sense.get_temperature_from_humidity(), 1)
    humidity = round(sense.get_humidity(), 1)
    pressure = round(sense.get_pressure(), 1)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        'timestamp': timestamp,
        'temperature': temp,
        'humidity': humidity,
        'pressure': pressure
    }


@app.route('/data')
def get_data():
    # Endpoint to retrieve sensor data
    return jsonify(get_readings())


if __name__ == '__main__':
    # Run server without displaying banner logs
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    app.run(host='0.0.0.0', port=5001, debug=False)