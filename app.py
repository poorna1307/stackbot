import sqlite3
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, send

app = Flask(_name_)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Set up the SQLite3 database
def init_db():
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS correct_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        message TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    username = data['username']
    msg = data['message']
    print(f'Message from {username}: {msg}')
    send({'username': username, 'message': msg}, broadcast=True)

@app.route('/feedback', methods=['POST'])
def feedback():
    username = request.json['username']
    feedback_type = request.json['feedback']

    satisfied = feedback_type == 'Satisfied'
    not_satisfied = feedback_type == 'Not Satisfied'

    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('INSERT INTO feedback (username, satisfied, not_satisfied) VALUES (?, ?, ?)',
              (username, satisfied, not_satisfied))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'}), 200

@app.route('/correct-answer', methods=['POST'])
def correct_answer():
    username = request.json['username']
    message = request.json['message']

    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('INSERT INTO correct_answers (username, message) VALUES (?, ?)', (username, message))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'}), 200


if _name_ == '_main_':
    socketio.run(app, debug=True)