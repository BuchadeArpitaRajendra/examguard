from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, init_db
from event_logger import EventLogger
from event_types import EventTypes
import sqlite3
import os
import re
import base64
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'

# ===== HELPER FUNCTIONS =====

def validate_email(email):
    """Validate email format using regex"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    return True, "Password is strong"

import base64
import os
from datetime import datetime

def save_photo(photo_data, candidate_id):
    """Save base64 photo data to file and return path"""
    try:
        # Create photos directory
        photos_dir = os.path.join('static', 'photos')
        os.makedirs(photos_dir, exist_ok=True)
        
        # Debug: Print photo data info
        print(f"📸 Photo data length: {len(photo_data) if photo_data else 0}")
        
        if not photo_data:
            print("❌ No photo data received")
            return None
        
        # Remove the data URL prefix if present
        if 'base64' in photo_data:
            if ',' in photo_data:
                photo_data = photo_data.split(',')[1]
            else:
                print("❌ Invalid photo data format")
                return None
        
        # Decode base64 data
        try:
            image_data = base64.b64decode(photo_data)
        except Exception as e:
            print(f"❌ Failed to decode base64: {e}")
            return None
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"candidate_{candidate_id}_{timestamp}.jpg"
        filepath = os.path.join(photos_dir, filename)
        
        # Save image
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        print(f"✅ Photo saved: {filepath}")
        
        # Return relative path for database
        return f"static/photos/{filename}"
        
    except Exception as e:
        print(f"❌ Error saving photo: {e}")
        return None

# ===== SESSION MANAGEMENT FUNCTIONS =====

def create_session(candidate_id):
    """Create a new exam session for a candidate"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if there's an active session already
        cursor.execute('''
            SELECT session_id FROM session 
            WHERE candidate_id = ? AND status IN ('active', 'paused')
        ''', (candidate_id,))
        
        existing = cursor.fetchone()
        if existing:
            conn.close()
            return None, "You already have an active session. Please end it first."
        
        # Create new session
        cursor.execute('''
            INSERT INTO session (candidate_id, status, start_time)
            VALUES (?, 'active', CURRENT_TIMESTAMP)
        ''', (candidate_id,))
        
        conn.commit()
        session_id = cursor.lastrowid
        conn.close()
        
        return session_id, "Session started successfully!"
        
    except Exception as e:
        return None, f"Error creating session: {str(e)}"

def pause_session(session_id):
    """Pause an active session"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT status FROM session WHERE session_id = ?
        ''', (session_id,))
        
        session = cursor.fetchone()
        if not session:
            conn.close()
            return False, "Session not found."
        
        if session['status'] != 'active':
            conn.close()
            return False, f"Session is already {session['status']}."
        
        cursor.execute('''
            UPDATE session 
            SET status = 'paused' 
            WHERE session_id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
        return True, "Session paused successfully!"
        
    except Exception as e:
        return False, f"Error pausing session: {str(e)}"

def resume_session(session_id):
    """Resume a paused session"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT status FROM session WHERE session_id = ?
        ''', (session_id,))
        
        session = cursor.fetchone()
        if not session:
            conn.close()
            return False, "Session not found."
        
        if session['status'] != 'paused':
            conn.close()
            return False, f"Session is not paused (current status: {session['status']})."
        
        cursor.execute('''
            UPDATE session 
            SET status = 'active' 
            WHERE session_id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
        return True, "Session resumed successfully!"
        
    except Exception as e:
        return False, f"Error resuming session: {str(e)}"

