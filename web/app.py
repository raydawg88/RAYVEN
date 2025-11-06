"""
RAYVEN Web Interface

Flask server with WebSocket for real-time visualization.
"""

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rayven-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state (updated by main.py)
current_state = {
    "level": 1,
    "balance": 59.85,
    "progress": 0,
    "target": 85.0,
    "coin": "BTC",
    "current_step": 0,
    "step_name": "Initializing...",
    "trades": [],  # Last 100 trades
    "status": "Starting RAYVEN..."
}


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    """Send current state when client connects"""
    print("Client connected")
    emit('state_update', current_state)


def update_state(data):
    """
    Called by main.py to update state.

    Args:
        data: Dict with state updates
    """
    global current_state
    current_state.update(data)
    socketio.emit('state_update', current_state)


def emit_step(step_num, step_name):
    """Emit step update"""
    socketio.emit('step_update', {
        'step': step_num,
        'name': step_name
    })


def emit_trade(trade_data):
    """Emit completed trade"""
    current_state['trades'].insert(0, trade_data)
    if len(current_state['trades']) > 100:
        current_state['trades'].pop()

    socketio.emit('trade_complete', trade_data)


def emit_level_up(level_data):
    """Emit level up event"""
    socketio.emit('level_up', level_data)


def emit_status(message):
    """Emit status message"""
    current_state['status'] = message
    socketio.emit('status', {'message': message})


def run_server():
    """Run the Flask server"""
    print("🌐 Starting web interface on http://localhost:5001")
    socketio.run(app, host='0.0.0.0', port=5001, debug=False, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    run_server()
