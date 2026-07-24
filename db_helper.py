import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from init_db import get_db_connection

class CandidateManager:
    """Handle all candidate-related database operations"""
    
    @staticmethod
    def register_candidate(name, email, password, photo_path=None):
        """Register a new candidate"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            
            cursor.execute('''
                INSERT INTO candidate (name, email, password, photo_path)
                VALUES (?, ?, ?, ?)
            ''', (name, email, hashed_password, photo_path))
            
            conn.commit()
            candidate_id = cursor.lastrowid
            conn.close()
            return candidate_id
            
        except sqlite3.IntegrityError:
            conn.close()
            raise Exception("Email already registered")
        except Exception as e:
            conn.close()
            raise Exception(f"Registration failed: {str(e)}")
    
    @staticmethod
    def authenticate_candidate(email, password):
        """Authenticate candidate login"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM candidate WHERE email = ?', (email,))
        candidate = cursor.fetchone()
        conn.close()
        
        if candidate and check_password_hash(candidate['password'], password):
            return dict(candidate)
        return None
    
    @staticmethod
    def get_candidate_by_email(email):
        """Get candidate by email"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM candidate WHERE email = ?', (email,))
        candidate = cursor.fetchone()
        conn.close()
        
        return dict(candidate) if candidate else None
    
    @staticmethod
    def get_candidate_by_id(candidate_id):
        """Get candidate by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM candidate WHERE candidate_id = ?', (candidate_id,))
        candidate = cursor.fetchone()
        conn.close()
        
        return dict(candidate) if candidate else None
    
    @staticmethod
    def update_candidate(candidate_id, name=None, email=None, photo_path=None):
        """Update candidate details"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if name:
            updates.append("name = ?")
            params.append(name)
        if email:
            updates.append("email = ?")
            params.append(email)
        if photo_path:
            updates.append("photo_path = ?")
            params.append(photo_path)
        
        if not updates:
            return False
        
        params.append(candidate_id)
        query = f"UPDATE candidate SET {', '.join(updates)} WHERE candidate_id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        
        return affected > 0
    
    @staticmethod
    def delete_candidate(candidate_id):
        """Delete candidate and their sessions"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM session WHERE candidate_id = ?', (candidate_id,))
            cursor.execute('DELETE FROM candidate WHERE candidate_id = ?', (candidate_id,))
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            return affected > 0
        except Exception:
            conn.close()
            return False
    
    @staticmethod
    def get_all_candidates():
        """Get all candidates with session counts"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                c.*,
                COUNT(s.session_id) as session_count,
                MAX(s.start_time) as last_session
            FROM candidate c
            LEFT JOIN session s ON c.candidate_id = s.candidate_id
            GROUP BY c.candidate_id
            ORDER BY c.created_at DESC
        ''')
        
        candidates = cursor.fetchall()
        conn.close()
        return [dict(c) for c in candidates]

# Usage example
if __name__ == '__main__':
    # Register a new candidate
    try:
        id = CandidateManager.register_candidate(
            'Test User',
            'test@example.com',
            'SecurePass123'
        )
        print(f"✅ Registered with ID: {id}")
    except Exception as e:
        print(f"❌ {e}")
    
    # Authenticate
    user = CandidateManager.authenticate_candidate('test@example.com', 'SecurePass123')
    if user:
        print(f"✅ Login successful: {user['name']}")
    else:
        print("❌ Login failed")
    
    # Get all candidates
    candidates = CandidateManager.get_all_candidates()
    print(f"📊 Total candidates: {len(candidates)}")