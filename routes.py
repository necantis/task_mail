from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from utils import process_excel, process_word_document, process_google_sheet, analyze_documents, generate_email
from models import Task
from extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@main_bp.route('/upload_excel', methods=['POST'])
@login_required
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

@main_bp.route('/upload_word', methods=['POST'])
@login_required
def upload_word():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.endswith('.docx'):
        try:
            tasks = process_word_document(file, add_to_db=False)
            return jsonify({'tasks': tasks})
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
    return jsonify({'error': 'Invalid file format'}), 400

@main_bp.route('/upload_gsheet', methods=['POST'])
@login_required
def upload_gsheet():
    sheet_id = request.form.get('sheetId')
    if not sheet_id:
        return jsonify({'error': 'No Google Sheet ID provided'}), 400
    try:
        tasks = process_google_sheet(sheet_id, add_to_db=False)
        return jsonify({'tasks': tasks})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@main_bp.route('/analyze_documents', methods=['POST'])
@login_required
def analyze_documents_route():
    if 'doc1' not in request.files or 'doc2' not in request.files:
        return jsonify({'error': 'Both documents are required'}), 400
    doc1 = request.files['doc1']
    doc2 = request.files['doc2']
    
    if doc1.filename == '' or doc2.filename == '':
        return jsonify({'error': 'Both documents must be selected'}), 400
        
    allowed_extensions = {'.pdf', '.docx'}
    if not (any(doc1.filename.endswith(ext) for ext in allowed_extensions) and 
            any(doc2.filename.endswith(ext) for ext in allowed_extensions)):
        return jsonify({'error': 'Invalid file format. Only PDF and DOCX files are supported.'}), 400
        
    try:
        analysis = analyze_documents([doc1, doc2])
        return jsonify({'analysis': analysis})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@main_bp.route('/generate_email', methods=['POST'])
@login_required
def generate_email_route():
    data = request.json
    task = data.get('task')
    email = data.get('email')
    recipient = data.get('recipient')
    if not task or not email or not recipient:
        return jsonify({'error': 'Missing task, email, or recipient'}), 400
    
    new_task = Task(description=task, email=email, recipient=recipient, user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()
    
    generated_email = generate_email(task, email, recipient)
    return jsonify({'email': generated_email})
