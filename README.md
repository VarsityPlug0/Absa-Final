# ABSA Banking Authentication System

A professional Flask-based banking authentication system that replicates the ABSA online banking experience with admin approval workflow.

## Features

### 🏦 Banking Authentication Flow
- **Login Page** - Professional ABSA-branded login interface
- **Customer Information** - Comprehensive user verification form
- **SurePhrase Authentication** - Secure phrase verification
- **PIN Entry** - 5-digit PIN verification
- **Multi-step Progress** - Visual progress indicators

### 👨‍💼 Admin Management System
- **Admin Dashboard** - Real-time approval management
- **Step-by-step Approval** - Each user step requires admin approval
- **Request Monitoring** - Live tracking of user authentication requests
- **Approval Statistics** - Daily approval/rejection metrics

### 🎨 Professional Design
- **ABSA Brand Colors** - Exact color matching (#8b1538, #ff6600)
- **Professional Icons** - Custom-designed icons for all sections
- **Responsive Layout** - Mobile-friendly design
- **Clean UI** - No emojis, professional banking appearance

## Technology Stack

- **Backend:** Flask 2.3.3
- **Frontend:** HTML5, CSS3, JavaScript
- **Deployment:** Render-ready with Gunicorn
- **Session Management:** Flask sessions
- **Real-time Updates:** JavaScript polling

## Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/absa-banking-auth.git
   cd absa-banking-auth
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Main application: http://127.0.0.1:5000
   - Admin panel: http://127.0.0.1:5000/admin

## Admin Credentials

**Default admin login:**
- Username: `admin`
- Password: `admin123`

> ⚠️ **Security Note:** Change these credentials in production by updating the `ADMIN_USERNAME` and `ADMIN_PASSWORD` variables in `app.py`.

## Deployment on Render

### Quick Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Manual Deployment

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create Render Web Service**
   - Connect your GitHub repository
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

3. **Environment Variables** (Optional)
   ```
   ADMIN_USERNAME=your_admin_username
   ADMIN_PASSWORD=your_secure_password
   FLASK_ENV=production
   ```

## Usage

### For Users (Testing Mode)
1. Visit the main page
2. Fill out any customer information (all fields required but any values accepted)
3. Enter any SurePhrase (minimum 3 characters)
4. Enter any 5-digit PIN
5. Wait for admin approval at each step
6. Final redirect to official ABSA website

### For Administrators
1. Navigate to `/admin`
2. Login with admin credentials
3. Monitor the dashboard for pending requests
4. Approve or reject user authentication steps
5. View daily statistics and metrics

## Project Structure

```
absa/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Render deployment config
├── runtime.txt           # Python version specification
├── .gitignore           # Git ignore patterns
├── static/
│   └── logo.png         # ABSA logo asset
└── templates/
    ├── base.html        # Base template
    ├── base_login.html  # Login-specific base
    ├── login.html       # Main login page
    ├── customer_info.html    # Customer information form
    ├── surephrase_auth.html  # SurePhrase authentication
    ├── pin_entry.html        # PIN entry form
    ├── waiting_approval.html # Approval waiting page
    ├── admin_login.html      # Admin login form
    └── admin_dashboard.html  # Admin dashboard
```

## Security Features

- **Session Management** - Secure Flask sessions
- **Rate Limiting** - Protection against brute force attacks
- **Admin Authentication** - Separate admin login system
- **Request Validation** - Input validation and sanitization
- **CSRF Protection** - Built-in Flask security

## Customization

### Brand Colors
Update CSS variables in templates:
```css
:root {
  --primary: #8b1538;  /* ABSA Red */
  --accent: #ff6600;   /* ABSA Orange */
  --border: #ddd;
  --text-dark: #333;
  --text-light: #666;
}
```

### Admin Credentials
Update in `app.py`:
```python
ADMIN_USERNAME = 'your_username'
ADMIN_PASSWORD = 'your_secure_password'
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is for educational purposes only. ABSA Bank branding and design elements are used for demonstration purposes.

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the admin dashboard for system status
- Review the Flask application logs

---

**⚡ Live Demo:** [Deploy on Render](https://render.com/deploy)  
**🔧 Admin Panel:** `your-domain.com/admin`  
**📱 Mobile Friendly:** Responsive design for all devices