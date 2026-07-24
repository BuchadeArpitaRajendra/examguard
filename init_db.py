import sqlite3
import os
from datetime import datetime

# Database path
DB_PATH = 'instance/examguard.db'

def get_db_connection():
    """Create and return a database connection"""
    # Ensure instance folder exists
    os.makedirs('instance', exist_ok=True)
    
    # Create connection
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def create_tables():
    """Create all database tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Candidate Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidate (
            candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            photo_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Session Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS session (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (candidate_id) REFERENCES candidate(candidate_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database tables created successfully!")
    print(f"📁 Database file: {DB_PATH}")

def test_connection():
    """Test database connection"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        conn.close()
        print(f"✅ SQLite version: {version}")
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Initializing ExamGuard Database...")
    test_connection()
    create_tables()
    print("🎉 Database setup complete!")