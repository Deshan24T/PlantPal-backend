from flask import Flask, request, jsonify
import os
import psycopg2

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASS"),
        port=os.environ.get("DB_PORT", 5432)
    )
    return conn

@app.route("/")
def home():
    return "Sensor API (Supabase + Railway) is running 🚀"

@app.route("/api/data", methods=["POST"])
def receive_data():
    data = request.json
    temperature = data.get("temperature")
    humidity = data.get("humidity")
    soil_moisture = data.get("soil_moisture")
    light = data.get("light")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sensor_readings (temperature, humidity, soil_moisture, light) VALUES (%s, %s, %s, %s)",
        (temperature, humidity, soil_moisture, light)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Data stored successfully"}), 201

@app.route("/api/data", methods=["GET"])
def get_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT 10")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
