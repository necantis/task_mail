from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from utils import process_excel, process_word_document, process_google_sheet, analyze_documents, generate_email
from models import Task, GeneratedEmail, EmailEvent
from extensions import db
from sqlalchemy import func
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get overall statistics
    total_emails = GeneratedEmail.query.filter_by(user_id=current_user.id).count()
    sent_emails = GeneratedEmail.query.filter_by(user_id=current_user.id, status='sent').count()
    total_opens = db.session.query(func.sum(GeneratedEmail.opens))\
        .filter_by(user_id=current_user.id).scalar() or 0
    total_clicks = db.session.query(func.sum(GeneratedEmail.clicks))\
        .filter_by(user_id=current_user.id).scalar() or 0
    total_replies = db.session.query(func.sum(GeneratedEmail.replies))\
        .filter_by(user_id=current_user.id).scalar() or 0
    
    # Get recent emails (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_emails = GeneratedEmail.query\
        .filter(GeneratedEmail.user_id == current_user.id,
                GeneratedEmail.created_at >= thirty_days_ago)\
        .order_by(GeneratedEmail.created_at.desc())\
        .all()
    
    # Calculate engagement rates
    open_rate = (total_opens / sent_emails * 100) if sent_emails > 0 else 0
    click_rate = (total_clicks / sent_emails * 100) if sent_emails > 0 else 0
    
    return render_template('dashboard.html',
                         total_emails=total_emails,
                         sent_emails=sent_emails,
                         total_opens=total_opens,
                         total_clicks=total_clicks,
                         total_replies=total_replies,
                         open_rate=round(open_rate, 2),
                         click_rate=round(click_rate, 2),
                         recent_emails=recent_emails)

@main_bp.route('/track_email_event/<int:email_id>/<event_type>')
def track_email_event(email_id, event_type):
    if event_type not in ['open', 'click', 'reply', 'bounce']:
        return jsonify({'error': 'Invalid event type'}), 400
        
    email = GeneratedEmail.query.get_or_404(email_id)
    
    # Record the event
    event = EmailEvent(
        email_id=email_id,
        event_type=event_type,
        event_metadata=request.args.to_dict()  # Using the renamed column
    )
    db.session.add(event)
    
    # Update email metrics
    if event_type == 'open':
        email.opens += 1
    elif event_type == 'click':
        email.clicks += 1
    elif event_type == 'reply':
        email.replies += 1
    elif event_type == 'bounce':
        email.bounces += 1
    
    db.session.commit()
    
    return '', 204  # No content response
