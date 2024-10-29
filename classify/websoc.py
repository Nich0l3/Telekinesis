from flask import Flask
from flask_socketio import SocketIO
import numpy as np
import pickle

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return "WebSocket server is running"

@socketio.on('send_eeg')
def handle_eeg(data):
    frequency_data = pickle.loads(data)
    # Process or classify the data
    print("Received EEG data")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
