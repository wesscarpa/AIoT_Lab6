from flask import Flask, request, jsonify
import json
from datetime import datetime, timezone
import os

app = Flask(__name__)

DATA_FILE = "accelerometer_data.jsonl"


@app.route("/", methods=["GET"])
def home():
    return "ESP32 Accelerometer Server is running!"


@app.route("/upload", methods=["POST"])
def upload_data():

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400

    # Check that all three axes are present
    required = ["x", "y", "z"]

    for axis in required:
        if axis not in data:
            return jsonify({"error": "Missing axis: " + axis}), 400

    # Check that the three arrays have matching lengths
    if not all(isinstance(data[a], list) for a in required):
        return jsonify({"error": "Axis data must be lists"}), 400

    if not (len(data["x"]) == len(data["y"]) == len(data["z"])):
        return jsonify({"error": "Axis lengths do not match"}), 400

    if len(data["x"]) == 0:
        return jsonify({"error": "No accelerometer samples"}), 400

    # Add server-side timestamp
    data["received_at"] = datetime.now(timezone.utc).isoformat()

    # Append one JSON object per line
    with open(DATA_FILE, "a") as file:
        file.write(json.dumps(data) + "\n")

    return jsonify({
        "status": "success",
        "message": "Accelerometer data saved",
        "samples_received": len(data["x"])
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
