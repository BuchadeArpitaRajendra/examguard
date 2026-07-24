import sqlite3
from init_db import get_db_connection

def view_tables():
    """Display all tables in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\n📊 Tables in database:")
    for table in tables:
        print(f"  📋 {table['name']}")
    
    conn.close()

def view_table_schema(table_name):
    """Show schema of a specific table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    print(f"\n📐 Schema for table: {table_name}")
    print("-" * 50)
    print(f"{'Column':<20} {'Type':<15} {'Constraints'}")
    print("-" * 50)
    
    for col in columns:
        constraints = []
        if col['notnull']:
            constraints.append('NOT NULL')
        if col['pk']:
            constraints.append('PRIMARY KEY')
        
        print(f"{col['name']:<20} {col['type']:<15} {', '.join(constraints)}")
    
    conn.close()

def test_insert():
    """Test inserting sample data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Insert sample candidate
        cursor.execute('''
            INSERT INTO candidate (name, email, password, photo_path)
            VALUES (?, ?, ?, ?)
        ''', ('John Doe', 'john@example.com', 'hashed_password123', '/static/photos/john.jpg'))
        
        conn.commit()
        print("✅ Sample candidate inserted successfully!")
        
        # Get the inserted candidate
        cursor.execute("SELECT * FROM candidate WHERE email = 'john@example.com'")
        candidate = cursor.fetchone()
        print(f"   📝 Candidate: {candidate['name']} (ID: {candidate['candidate_id']})")
        
    except sqlite3.IntegrityError as e:
        print(f"⚠️  Error inserting sample data: {e}")
        print("   (Sample data might already exist)")
    
    finally:
        conn.close()

if __name__ == '__main__':
    view_tables()
    view_table_schema('candidate')
    view_table_schema('session')
    test_insert()