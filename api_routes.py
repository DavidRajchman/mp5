from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime

temperature_api = Blueprint('temperature_api', __name__)

def get_current_timestamp():
    return datetime.now().strftime("%H:%M")

@temperature_api.route('/add', methods=['POST'])
def add_temperature():
    new_temp = request.json.get('temperature')
    new_reading = {"timestamp": get_current_timestamp(), "temperature": new_temp}

    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("INSERT INTO temperatures VALUES (?, ?)", (new_reading["timestamp"], new_reading["temperature"]))
    conn.commit()
    conn.close()

    return jsonify(new_reading), 201

@temperature_api.route('/newest', methods=['GET'])
def get_newest_reading():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM temperatures ORDER BY timestamp DESC LIMIT 1")
    last_reading = c.fetchone()
    conn.close()

    return jsonify({"timestamp": last_reading[0], "temperature": last_reading[1]})

@temperature_api.route('/newest/<int:x>', methods=['GET'])
def get_newest_x_readings(x):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM temperatures ORDER BY timestamp DESC LIMIT ?", (x,))
    last_x_readings = c.fetchall()
    conn.close()

    return jsonify([{"timestamp": reading[0], "temperature": reading[1]} for reading in last_x_readings])

@temperature_api.route('/delete_oldest/<int:y>', methods=['DELETE'])
def delete_oldest_y_readings(y):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM temperatures ORDER BY timestamp ASC LIMIT ?", (y,))
    oldest_y_readings = c.fetchall()

    for reading in oldest_y_readings:
        c.execute("DELETE FROM temperatures WHERE timestamp = ? AND temperature = ?", (reading[0], reading[1]))

    conn.commit()
    conn.close()

    return jsonify({"message": f"Deleted {y} oldest readings"}), 200

@temperature_api.route('/count', methods=['GET'])
def get_reading_count():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM temperatures")
    count = c.fetchone()[0]
    conn.close()

    return jsonify({"count": count})