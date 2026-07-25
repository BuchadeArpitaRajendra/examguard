import sqlite3
import os
from init_db import get_db_connection

def get_all_candidates():
    """Get all candidates with photo info"""
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
        ORDER BY created_at DESC
    ''')
    
    candidates = cursor.fetchall()
    conn.close()
    return candidates

def check_registered_candidates():
    """Display all registered candidates"""
    candidates = get_all_candidates()
    
    print("\n" + "="*80)
    print("📊 REGISTERED CANDIDATES")
    print("="*80)
    
    if not candidates:
        print("❌ No candidates registered yet.\n")
        return
    
    print(f"✅ Found {len(candidates)} registered candidates:\n")
    print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'Photo':<25} {'Registered'}")
    print("-"*90)
    
    for c in candidates:
        created = c['created_at'][:19] if c['created_at'] else 'N/A'
        
        # Check photo
        if c['photo_path']:
            # Check if file actually exists
            if os.path.exists(c['photo_path']):
                photo = f"✅ {os.path.basename(c['photo_path'])}"
            else:
                photo = "⚠️ File missing"
        else:
            photo = "❌ No photo"
        
        print(f"{c['candidate_id']:<5} {c['name']:<20} {c['email']:<30} {photo:<25} {created}")

def check_photo_files():
    """Check photos in folder vs database"""
    print("\n" + "="*80)
    print("📸 PHOTO VERIFICATION")
    print("="*80)
    
    # Get photos from database
    candidates = get_all_candidates()
    
    # Get photos from folder
    photos_dir = 'static/photos'
    folder_photos = []
    if os.path.exists(photos_dir):
        folder_photos = [f for f in os.listdir(photos_dir) 
                        if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    
    print(f"📁 Photos in folder: {len(folder_photos)}")
    print(f"📊 Photos in database: {sum(1 for c in candidates if c['photo_path'])}")
    
    # Check each candidate
    print("\n📋 Candidate Photo Status:")
    print("-"*60)
    for c in candidates:
        status = "✅ Has photo" if c['photo_path'] else "❌ No photo"
        if c['photo_path'] and os.path.exists(c['photo_path']):
            status = "✅ File exists"
        elif c['photo_path'] and not os.path.exists(c['photo_path']):
            status = "⚠️ File missing"
        print(f"  {c['name']:<20} {status}")

def debug_photo_paths():
    """Debug: Show raw photo_path values"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("🔍 RAW PHOTO_PATH VALUES")
    print("="*80)
    
    cursor.execute('SELECT candidate_id, name, photo_path FROM candidate')
    candidates = cursor.fetchall()
    conn.close()
    
    for c in candidates:
        print(f"  ID: {c['candidate_id']}")
        print(f"  Name: {c['name']}")
        print(f"  Photo Path: '{c['photo_path']}'")
        print(f"  Exists: {os.path.exists(c['photo_path']) if c['photo_path'] else False}")
        print("-"*40)

if __name__ == '__main__':
    check_registered_candidates()
    check_photo_files()
    debug_photo_paths()
    
    print("\n" + "="*80)
    print("💡 TROUBLESHOOTING")
    print("="*80)
    print("If photo is not showing:")
    print("1. Make sure you captured a photo during registration")
    print("2. Check if photo was saved: ls static/photos/")
    print("3. Check database: sqlite3 instance/examguard.db")
    print("   SELECT candidate_id, name, photo_path FROM candidate;")
    print("4. Run: python init_db.py to reset database")