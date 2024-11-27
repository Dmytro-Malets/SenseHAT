from sense_hat import SenseHat
from flask import Flask, jsonify
import time
import logging

app = Flask(__name__)
# Disable all Flask logs
app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True

sense = SenseHat()


@app.route('/get_acceleration')
def get_acceleration():

    acceleration = sense.get_accelerometer_raw()
    return jsonify({
        'x': acceleration['x'],
        'y': acceleration['y'],
        'z': acceleration['z'],
        'timestamp': time.time()
    })


if __name__ == '__main__':
    # Run Flask server on all network interfaces, port 5003
    app.run(host='0.0.0.0', port=5003, debug=False)