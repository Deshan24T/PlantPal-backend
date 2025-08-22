from flask import Flask, request, jsonify
from supabase import create_client
import os

app = Flask(__name__)

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/api/data", methods=["POST"])
def receive_data():
    data = request.json
    res = supabase.table("sensor_readings").insert({
        "temperature": data["temperature"],
        "humidity": data["humidity"],
        "soil_moisture": data["soil_moisture"],
        "light": data["light"]
    }).execute()
    return jsonify({"status": "success", "data": res.data})

@app.route("/api/latest", methods=["GET"])
def latest_data():
    res = supabase.table("sensor_readings").select("*").order("timestamp", desc=True).limit(20).execute()
    return jsonify(res.data)