def end_session(session_id):
    """End a session"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT status FROM session WHERE session_id = ?
        ''', (session_id,))
        
        session = cursor.fetchone()
        if not session:
            conn.close()
            return False, "Session not found."
        
        if session['status'] == 'completed':
            conn.close()
            return False, "Session is already completed."
        
        cursor.execute('''
            UPDATE session 
            SET status = 'completed', end_time = CURRENT_TIMESTAMP
            WHERE session_id = ?
        ''', (session_id,))
        
        conn.commit()
        conn.close()
        return True, "Session ended successfully!"
        
    except Exception as e:
        return False, f"Error ending session: {str(e)}"

# ===== ROUTES =====

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Candidate Registration Page"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        terms = request.form.get('terms', '')
        photo_data = request.form.get('photo_data', '')
        print(f"📸 Photo data received: {len(photo_data) if photo_data else 0} characters")
        if photo_data:
            print(f"📸 Photo data starts with: {photo_data[:50]}...")
        else:
            print("❌ No photo data received in form")
        # ===== VALIDATION =====
        errors = []
        
        # Check for empty fields
        if not name:
            errors.append("Full name is required.")
        elif len(name) < 2:
            errors.append("Name must be at least 2 characters long.")
        
        if not email:
            errors.append("Email address is required.")
        elif not validate_email(email):
            errors.append("Please enter a valid email address.")
        
        if not password:
            errors.append("Password is required.")
        else:
            is_valid, message = validate_password(password)
            if not is_valid:
                errors.append(message)
        
        if not confirm_password:
            errors.append("Please confirm your password.")
        elif password and confirm_password and password != confirm_password:
            errors.append("Passwords do not match.")
        
        if not terms:
            errors.append("You must agree to the Terms & Conditions.")
        
        if not photo_data:
            errors.append("Please capture your photo.")
        
        # If there are errors, flash them and return to form
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        # ===== CHECK FOR DUPLICATE EMAIL =====
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if email already exists
            cursor.execute('SELECT candidate_id FROM candidate WHERE email = ?', (email,))
            existing = cursor.fetchone()
            
            if existing:
                conn.close()
                flash('❌ This email is already registered. Please use a different email or login.', 'error')
                return render_template('register.html')
            
            # ===== STORE IN DATABASE =====
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            
            cursor.execute('''
                INSERT INTO candidate (name, email, password, photo_path)
                VALUES (?, ?, ?, ?)
            ''', (name, email, hashed_password, None))
            
            conn.commit()
            candidate_id = cursor.lastrowid
            
            # Save photo and get path
            
            # SAVE PHOTO AFTER INSERT
            if photo_data:
                photo_path = save_photo(photo_data, candidate_id)
                if photo_path:
                    cursor.execute('''
                        UPDATE candidate 
                        SET photo_path = ? 
                        WHERE candidate_id = ?
                    ''', (photo_path, candidate_id))
                    conn.commit()
                    print(f"✅ Photo saved: {photo_path}")
                else:
                    print("❌ Failed to save photo")
            else:
                print("❌ No photo data received")
            
            # Auto-login after registration
            session['candidate_id'] = candidate_id
            session['candidate_name'] = name
            session['candidate_email'] = email
            
            flash(f'✅ Registration successful! Welcome, {name}!', 'success')
            return redirect(url_for('dashboard'))
            
        except sqlite3.IntegrityError:
            conn.close()
            flash('❌ This email is already registered. Please use a different email or login.', 'error')
            return render_template('register.html')
        except Exception as e:
            flash(f'❌ An error occurred during registration: {str(e)}', 'error')
            return render_template('register.html')
    
    # GET request - show registration form
    return render_template('register.html')
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Page"""
    # If user is already logged in, redirect to dashboard
    if 'candidate_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('login.html')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get candidate by email
            cursor.execute('SELECT * FROM candidate WHERE email = ?', (email,))
            candidate = cursor.fetchone()
            conn.close()
            
            if candidate:
                # Check password
                if check_password_hash(candidate['password'], password):
                    # Login successful
                    session['candidate_id'] = candidate['candidate_id']
                    session['candidate_name'] = candidate['name']
                    session['candidate_email'] = candidate['email']
                    
                    flash(f'✅ Welcome back, {candidate["name"]}!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('❌ Invalid password. Please try again.', 'error')
                    return render_template('login.html')
            else:
                flash('❌ No account found with this email. Please register.', 'error')
                return render_template('login.html')
                
        except Exception as e:
            flash(f'❌ Login error: {str(e)}', 'error')
            return render_template('login.html')
    
    # GET request - show login form
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Candidate Dashboard with Session Management"""
    if 'candidate_id' not in session:
        flash('Please login to access your dashboard.', 'warning')
        return redirect(url_for('login'))
    
    candidate_id = session['candidate_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get candidate details
        cursor.execute('SELECT * FROM candidate WHERE candidate_id = ?', (candidate_id,))
        candidate_data = cursor.fetchone()
        
        if not candidate_data:
            flash('Candidate not found.', 'error')
            return redirect(url_for('logout'))
        
        # Get all sessions
        cursor.execute('SELECT * FROM session WHERE candidate_id = ? ORDER BY start_time DESC', (candidate_id,))
        sessions = cursor.fetchall()
        
        # Get active session
        cursor.execute('''
            SELECT * FROM session 
            WHERE candidate_id = ? AND status IN ('active', 'paused')
            ORDER BY start_time DESC LIMIT 1
        ''', (candidate_id,))
        active_session = cursor.fetchone()
        
        # If active session exists, store in session
        if active_session:
            session['exam_session_id'] = active_session['session_id']
        elif 'exam_session_id' in session:
            session.pop('exam_session_id', None)
        
        # Get statistics
        cursor.execute('SELECT COUNT(*) FROM session WHERE candidate_id = ?', (candidate_id,))
        total_sessions = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT COUNT(*) FROM session WHERE candidate_id = ? AND status = "active"', (candidate_id,))
        active_sessions = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT COUNT(*) FROM session WHERE candidate_id = ? AND status = "completed"', (candidate_id,))
        completed_sessions = cursor.fetchone()[0] or 0
        
        conn.close()
        
        # ✅ FIX: Include photo_path in candidate dictionary
        candidate = {
            'candidate_id': candidate_data['candidate_id'],
            'name': candidate_data['name'],
            'email': candidate_data['email'],
            'created_at': candidate_data['created_at'],
            'photo_path': candidate_data['photo_path']  
        }
        
        return render_template('dashboard.html', 
                             candidate=candidate, 
                             sessions=sessions,
                             active_session=active_session,
                             total_sessions=total_sessions,
                             active_sessions=active_sessions,
                             completed_sessions=completed_sessions)
        
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('login'))

@app.route('/start-exam', methods=['POST'])
def start_exam():
    if 'candidate_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    candidate_id = session['candidate_id']
    
    session_id, message = create_session(candidate_id)
    
    if session_id:
        # Log event
        EventLogger.log_event(
            session_id, 
            candidate_id, 
            'exam_started',
            f"Exam started by candidate ID: {candidate_id}"
        )
        flash(message, 'success')
        session['exam_session_id'] = session_id
    else:
        flash(message, 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/pause-exam', methods=['POST'])
def pause_exam():
    if 'candidate_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    if 'exam_session_id' not in session:
        flash('No active exam session.', 'error')
        return redirect(url_for('dashboard'))
    
    session_id = session['exam_session_id']
    candidate_id = session['candidate_id']
    success, message = pause_session(session_id)
    
    if success:
        EventLogger.log_event(
            session_id, 
            candidate_id, 
            'exam_paused',
            f"Exam paused by candidate ID: {candidate_id}"
        )
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/resume-exam', methods=['POST'])
def resume_exam():
    if 'candidate_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    if 'exam_session_id' not in session:
        flash('No session to resume.', 'error')
        return redirect(url_for('dashboard'))
    
    session_id = session['exam_session_id']
    candidate_id = session['candidate_id']
    success, message = resume_session(session_id)
    
    if success:
        EventLogger.log_event(
            session_id, 
            candidate_id, 
            'exam_resumed',
            f"Exam resumed by candidate ID: {candidate_id}"
        )
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/end-exam', methods=['POST'])
def end_exam():
    if 'candidate_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    if 'exam_session_id' not in session:
        flash('No active exam session.', 'error')
        return redirect(url_for('dashboard'))
    
    session_id = session['exam_session_id']
    candidate_id = session['candidate_id']
    success, message = end_session(session_id)
    
    if success:
        EventLogger.log_event(
            session_id, 
            candidate_id, 
            'exam_submitted',
            f"Exam submitted by candidate ID: {candidate_id}"
        )
        flash(message, 'success')
        session.pop('exam_session_id', None)
    else:
        flash(message, 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/exam')
def exam_page():
    if 'candidate_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    if 'exam_session_id' not in session:
        flash('Please start an exam session first.', 'warning')
        return redirect(url_for('dashboard'))
    
    return render_template('exam.html', 
                         session_id=session['exam_session_id'],
                         candidate_id=session['candidate_id'])

@app.route('/browser-monitor')
def browser_monitor():
    """Browser Activity Monitoring Page"""
    if 'candidate_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    if 'exam_session_id' not in session:
        flash('Please start an exam session first.', 'warning')
        return redirect(url_for('dashboard'))
    
    return render_template('browser_monitor.html', 
                         session_id=session['exam_session_id'],
                         candidate_id=session['candidate_id'])

@app.route('/log-event', methods=['POST'])
def log_event():
    try:
        data = request.json
        
        session_id = data.get('session_id')
        candidate_id = data.get('candidate_id')
        event_type = data.get('event_type')
        remarks = data.get('remarks', '')
        event_data = data.get('event_data', '')
        
        if not all([session_id, candidate_id, event_type]):
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        event_id = EventLogger.log_event(
            session_id, 
            candidate_id, 
            event_type, 
            remarks, 
            event_data
        )
        
        if event_id:
            return jsonify({'status': 'success', 'event_id': event_id})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to log event'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/view-events/<int:candidate_id>')
def view_events(candidate_id):
    if 'candidate_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    if session['candidate_id'] != candidate_id:
        flash('You can only view your own events.', 'error')
        return redirect(url_for('dashboard'))
    
    events = EventLogger.get_candidate_events(candidate_id)
    stats = EventLogger.get_event_statistics(candidate_id)
    
    return render_template('view_events.html', 
                         events=events, 
                         stats=stats,
                         candidate_id=candidate_id)



@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("🚀 Starting ExamGuard Application...")
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)