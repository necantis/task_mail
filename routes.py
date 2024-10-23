import os
import re
from flask import Blueprint, request, jsonify, render_template
import pandas as pd
from werkzeug.utils import secure_filename
from email_generator import generate_email_from_task
from pdf_analyzer import analyze_pdf_document, PDFAnalysisError
from utils import send_email

# Create a Blueprint for our routes
upload_bp = Blueprint('upload', __name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'pdf'}
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
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, str(email)) is not None

def clean_dataframe(df):
    # Replace NaN values with empty strings
    df = df.fillna('')
    
    # Convert all values to strings and strip whitespace
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
    
    # Filter out rows with empty tasks
    original_rows = len(df)
    df = df[df['Task'].str.len() > 0]
    filtered_rows = original_rows - len(df)
    
    # Validate email addresses on remaining rows
    invalid_emails = df[~df['E-mail'].apply(validate_email)].index.tolist()
    if invalid_emails:
        raise ValueError(f"Invalid email addresses found in rows: {[i+2 for i in invalid_emails]}")
    
    return df, filtered_rows

def cleanup_file(filepath):
    """Safely clean up uploaded file."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Warning: Failed to clean up file {filepath}: {str(e)}")

@upload_bp.route('/')
def index():
    return render_template('upload.html')

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if not file or not file.filename:
        return jsonify({'error': 'No selected file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        file.save(filepath)
        
        if filename.lower().endswith('.pdf'):
            try:
                # Handle PDF analysis with improved error handling
                analysis_results = analyze_pdf_document(open(filepath, 'rb'))
                return jsonify({
                    'type': 'pdf_analysis',
                    'results': analysis_results
                })
            except PDFAnalysisError as pe:
                return jsonify({'error': str(pe)}), 400
            except Exception as e:
                return jsonify({'error': f'PDF analysis failed: {str(e)}'}), 500
        else:
            try:
                # Handle Excel file
                df = pd.read_excel(filepath)
                validate_columns(df)
                df = df[REQUIRED_COLUMNS]
                df, filtered_rows = clean_dataframe(df)
                
                emails = []
                for _, row in df.iterrows():
                    try:
                        email = generate_email_from_task(
                            task=str(row['Task']),
                            recipient_name=str(row['Recipient'])
                        )
                        emails.append({
                            'task': row['Task'],
                            'recipient': row['Recipient'],
                            'email': row['E-mail'],
                            'generated_email': email
                        })
                    except Exception as e:
                        print(f"Warning: Failed to generate email for task: {str(e)}")
                        continue
                
                if not emails:
                    raise ValueError("Failed to generate any emails from the Excel data")
                
                return jsonify({
                    'type': 'excel_processing',
                    'columns': REQUIRED_COLUMNS,
                    'rows': len(df),
                    'filtered_rows': filtered_rows,
                    'preview': df.head().to_dict('records'),
                    'generated_emails': emails
                })
            except pd.errors.EmptyDataError:
                return jsonify({'error': 'The Excel file is empty'}), 400
            except pd.errors.ParserError:
                return jsonify({'error': 'Failed to parse Excel file. Please ensure it is a valid Excel file.'}), 400
            except Exception as e:
                return jsonify({'error': f'Excel processing failed: {str(e)}'}), 500
                
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    finally:
        # Always clean up the uploaded file
        cleanup_file(filepath)

@upload_bp.route('/send-email', methods=['POST'])
def send_single_email():
    try:
        data = request.get_json()
        if not data or not all(key in data for key in ['email', 'subject', 'body']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        send_email(data['email'], data['subject'], data['body'])
        return jsonify({'message': 'Email sent successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to send email: {str(e)}'}), 500

@upload_bp.route('/generate-email', methods=['POST'])
def generate_email():
    data = request.get_json()
    if not data or 'task' not in data or 'recipient' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        email = generate_email_from_task(data['task'], data['recipient'])
        return jsonify(email)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
