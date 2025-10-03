from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__, static_folder='.')
CORS(app)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '181818',
    'database': 'yoga',
    'port': 3306
}

@app.route('/')
def index():
    # Serve index.html from the current directory
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    # Basic validation
    if not data.get('category') or not data.get('college') or not data.get('gender'):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    if data['category'] == 'Traditional Team':
        if not data.get('teamPlayers') or len([p for p in data['teamPlayers'] if p]) < 6:
            return jsonify({'success': False, 'message': 'Team must have 6 player names'}), 400
    else:
        if not data.get('name'):
            return jsonify({'success': False, 'message': 'Name required for individual registration'}), 400
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        if data['category'] == 'Traditional Team':
            for player in data['teamPlayers']:
                cursor.execute(
                    "INSERT INTO registrations (name, college, gender, category, team) VALUES (%s, %s, %s, %s, %s)",
                    (player, data['college'], data['gender'], data['category'], 1)
                )
        else:
            cursor.execute(
                "INSERT INTO registrations (name, college, gender, category, team) VALUES (%s, %s, %s, %s, %s)",
                (data['name'], data['college'], data['gender'], data['category'], 0)
            )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/registrations')
def get_registrations():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM registrations")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
