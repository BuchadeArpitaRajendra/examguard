import csv
import sqlite3
from app import get_db_connection
from werkzeug.security import generate_password_hash

def import_candidates_from_csv(filename='sample_candidates.csv'):
    """Import candidates from CSV to database"""
    
    try:
        # Read CSV
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            candidates = list(reader)
        
        if not candidates:
            print("❌ No data found in CSV!")
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        successful = 0
        skipped = 0
        
        for c in candidates:
            try:
                # Check if email already exists
                cursor.execute('SELECT candidate_id FROM candidate WHERE email = ?', (c['email'],))
                if cursor.fetchone():
                    print(f"⚠️ Skipping {c['email']} - already exists")
                    skipped += 1
                    continue
                
                # Generate default password
                default_password = 'Default@123'
                hashed_password = generate_password_hash(default_password, method='pbkdf2:sha256')
                
                # Insert candidate
                cursor.execute('''
                    INSERT INTO candidate (name, email, password, photo_path)
                    VALUES (?, ?, ?, ?)
                ''', (c['name'], c['email'], hashed_password, None))
                
                candidate_id = cursor.lastrowid
                
                # Create sample session for some candidates
                if candidate_id % 2 == 0:  # Every 2nd candidate has a session
                    import random
                    from datetime import datetime, timedelta
                    
                    # Random session status
                    status = random.choice(['active', 'completed', 'paused'])
                    
                    if status == 'active':
                        cursor.execute('''
                            INSERT INTO session (candidate_id, status, start_time)
                            VALUES (?, ?, CURRENT_TIMESTAMP)
                        ''', (candidate_id, status))
                    else:
                        # Completed or paused with end time
                        start_time = datetime.now() - timedelta(days=random.randint(1, 30))
                        end_time = start_time + timedelta(hours=random.randint(1, 3))
                        cursor.execute('''
                            INSERT INTO session (candidate_id, start_time, end_time, status)
                            VALUES (?, ?, ?, ?)
                        ''', (candidate_id, start_time, end_time, status))
                
                successful += 1
                
            except Exception as e:
                print(f"❌ Error importing {c.get('email', 'unknown')}: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        print("\n" + "="*60)
        print("📊 IMPORT SUMMARY")
        print("="*60)
        print(f"✅ Successfully imported: {successful} candidates")
        print(f"⚠️ Skipped: {skipped} candidates (duplicate emails)")
        print(f"📁 File: {filename}")
        print("="*60)
        
        return True
        
    except FileNotFoundError:
        print(f"❌ File '{filename}' not found!")
        print("💡 First run: python generate_candidates.py")
        return False
    except Exception as e:
        print(f"❌ Error importing CSV: {e}")
        return False

def check_imported_candidates():
    """Check how many candidates were imported"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM candidate')
    count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM session')
    session_count = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n📊 Database Status:")
    print(f"   Candidates: {count}")
    print(f"   Sessions: {session_count}")

if __name__ == '__main__':
    # Import candidates from CSV
    import_candidates_from_csv('sample_candidates.csv')
    
    # Check results
    check_imported_candidates()