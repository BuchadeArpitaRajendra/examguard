"""
ExamGuard - Online Exam Monitoring Platform
Copyright (c) 2026 BuchadeArpitaRajendra
Licensed under MIT License - see LICENSE file for details
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'

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
    
    conn.commit()
    conn.close()

def validate_email(email):
    """Validate email format"""
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

@app.route('/')
def home():
    """Home page - redirect to registration"""
    return redirect(url_for('register'))

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
        
        # ===== VALIDATION =====
        errors = []
        
        # Validate Name
        if not name:
            errors.append("Full name is required.")
        elif len(name) < 2:
            errors.append("Name must be at least 2 characters long.")
        
        # Validate Email
        if not email:
            errors.append("Email address is required.")
        elif not validate_email(email):
            errors.append("Please enter a valid email address.")
        
        # Validate Password
        if not password:
            errors.append("Password is required.")
        else:
            is_valid, message = validate_password(password)
            if not is_valid:
                errors.append(message)
        
        # Validate Password Match
        if password and confirm_password and password != confirm_password:
            errors.append("Passwords do not match.")
        
        # Validate Terms
        if not terms:
            errors.append("You must agree to the Terms & Conditions.")
        
        # If there are errors, flash them and return to form
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        # ===== STORE IN DATABASE =====
        try:
            # Hash the password
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            
            # Insert into database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO candidate (name, email, password, photo_path)
                VALUES (?, ?, ?, ?)
            ''', (name, email, hashed_password, None))
            
            conn.commit()
            
            # Get the inserted candidate ID
            candidate_id = cursor.lastrowid
            
            # Fetch the inserted record to confirm
            cursor.execute('SELECT * FROM candidate WHERE candidate_id = ?', (candidate_id,))
            new_candidate = cursor.fetchone()
            
            conn.close()
            
            # Success message
            flash(f'✅ Registration successful! Welcome, {name}! Please login to continue.', 'success')
            
            # Store in session for auto-login (optional)
            session['registered_email'] = email
            
            return redirect(url_for('register'))
            
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                flash('❌ This email is already registered. Please use a different email or login.', 'error')
            else:
                flash(f'❌ Database error: {str(e)}', 'error')
            return render_template('register.html')
            
        except Exception as e:
            flash(f'❌ An error occurred during registration: {str(e)}', 'error')
            return render_template('register.html')
    
    # GET request - show registration form
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Page"""
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
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Candidate Dashboard"""
    if 'candidate_id' not in session:
        flash('Please login to access your dashboard.', 'warning')
        return redirect(url_for('login'))
    
    candidate_id = session['candidate_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get candidate details
        cursor.execute('SELECT * FROM candidate WHERE candidate_id = ?', (candidate_id,))
        candidate = cursor.fetchone()
        
        # Get session history
        cursor.execute('''
            SELECT * FROM session 
            WHERE candidate_id = ? 
            ORDER BY start_time DESC
        ''', (candidate_id,))
        sessions = cursor.fetchall()
        
        conn.close()
        
        return render_template('dashboard.html', candidate=candidate, sessions=sessions)
        
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/view-candidates')
def view_candidates():
    """Admin view - Show all candidates"""
    try:
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
        
        return render_template('candidates.html', candidates=candidates)
        
    except Exception as e:
        flash(f'Error loading candidates: {str(e)}', 'error')
        return redirect(url_for('login'))

# ===== ERROR HANDLERS =====
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Initialize database
    print("🚀 Starting ExamGuard Application...")
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)