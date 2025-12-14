from flask import Flask, request, jsonify
from flask_cors import CORS
import time, io, base64
from PIL import Image, ImageOps
from skelo.circuit_parser import CircuitParser
from pathlib import Path

app = Flask(__name__)
CORS(app)

MODEL_PATH = Path("skelo/SKELOv1.pt")

# PREPARE THE CIRCUIT PARSER
engine = CircuitParser(MODEL_PATH)
engine.load_model()
engine.parse_circuit("example.jpg")

@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "circuit_parser_loaded": True,  # TODO: set real value later
        "timestamp": time.time()
    })

@app.route("/api/process-circuit", methods=["POST"])
def process_circuit():
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

    start = time.time()

    # Parser always returns (analysis_results, processed PIL image)
    analysis_results, processed_pil = engine.parse_circuit(img)

    # Original image as data URL (use the uploaded mimetype if available)
    orig_mime = f.mimetype or (f"image/{(img.format or 'jpeg').lower()}")
    original_b64 = base64.b64encode(img_bytes).decode("utf-8")
    original_data_url = f"data:{orig_mime};base64,{original_b64}"

    # Processed PIL -> data URL (PNG if alpha, else JPEG)
    buf = io.BytesIO()
    has_alpha = (
        processed_pil.mode in ("RGBA", "LA")
        or (processed_pil.mode == "P" and "transparency" in processed_pil.info)
    )
    if has_alpha:
        processed_pil.save(buf, format="PNG", optimize=True)
        proc_mime = "image/png"
    else:
        if processed_pil.mode not in ("RGB", "L"):
            processed_pil = processed_pil.convert("RGB")
        processed_pil.save(buf, format="JPEG", quality=85, optimize=True)
        proc_mime = "image/jpeg"

    processed_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    processed_data_url = f"data:{proc_mime};base64,{processed_b64}"

    return jsonify({
        "success": True,
        "processing_time": round(time.time() - start, 2),
        "analysis_results": analysis_results,   # ← real results from the parser
        "original_image": original_data_url,
        "processed_image": processed_data_url,
        "filename": f.filename,
        "timestamp": time.time()
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
