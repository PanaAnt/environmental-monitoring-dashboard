
from flask import Flask, render_template, jsonify
import redis
import json
import time
import os 
from dotenv import load_dotenv
app = Flask(
    __name__,
    static_url_path="/humitemp/static",
    static_folder="static",
    template_folder="templates"
)

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/sensor/latest")
def get_latest():
    data = redis_client.get("sensor:latest")
    if not data:
        return jsonify({"status": "initializing"}), 503
    return jsonify(json.loads(data))


@app.route("/api/sensor/history")
def get_window():
    values = redis_client.lrange("sensor:history", 0, -1)
    return jsonify([json.loads(v) for v in reversed(values)])


@app.route("/api/status")
def status():
    timestamp = redis_client.get("sensor:timestamp")
    if not timestamp:
        return jsonify({"redis": "connected", "sensor": "no data"})

    age = time.time() - float(timestamp)
    return jsonify({
        "redis": "connected",
        "last_update_seconds": round(age, 1),
        "data_fresh": age < 2
    })


if __name__ == "__main__":
    app.run(host=os.getenv("IP_ADDRESS"), port=os.getenv("PORT"))
