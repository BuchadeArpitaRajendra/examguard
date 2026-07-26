import sqlite3
import os

# Database path
DB_PATH = 'instance/examguard.db'

def get_db_connection():
    """Create and return a database connection"""
    # Ensure instance folder exists
    os.makedirs('instance', exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db():
    """Initialize database tables if they don't exist"""
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
    
    # Create Event Log Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_log (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            remarks TEXT,
            event_data TEXT,
            FOREIGN KEY (session_id) REFERENCES session(session_id),
            FOREIGN KEY (candidate_id) REFERENCES candidate(candidate_id)
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_session ON event_log(session_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_candidate ON event_log(candidate_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON event_log(event_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_event_timestamp ON event_log(timestamp)')
    
    conn.commit()
    conn.close()
    print("✅ Database tables initialized successfully!")