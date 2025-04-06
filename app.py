import os
import json
import webbrowser
import threading
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from src.main import PolicyDNAExtractor
from config.config import get_config

app = Flask(__name__)

# Configure upload settings
UPLOAD_FOLDER = 'src/data'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size

def get_processed_files():
    """
    Retrieve list of processed files from the output directory.
    
    Returns:
        List of dictionaries containing file information
    """
    processed_files = []
    
    # List of files to look for
    file_types = [
        'policy_dna_complete.json',
        'phase4_graph_map.json',
        'phase3_language_map.json',
        'phase2_element_map.json',
        'phase1_document_map.json'
    ]
    
    for filename in file_types:
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        if os.path.exists(filepath):
            file_stat = os.stat(filepath)
            processed_files.append({
                'filename': filename,
                'path': filepath,
                'size': f"{file_stat.st_size / 1024:.2f} KB",
                'modified': os.path.getmtime(filepath)
            })
    
    # Sort by modification time, most recent first
    processed_files.sort(key=lambda x: x['modified'], reverse=True)
    
    return processed_files

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Main page with file upload and list of processed files.
    """
    # Get list of processed files
    processed_files = get_processed_files()
    
    if request.method == 'POST':
        # Handle file upload
        if 'file' not in request.files:
            return render_template('index.html', 
                                   error='No file part', 
                                   processed_files=processed_files)
        
        file = request.files['file']
        
        # If no file is selected
        if file.filename == '':
            return render_template('index.html', 
                                   error='No selected file', 
                                   processed_files=processed_files)
        
        # If file is allowed
        if file and allowed_file(file.filename):
            # Secure the filename and save it
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Process the document
            try:
                # Initialize config and extractor
                config = get_config()
                config.output_dir = OUTPUT_FOLDER
                extractor = PolicyDNAExtractor(config)
                
                # Process the document
                result = extractor.process_document(filename)
                
                # Redirect to results page or show processed files
                return redirect(url_for('index'))
            
            except Exception as e:
                # Handle any processing errors
                return render_template('index.html', 
                                       error=f'Error processing document: {str(e)}', 
                                       processed_files=processed_files)
        
        # If file type is not allowed
        return render_template('index.html', 
                               error='File type not allowed. Please upload PDF, DOCX, or TXT.', 
                               processed_files=processed_files)
    
    # GET request - show upload form and processed files
    return render_template('index.html', 
                           processed_files=processed_files)

@app.route('/download/<path:filename>')
def download_file(filename):
    """Allow downloading of processed file."""
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

@app.route('/view/<path:filename>')
def view_file(filename):
    """View contents of a processed file."""
    try:
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        with open(filepath, 'r') as f:
            # Try to parse as JSON for pretty printing
            file_contents = json.load(f)
            formatted_contents = json.dumps(file_contents, indent=2)
        return render_template('view_file.html', 
                               filename=filename, 
                               contents=formatted_contents)
    except Exception as e:
        return f"Error viewing file: {str(e)}", 500

def open_browser():
    """Open the default web browser to the app's URL."""
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    # Ensure necessary directories exist
    os.makedirs('src/data', exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    # Open browser after a short delay to allow server to start
    threading.Timer(1.25, open_browser).start()
    
    # Run the app
    app.run(debug=True)