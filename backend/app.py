from flask import Flask, request, send_file, jsonify, render_template
from flask_cors import CORS
from PIL import Image
import io
import os
import logging
from werkzeug.utils import secure_filename
import time
import tempfile
import json
from pathlib import Path

# Import the CircuitParser
from skelo_ai import CircuitParser
CIRCUIT_PARSER_AVAILABLE = True

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
BASEDIR = Path("C:/Users/shahz/OneDrive/Documents/Projects/SketchLogic")

app = Flask(
    __name__,
    static_folder=BASEDIR / 'frontend',   # where style.css and script.js live
    static_url_path='/'                 # they’re served at /static/...
)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max file size for circuit diagrams
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}

# Global circuit parser instance
circuit_parser = None

def initialize_circuit_parser():
    """Initialize the CircuitParser model globally."""
    global circuit_parser
    if CIRCUIT_PARSER_AVAILABLE and circuit_parser is None:
        try:
            logger.info("Loading CircuitParser model...")
            circuit_parser = CircuitParser()
            circuit_parser.load_model()
            circuit_parser.parse_circuit("skelo_ai/inputs/3.jpg")
            logger.info("CircuitParser model loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to load CircuitParser: {e}")
            circuit_parser = None

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_temp_image(image_data):
    """Save uploaded image to a temporary file and return the path."""
    # Create a temporary file with proper extension
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    
    # Open and convert image if necessary
    image = Image.open(io.BytesIO(image_data))
    
    # Convert to RGB if necessary (for JPEG compatibility)
    if image.mode in ('RGBA', 'LA'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode == 'RGBA':
            background.paste(image, mask=image.split()[-1])
        else:
            background.paste(image)
        image = background
    elif image.mode not in ('RGB', 'L'):
        image = image.convert('RGB')
    
    # Save to temporary file
    image.save(temp_file.name, format='JPEG', quality=95)
    temp_file.close()
    
    return temp_file.name

@app.route('/')
def serve_index():
    return send_file(BASEDIR / 'frontend/index.html')

@app.route('/health')
def index():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'Circuit Analysis Server is running',
        'circuit_parser_loaded': circuit_parser is not None,
        'max_file_size': '32MB',
        'allowed_formats': list(ALLOWED_EXTENSIONS)
    })

@app.route('/process-circuit', methods=['POST'])
def process_circuit_endpoint():
    """Process uploaded circuit image and return analysis results."""
    start_time = time.time()
    
    try:
        # Check if CircuitParser is available
        if not circuit_parser:
            logger.error("CircuitParser not available")
            return jsonify({
                'error': 'Circuit analysis service not available',
                'details': 'CircuitParser model not loaded'
            }), 503
        
        # Check if image was uploaded
        if 'image' not in request.files:
            logger.warning("No image file in request")
            return jsonify({'error': 'No circuit image file provided'}), 400
        
        file = request.files['image']
        
        # Check if file was selected
        if file.filename == '':
            logger.warning("Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type: {file.filename}")
            return jsonify({
                'error': 'Invalid file type', 
                'allowed_formats': list(ALLOWED_EXTENSIONS)
            }), 400
        
        logger.info(f"Processing circuit diagram: {file.filename}")
        
        # Read image data
        image_data = file.read()
        
        # Save to temporary file for processing
        temp_image_path = None
        try:
            temp_image_path = save_temp_image(image_data)
            logger.info(f"Saved temporary image: {temp_image_path}")
            
            # Process the circuit
            logger.info("Starting circuit analysis...")

            circuit_results, rendered_image = circuit_parser.parse_circuit(temp_image_path)
            # PATCH: fix for circuit results
            patched_wires = []
            for wire_id, value in circuit_results['wires'].items():
                patched_wires.append({wire_id: value})
            circuit_results['wires'] = patched_wires
            
            processing_time = time.time() - start_time
            logger.info(f"Circuit analysis completed in {processing_time:.2f}s")
            
            # Convert PIL image to bytes for response
            output_buffer = io.BytesIO()
            if rendered_image:
                # Ensure rendered_image is in RGB mode
                if rendered_image.mode != 'RGB':
                    rendered_image = rendered_image.convert('RGB')
                rendered_image.save(output_buffer, format='JPEG', quality=90, optimize=True)
                output_buffer.seek(0)
                
                # Encode the processed image as base64 for JSON response
                import base64
                processed_image_b64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
                
                # Also prepare original image as base64
                original_image_b64 = base64.b64encode(image_data).decode('utf-8')
                
                response_data = {
                    'success': True,
                    'processing_time': round(processing_time, 2),
                    'analysis_results': circuit_results,
                    'original_image': f"data:image/jpeg;base64,{original_image_b64}",
                    'processed_image': f"data:image/jpeg;base64,{processed_image_b64}",
                    'filename': secure_filename(file.filename),
                    'timestamp': time.time()
                }
                
                return jsonify(response_data)
            else:
                return jsonify({
                    'error': 'Failed to render circuit diagram',
                    'analysis_results': circuit_results
                }), 500
                
        except Exception as e:
            logger.error(f"Error during circuit processing: {str(e)}")
            return jsonify({
                'error': 'Circuit analysis failed',
                'details': str(e)
            }), 500
            
        finally:
            # Clean up temporary file
            if temp_image_path and os.path.exists(temp_image_path):
                try:
                    os.unlink(temp_image_path)
                    logger.info(f"Cleaned up temporary file: {temp_image_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temp file: {e}")
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/health')
def health_check():
    """Detailed health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'server': 'Circuit Analysis Server',
        'version': '1.0',
        'circuit_parser_loaded': circuit_parser is not None,
        'uptime': time.time()
    })

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({'error': 'File too large. Maximum size is 32MB.'}), 413

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize the circuit parser model
    initialize_circuit_parser()
    
    # Create temporary directory if it doesn't exist
    os.makedirs('temp', exist_ok=True)
    
    # Run the server
    logger.info("Starting Circuit Analysis Server...")
    logger.info("Server will be available at http://localhost:5000")
    
    if circuit_parser:
        logger.info("✓ Circuit analysis capabilities enabled")
    else:
        logger.warning("⚠ Circuit analysis capabilities disabled")
    
    # For production, use a proper WSGI server like Gunicorn
    app.run(
        host='0.0.0.0',  # Listen on all interfaces
        port=5000,
        debug=False,     # Set to False for production
        threaded=True    # Enable threading for better concurrency
    )