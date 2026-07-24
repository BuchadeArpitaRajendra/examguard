import sqlite3
from datetime import datetime
from init_db import get_db_connection

class DatabaseHelper:
    """Helper class for database operations"""
    
    @staticmethod
    def add_candidate(name, email, password, photo_path=None):
        """Add a new candidate to database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO candidate (name, email, password, photo_path)
                VALUES (?, ?, ?, ?)
            ''', (name, email, password, photo_path))
            
            conn.commit()
            candidate_id = cursor.lastrowid
            conn.close()
            return candidate_id
        except sqlite3.IntegrityError as e:
            conn.close()
            raise Exception(f"Email '{email}' already exists!")
    
    @staticmethod
    def get_candidate_by_email(email):
        """Get candidate by email"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM candidate WHERE email = ?', (email,))
        candidate = cursor.fetchone()
        conn.close()
        return candidate
    
    @staticmethod
    def get_candidate_by_id(candidate_id):
        """Get candidate by ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM candidate WHERE candidate_id = ?', (candidate_id,))
        candidate = cursor.fetchone()
        conn.close()
        return candidate
    
    @staticmethod
    def create_session(candidate_id):
        """Create a new session for candidate"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO session (candidate_id, status)
            VALUES (?, 'active')
        ''', (candidate_id,))
        
        conn.commit()
        session_id = cursor.lastrowid
        conn.close()
        return session_id
    
    @staticmethod
    def end_session(session_id):
        """End a session"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE session 
            SET end_time = CURRENT_TIMESTAMP, status = 'completed'
            WHERE session_id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_active_session(candidate_id):
        """Get active session for candidate"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM session 
            WHERE candidate_id = ? AND status = 'active'
            ORDER BY start_time DESC LIMIT 1
        ''', (candidate_id,))
        
        session = cursor.fetchone()
        conn.close()
        return session
    
    @staticmethod
    def get_all_candidates():
        """Get all candidates"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM candidate ORDER BY name')
        candidates = cursor.fetchall()
        conn.close()
        return candidates
    
    @staticmethod
    def get_all_sessions():
        """Get all sessions with candidate names"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.*, c.name, c.email 
            FROM session s
            JOIN candidate c ON s.candidate_id = c.candidate_id
            ORDER BY s.start_time DESC
        ''')
        sessions = cursor.fetchall()
        conn.close()
        return sessions
    
    @staticmethod
    def delete_candidate(candidate_id):
        """Delete candidate and their sessions"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM session WHERE candidate_id = ?', (candidate_id,))
            cursor.execute('DELETE FROM candidate WHERE candidate_id = ?', (candidate_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            return False