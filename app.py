"""
ExamGuard - Online Exam Monitoring Platform
Copyright (c) 2026 BuchadeArpitaRajendra
Licensed under MIT License - see LICENSE file for details
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'

# Database path
DB_PATH = 'instance/examguard.db'

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    """Home page"""
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Candidate Registration Page"""
    if request.method == 'POST':
        # Get form data
        candidate_id = request.form.get('candidate_id', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        terms = request.form.get('terms', '')
        
        # Validation
        errors = []
        
        # Check required fields
        if not candidate_id:
            errors.append("Candidate ID is required.")
        if not name:
            errors.append("Name is required.")
        if not email:
            errors.append("Email is required.")
        if not password:
            errors.append("Password is required.")
        
        # Check password match
        if password and confirm_password and password != confirm_password:
            errors.append("Passwords do not match.")
        
        # Check password length
        if password and len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        
        # Check terms
        if not terms:
            errors.append("You must agree to the Terms & Conditions.")
        
        # If errors, flash them and return
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        try:
            # Hash the password
            hashed_password = generate_password_hash(password)
            
            # Insert into database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO candidate (name, email, password, photo_path)
                VALUES (?, ?, ?, ?)
            ''', (name, email, hashed_password, None))
            
            conn.commit()
            conn.close()
            
            flash('✅ Registration successful! Please login to continue.', 'success')
            return redirect(url_for('register'))
            
        except sqlite3.IntegrityError:
            flash('❌ Email already registered. Please use a different email.', 'error')
            return render_template('register.html')
        except Exception as e:
            flash(f'❌ An error occurred: {str(e)}', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

if __name__ == '__main__':
    # Ensure instance folder exists
    os.makedirs('instance', exist_ok=True)
    app.run(debug=True)