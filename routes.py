import os
from flask import Blueprint, request, jsonify, render_template
import pandas as pd
from werkzeug.utils import secure_filename

# Create a Blueprint for our routes
upload_bp = Blueprint('upload', __name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/')
def index():
    return render_template('upload.html')

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Process Excel file
        try:
            df = pd.read_excel(filepath)
            # Extract basic information
            data = {
                'columns': df.columns.tolist(),
                'rows': len(df),
                'preview': df.head().to_dict('records')
            }
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400
