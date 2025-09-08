import os, json, subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error":"Invalid JSON"}), 400

    prompt = data.get("prompt") or data.get("tts_text")
    image_url = data.get("image_url") or data.get("url")
    if not prompt or not image_url:
        return jsonify({"error":"Missing prompt or image_url"}), 400

    # Call the selenium runner as a subprocess (synchronous)
    try:
        cmd = ["python", "run_selenium.py", json.dumps({"prompt": prompt, "image_url": image_url})]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=420)
        out = json.loads(result.stdout)
        return jsonify({"status":"ok","prompt":prompt,"image_url":image_url,"video_url":out.get("video_url")})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.stderr or e.stdout}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)