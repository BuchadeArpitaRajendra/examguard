from database import get_db_connection
import datetime

class EventLogger:
    """Handle all event logging operations"""
    
    @staticmethod
    def log_event(session_id, candidate_id, event_type, remarks=None, event_data=None):
        """Log an event to the database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO event_log (session_id, candidate_id, event_type, remarks, event_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, candidate_id, event_type, remarks, event_data))
            
            conn.commit()
            event_id = cursor.lastrowid
            conn.close()
            
            return event_id
            
        except Exception as e:
            print(f"Error logging event: {e}")
            return None
    
    @staticmethod
    def get_session_events(session_id):
        """Get all events for a session"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM event_log 
                WHERE session_id = ? 
                ORDER BY timestamp ASC
            ''', (session_id,))
            
            events = cursor.fetchall()
            conn.close()
            return events
            
        except Exception as e:
            print(f"Error getting events: {e}")
            return []
    
    @staticmethod
    def get_candidate_events(candidate_id):
        """Get all events for a candidate"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM event_log 
                WHERE candidate_id = ? 
                ORDER BY timestamp DESC
            ''', (candidate_id,))
            
            events = cursor.fetchall()
            conn.close()
            return events
            
        except Exception as e:
            print(f"Error getting events: {e}")
            return []
    
    @staticmethod
    def get_recent_events(candidate_id, limit=100):
        """Get recent events for a candidate"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM event_log 
                WHERE candidate_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (candidate_id, limit))
            
            events = cursor.fetchall()
            conn.close()
            return events
            
        except Exception as e:
            print(f"Error getting recent events: {e}")
            return []
    
    @staticmethod
    def get_events_by_type(candidate_id, event_type):
        """Get events of a specific type for a candidate"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM event_log 
                WHERE candidate_id = ? AND event_type = ?
                ORDER BY timestamp DESC
            ''', (candidate_id, event_type))
            
            events = cursor.fetchall()
            conn.close()
            return events
            
        except Exception as e:
            print(f"Error getting events by type: {e}")
            return []
    
    @staticmethod
    def get_event_count(candidate_id, event_type=None):
        """Get count of events for a candidate"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if event_type:
                cursor.execute('''
                    SELECT COUNT(*) FROM event_log 
                    WHERE candidate_id = ? AND event_type = ?
                ''', (candidate_id, event_type))
            else:
                cursor.execute('''
                    SELECT COUNT(*) FROM event_log 
                    WHERE candidate_id = ?
                ''', (candidate_id,))
            
            count = cursor.fetchone()[0]
            conn.close()
            return count
            
        except Exception as e:
            print(f"Error getting event count: {e}")
            return 0
    
    @staticmethod
    def get_event_statistics(candidate_id):
        """Get event statistics for a candidate"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    event_type,
                    COUNT(*) as count,
                    MIN(timestamp) as first_occurrence,
                    MAX(timestamp) as last_occurrence
                FROM event_log 
                WHERE candidate_id = ?
                GROUP BY event_type
                ORDER BY count DESC
            ''', (candidate_id,))
            
            stats = cursor.fetchall()
            conn.close()
            return stats
            
        except Exception as e:
            print(f"Error getting event statistics: {e}")
            return []