from flask import Blueprint, render_template, request, jsonify
from utils import process_excel, analyze_pdf, generate_email

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
        tasks = process_excel(file)
        return jsonify({'tasks': tasks})
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
    generated_email = generate_email(task, email)
    return jsonify({'email': generated_email})
