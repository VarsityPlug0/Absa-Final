# Deployment Guide - ABSA Banking Authentication System

## 🚀 Deploy to Render (Recommended)

### Option 1: One-Click Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/VarsityPlug0/Absa-Final)

### Option 2: Manual Deployment

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up/login with GitHub

2. **Connect Repository**
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select the `Absa-Final` repository

3. **Configure Service**
   - **Name**: `absa-banking-auth`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free (or paid for better performance)

4. **Environment Variables** (Auto-configured via render.yaml)
   - `FLASK_ENV=production`
   - `ADMIN_USERNAME=admin`
   - `ADMIN_PASSWORD=admin123`
   - `SECRET_KEY` (auto-generated)

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (usually 2-5 minutes)

## 🌐 Access Your Deployed Application

After deployment, you'll get a URL like: `https://absa-banking-auth.onrender.com`

**Access Points:**
- **Main Application**: `https://your-app-name.onrender.com`
- **Admin Panel**: `https://your-app-name.onrender.com/admin`
- **Health Check**: `https://your-app-name.onrender.com/health`

**Admin Credentials:**
- Username: `admin`
- Password: `admin123`

## 🔧 Configuration Details

### Automatic Configuration (render.yaml)
The `render.yaml` file automatically configures:
```yaml
services:
  - type: web
    name: absa-banking-auth
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: FLASK_ENV
        value: production
      - key: ADMIN_USERNAME
        value: admin
      - key: ADMIN_PASSWORD
        value: admin123
      - key: SECRET_KEY
        generateValue: true
```

### Manual Environment Variables (if needed)
If you want to customize, add these in Render dashboard:

| Variable | Value | Description |
|----------|-------|-------------|
| `FLASK_ENV` | `production` | Sets production mode |
| `ADMIN_USERNAME` | `admin` | Admin login username |
| `ADMIN_PASSWORD` | `admin123` | Admin login password |
| `SECRET_KEY` | (auto-generated) | Flask session security |
| `PORT` | (auto-set by Render) | Application port |

## 🛠 Alternative Deployment Options

### Deploy to Heroku

1. **Install Heroku CLI**
   ```bash
   # Download from heroku.com/cli
   ```

2. **Login and Create App**
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set ADMIN_USERNAME=admin
   heroku config:set ADMIN_PASSWORD=admin123
   heroku config:set SECRET_KEY=your-secret-key-here
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

### Deploy to Railway

1. **Connect Repository**
   - Go to [railway.app](https://railway.app)
   - Connect GitHub repository

2. **Environment Variables**
   ```
   FLASK_ENV=production
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=admin123
   ```

3. **Deploy** - Automatic deployment from GitHub

## 📊 Post-Deployment Verification

### 1. Health Check
Visit: `https://your-app.onrender.com/health`

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:30:00",
  "version": "1.0.0",
  "pending_requests": 0
}
```

### 2. Test Authentication Flow
1. Go to main page
2. Fill customer information
3. Check admin panel for pending requests
4. Approve and continue through flow

### 3. Test Admin Features
1. Login to admin panel
2. View data history
3. Test export functionality

## 🔒 Security Considerations for Production

### Essential Security Updates
1. **Change Admin Credentials**
   ```bash
   # In Render dashboard, update:
   ADMIN_USERNAME=your-secure-username
   ADMIN_PASSWORD=your-secure-password
   ```

2. **Strong Secret Key**
   ```bash
   # Generate strong secret key
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **Environment Variables**
   - Never commit secrets to Git
   - Use Render's environment variable system
   - Regenerate SECRET_KEY regularly

### Recommended Production Settings
```bash
# In Render dashboard
FLASK_ENV=production
ADMIN_USERNAME=your-admin-user
ADMIN_PASSWORD=complex-secure-password-123!
SECRET_KEY=generated-32-character-hex-string
```

## 📈 Monitoring & Maintenance

### Built-in Monitoring
- **Health Endpoint**: `/health` for uptime monitoring
- **Admin Dashboard**: Real-time request statistics
- **Error Handling**: Custom error pages

### Render Features
- **Automatic HTTPS**: SSL certificates included
- **Auto-scaling**: Handles traffic spikes
- **Logs**: View application logs in dashboard
- **Metrics**: CPU, memory, and request metrics

### Maintenance Tasks
1. **Monitor Logs**: Check for errors in Render dashboard
2. **Update Dependencies**: Keep requirements.txt updated
3. **Backup Data**: Export captured data regularly
4. **Security Updates**: Update admin credentials periodically

## 🆘 Troubleshooting

### Common Issues

1. **Build Failed**
   ```bash
   # Check Python version in runtime.txt
   python-3.11.0
   ```

2. **App Won't Start**
   ```bash
   # Verify start command in render.yaml
   startCommand: gunicorn app:app
   ```

3. **404 Errors**
   ```bash
   # Check route definitions in app.py
   # Ensure templates/ directory is included
   ```

4. **Admin Login Issues**
   ```bash
   # Verify environment variables are set
   # Check admin credentials in Render dashboard
   ```

### Debug Steps
1. Check Render logs for error messages
2. Verify all environment variables are set
3. Test locally with same environment variables
4. Check GitHub repository for missing files

## 📞 Support

- **Render Support**: [render.com/support](https://render.com/support)
- **Documentation**: Check README.md and DEMO_GUIDE.md
- **Health Check**: Use `/health` endpoint for monitoring

---

**🎉 Your ABSA Banking System is now ready for production deployment!**

The application includes:
- ✅ Production-ready configuration
- ✅ Environment variable support
- ✅ Health monitoring
- ✅ Error handling
- ✅ Security best practices
- ✅ Automatic scaling support