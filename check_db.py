import sqlite3
from init_db import get_db_connection

def check_registered_candidates():
    """Display all registered candidates"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("📊 REGISTERED CANDIDATES")
    print("="*60)
    
    cursor.execute('''
        SELECT 
            candidate_id,
            name,
            email,
            photo_path,
            created_at
        FROM candidate
        ORDER BY created_at DESC
    ''')
    
    candidates = cursor.fetchall()
    
    if not candidates:
        print("❌ No candidates registered yet.")
    else:
        print(f"✅ Found {len(candidates)} registered candidates:\n")
        print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'Registered'}")
        print("-"*70)
        
        for c in candidates:
            created = c['created_at'][:19] if c['created_at'] else 'N/A'
            print(f"{c['candidate_id']:<5} {c['name']:<20} {c['email']:<30} {created}")
    
    conn.close()

def check_sessions():
    """Display all sessions"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("📋 EXAM SESSIONS")
    print("="*60)
    
    cursor.execute('''
        SELECT 
            s.session_id,
            s.candidate_id,
            c.name as candidate_name,
            s.start_time,
            s.end_time,
            s.status
        FROM session s
        JOIN candidate c ON s.candidate_id = c.candidate_id
        ORDER BY s.start_time DESC
    ''')
    
    sessions = cursor.fetchall()
    
    if not sessions:
        print("❌ No sessions found.")
    else:
        print(f"✅ Found {len(sessions)} sessions:\n")
        print(f"{'Session':<8} {'Candidate':<20} {'Status':<10} {'Start Time'}")
        print("-"*70)
        
        for s in sessions:
            start = s['start_time'][:19] if s['start_time'] else 'N/A'
            print(f"{s['session_id']:<8} {s['candidate_name']:<20} {s['status']:<10} {start}")
    
    conn.close()

def get_candidate_details(email):
    """Get specific candidate details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            candidate_id,
            name,
            email,
            photo_path,
            created_at
        FROM candidate
        WHERE email = ?
    ''', (email,))
    
    candidate = cursor.fetchone()
    conn.close()
    
    if candidate:
        print(f"\n👤 Candidate Details for {email}:")
        print(f"   ID: {candidate['candidate_id']}")
        print(f"   Name: {candidate['name']}")
        print(f"   Email: {candidate['email']}")
        print(f"   Photo: {candidate['photo_path'] or 'No photo'}")
        print(f"   Registered: {candidate['created_at']}")
    else:
        print(f"❌ No candidate found with email: {email}")
    
    return candidate

if __name__ == '__main__':
    check_registered_candidates()
    check_sessions()
    
    # Check specific candidate (optional)
    # get_candidate_details('john@example.com')