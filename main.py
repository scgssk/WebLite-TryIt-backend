from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
from flask import send_from_directory
import builder  # your existing builder.py

app = Flask(__name__)
CORS(app, origins="*")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.route("/api/build", methods=["POST"])
def build_site():
    data = request.json
    yaml_code = data.get("yaml")

    if not yaml_code:
        return jsonify({"error": "Missing YAML code"}), 400

    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}.wl")

    with open(input_path, "w", encoding="utf-8") as f:
        f.write(yaml_code)

    try:
        builder.build(input_path)

        # Determine default preview file
        start_page = None
        for candidate in ["home.html", "index.html"]:
            path = os.path.join(OUTPUT_DIR, candidate)
            if os.path.exists(path):
                start_page = candidate
                break

        if not start_page:
            # Try to use the first .html in the folder
            files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".html")]
            if files:
                start_page = files[0]
            else:
                return jsonify({"error": "No HTML page generated"}), 500

        return jsonify({ "success": True, "startPage": start_page })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/output/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True)
