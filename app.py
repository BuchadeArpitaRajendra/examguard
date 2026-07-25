from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import re
import base64
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'

# Database path
DB_PATH = 'instance/examguard.db'

def get_db_connection():
    """Create and return a database connection"""
    os.makedirs('instance', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

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

def save_photo(photo_data, candidate_id):
    """Save base64 photo data to file and return path"""
    try:
        # Create photos directory if it doesn't exist
        photos_dir = os.path.join('static', 'photos')
        os.makedirs(photos_dir, exist_ok=True)
        
        # Remove the data URL prefix if present
        if 'base64' in photo_data:
            # Extract the base64 data
            if ',' in photo_data:
                photo_data = photo_data.split(',')[1]
        
        # Decode base64 data
        image_data = base64.b64decode(photo_data)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"candidate_{candidate_id}_{timestamp}.jpg"
        filepath = os.path.join(photos_dir, filename)
        
        # Save image
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        # Return relative path for database
        return f"static/photos/{filename}"
        
    except Exception as e:
        print(f"Error saving photo: {e}")
        return None

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
        
        # Check if session exists and is active
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
        
        # Update status to paused
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
        
        # Check if session exists and is paused
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
        
        # Update status to active
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
        
        # Check if session exists
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
        
        # Update status to completed and set end time
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

def get_active_session(candidate_id):
    """Get the current active session for a candidate"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM session 
            WHERE candidate_id = ? AND status IN ('active', 'paused')
            ORDER BY start_time DESC LIMIT 1
        ''', (candidate_id,))
        
        session = cursor.fetchone()
        conn.close()
        return session
        
    except Exception as e:
        return None

def get_session_history(candidate_id):
    """Get all sessions for a candidate"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM session 
            WHERE candidate_id = ? 
            ORDER BY start_time DESC
        ''', (candidate_id,))
        
        sessions = cursor.fetchall()
        conn.close()
        return sessions
        
    except Exception as e:
        return []

@app.route('/')
def home():
    """Home page - redirect to login"""
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Candidate Registration Page with Photo Capture"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        terms = request.form.get('terms', '')
        photo_data = request.form.get('photo_data', '')
        
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
        
        # Check if photo was captured
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
            
            # First insert without photo path
            cursor.execute('''
                INSERT INTO candidate (name, email, password, photo_path)
                VALUES (?, ?, ?, ?)
            ''', (name, email, hashed_password, None))
            
            conn.commit()
            candidate_id = cursor.lastrowid
            
            # Save photo and get path
            photo_path = save_photo(photo_data, candidate_id)
            
            # Update candidate with photo path
            if photo_path:
                cursor.execute('''
                    UPDATE candidate 
                    SET photo_path = ? 
                    WHERE candidate_id = ?
                ''', (photo_path, candidate_id))
                conn.commit()
            
            conn.close()
            
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
            else:
                flash('❌ No account found with this email. Please register.', 'error')
                
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
        
        candidate = {
            'candidate_id': candidate_data['candidate_id'],
            'name': candidate_data['name'],
            'email': candidate_data['email'],
            'created_at': candidate_data['created_at']
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

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/start-exam', methods=['POST'])
def start_exam():
    """Start a new exam session"""
    if 'candidate_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    candidate_id = session['candidate_id']
    
    session_id, message = create_session(candidate_id)
    
    if session_id:
        flash(message, 'success')
        session['exam_session_id'] = session_id
    else:
        flash(message, 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/pause-exam', methods=['POST'])
def pause_exam():
    """Pause the current exam session"""
    if 'candidate_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    if 'exam_session_id' not in session:
        flash('No active exam session.', 'error')
        return redirect(url_for('dashboard'))
    
    session_id = session['exam_session_id']
    success, message = pause_session(session_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/resume-exam', methods=['POST'])
def resume_exam():
    """Resume a paused exam session"""
    if 'candidate_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    if 'exam_session_id' not in session:
        flash('No session to resume.', 'error')
        return redirect(url_for('dashboard'))
    
    session_id = session['exam_session_id']
    success, message = resume_session(session_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/end-exam', methods=['POST'])
def end_exam():
    """End the current exam session"""
    if 'candidate_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    if 'exam_session_id' not in session:
        flash('No active exam session.', 'error')
        return redirect(url_for('dashboard'))
    
    session_id = session['exam_session_id']
    success, message = end_session(session_id)
    
    if success:
        flash(message, 'success')
        session.pop('exam_session_id', None)
    else:
        flash(message, 'error')
    
    return redirect(url_for('dashboard'))



if __name__ == '__main__':
    print("🚀 Starting ExamGuard Application...")
    app.run(debug=True, host='0.0.0.0', port=5000)