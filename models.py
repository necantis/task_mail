from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    recipient = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))

class PDFAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    analysis = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('analyses', lazy=True))

class GeneratedEmail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('emails', lazy=True))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    subject = db.Column(db.String(255))
    status = db.Column(db.String(20), default='draft')  # draft, sent, failed
    sent_at = db.Column(db.DateTime)
    
    # Metrics
    opens = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    replies = db.Column(db.Integer, default=0)
    bounces = db.Column(db.Integer, default=0)

class EmailEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.Integer, db.ForeignKey('generated_email.id'), nullable=False)
    event_type = db.Column(db.String(20), nullable=False)  # open, click, reply, bounce
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    event_metadata = db.Column(db.JSON)  # Additional event data (e.g., link clicked, device info)
    
    email = db.relationship('GeneratedEmail', backref=db.backref('events', lazy=True))
