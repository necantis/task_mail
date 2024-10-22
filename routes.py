from flask import Blueprint, render_template, request, jsonify
from utils import process_excel, analyze_pdf, generate_email
from models import Task
from extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/upload_excel', methods=['POST'])
def upload_excel():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.endswith('.xlsx'):
        try:
            tasks = process_excel(file, add_to_db=False)
            return jsonify({'tasks': tasks})
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
    return jsonify({'error': 'Invalid file format'}), 400

@main_bp.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'files' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({'error': 'No selected files'}), 400
    
    pdf_files = [file for file in files if file.filename.endswith('.pdf')]
    if not pdf_files:
        return jsonify({'error': 'No valid PDF files found'}), 400
    
    analysis = analyze_pdf(pdf_files)
    return jsonify({'analysis': analysis})

@main_bp.route('/generate_email', methods=['POST'])
def generate_email_route():
    data = request.json
    task = data.get('task')
    email = data.get('email')
    recipient = data.get('recipient')
    if not task or not email or not recipient:
        return jsonify({'error': 'Missing task, email, or recipient'}), 400
    
    # Add the selected task to the database
    new_task = Task(description=task, email=email, recipient=recipient)
    db.session.add(new_task)
    db.session.commit()
    
    generated_email = generate_email(task, email, recipient)
    return jsonify({'email': generated_email})
