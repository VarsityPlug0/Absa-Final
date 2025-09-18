#!/usr/bin/env python3
"""
Database Setup Script for ABSA Banking System
Initializes the SQLite database for local development
"""

import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_database():
    """Initialize the database with tables"""
    try:
        # Import after adding path
        from app import app, db
        
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Print database location
            db_path = app.config['SQLALCHEMY_DATABASE_URI']
            if db_path.startswith('sqlite:///'):
                local_path = db_path.replace('sqlite:///', '')
                print(f"📁 Database file: {local_path}")
            else:
                print(f"🔗 Database URL: {db_path}")
                
            return True
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Setting up ABSA Banking System Database...")
    print("=" * 50)
    
    if setup_database():
        print("=" * 50)
        print("🎉 Database setup completed successfully!")
        print("You can now run the application with: python app.py")
    else:
        print("=" * 50)
        print("💥 Database setup failed!")
        sys.exit(1)