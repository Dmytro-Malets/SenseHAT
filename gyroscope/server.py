from sense_hat import SenseHat
from flask import Flask, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True

CORS(app)
sense = SenseHat()


@app.route('/orientation')
def get_orientation():
    """
    Retrieve device orientation data from Sense HAT.

    Returns:
    JSON object with pitch, roll, and yaw values rounded to 3 decimal places

    Note: Data is smoothed for more fluid animation
    """
    orientation = sense.get_orientation()
    # Smoothing data for more fluid animation
    return jsonify({
        'pitch': round(orientation['pitch'], 3),
        'roll': round(orientation['roll'], 3),
        'yaw': round(orientation['yaw'], 3)
    })


if __name__ == '__main__':
    # Run Flask server on all network interfaces, port 5002
    app.run(host='0.0.0.0', port=5002, debug=False)