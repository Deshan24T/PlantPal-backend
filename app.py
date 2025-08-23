
from flask import Flask, request, jsonify, render_template
import os
from supabase import create_client

app = Flask(__name__)

# --- Supabase Client ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    # App will still start so you can see a helpful error at /health
    supabase = None
else:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/health")
def health():
    ok = bool(supabase)
    return jsonify({
        "status": "ok" if ok else "missing_env",
        "needs": [] if ok else ["SUPABASE_URL", "SUPABASE_KEY"]
    })

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/data", methods=["POST"])
def receive_data():
    if not supabase:
        return jsonify({"error": "Server missing SUPABASE_URL and/or SUPABASE_KEY"}), 500

    data = request.get_json(silent=True) or {}
    # Basic validation
    required = ["temperature", "humidity", "soil_moisture", "light"]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        payload = {
            "temperature": float(data["temperature"]),
            "humidity": float(data["humidity"]),
            "soil_moisture": int(data["soil_moisture"]),
            "light": float(data["light"]),
        }
    except Exception as e:
        return jsonify({"error": f"Invalid types: {e}"}), 400

    try:
        res = supabase.table("sensor_readings").insert(payload).execute()
        return jsonify({"message": "Data stored", "inserted": res.data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/latest", methods=["GET"])
def latest():
    if not supabase:
        return jsonify({"error": "Server missing SUPABASE_URL and/or SUPABASE_KEY"}), 500

    try:
        res = (
            supabase.table("sensor_readings")
            .select("*")
            .order("timestamp", desc=True)
            .limit(20)
            .execute()
        )
        return jsonify(res.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
