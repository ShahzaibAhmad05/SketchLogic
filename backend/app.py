from flask import Flask, request, jsonify
from flask_cors import CORS
import time, io, base64, os
from PIL import Image, ImageOps
from skelo.circuit_parser import CircuitParser
from pathlib import Path


app = Flask(__name__)
CORS(app)
MODEL_PATH = Path("skelo/SKELOv1.pt")


engine = None
def get_engine():     # Returns the circuit parser engine if available
    global engine     # else prepares and returns it
    if engine is None:
        e = CircuitParser(MODEL_PATH)
        e.load_model()
        engine = e
    return engine


@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "circuit_parser_loaded": engine is not None,
        "timestamp": time.time()
    })


@app.route("/api/process-circuit", methods=["POST"])
def process_circuit():
    # Verify the image file is in the request
    if "image" not in request.files:
        return jsonify({"error": "No circuit image file provided"}), 400

    f = request.files["image"]
    img_bytes = f.read()

    # Open as PIL and fix orientation
    img = Image.open(io.BytesIO(img_bytes))
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass
    start_time = time.time()    # Record time taken for processing

    # Parse img in engine
    analysis_results = get_engine().parse_circuit(img)

    return jsonify({
        "success": True,
        "processing_time": round(time.time() - start_time, 6),
        "analysis_results": analysis_results,
        "filename": f.filename,
        "timestamp": time.time()
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
