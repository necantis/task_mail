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
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.endswith('.pdf'):
        analysis = analyze_pdf(file)
        return jsonify({'analysis': analysis})
    return jsonify({'error': 'Invalid file format'}), 400

@main_bp.route('/generate_email', methods=['POST'])
def generate_email_route():
    data = request.json
    task = data.get('task')
    email = data.get('email')
    if not task or not email:
        return jsonify({'error': 'Missing task or email'}), 400
    
    # Add the selected task to the database
    new_task = Task(description=task, email=email)
    db.session.add(new_task)
    db.session.commit()
    
    generated_email = generate_email(task, email)
    return jsonify({'email': generated_email})
