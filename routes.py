import os
import re
from flask import Blueprint, request, jsonify, render_template
import pandas as pd
from werkzeug.utils import secure_filename

# Create a Blueprint for our routes
upload_bp = Blueprint('upload', __name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
REQUIRED_COLUMNS = ['Task', 'E-mail', 'Recipient']

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_columns(df):
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    return True

def validate_email(email):
    if pd.isna(email):
        return False
    # Basic email validation pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, str(email)) is not None

def clean_dataframe(df):
    # Replace NaN values with empty strings
    df = df.fillna('')
    
    # Validate email addresses
    invalid_emails = df[~df['E-mail'].apply(validate_email)].index.tolist()
    if invalid_emails:
        raise ValueError(f"Invalid email addresses found in rows: {[i+2 for i in invalid_emails]}")  # +2 for Excel row numbers
    
    # Convert all values to strings and strip whitespace
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
    
    return df

@upload_bp.route('/')
def index():
    return render_template('upload.html')

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename or '')
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        try:
            # Read Excel file
            df = pd.read_excel(filepath)
            
            # Validate required columns
            validate_columns(df)
            
            # Extract only required columns
            df = df[REQUIRED_COLUMNS]
            
            # Clean and validate data
            df = clean_dataframe(df)
            
            # Extract basic information
            data = {
                'columns': REQUIRED_COLUMNS,
                'rows': len(df),
                'preview': df.head().to_dict('records')
            }
            return jsonify(data)
        except ValueError as ve:
            return jsonify({'error': str(ve)}), 400
        except Exception as e:
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
        finally:
            # Clean up the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
    
    return jsonify({'error': 'Invalid file type'}), 400
