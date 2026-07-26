import os
import sqlite3
from database import get_db_connection

def check_photos():
    print("="*60)
    print("📸 PHOTO DEBUG CHECK")
    print("="*60)
    
    # Check database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT candidate_id, name, photo_path FROM candidate
    ''')
    candidates = cursor.fetchall()
    conn.close()
    
    print("\n📊 Database Check:")
    for c in candidates:
        print(f"  ID: {c['candidate_id']}")
        print(f"  Name: {c['name']}")
        print(f"  Photo Path: '{c['photo_path']}'")
        
        if c['photo_path']:
            if os.path.exists(c['photo_path']):
                print(f"  ✅ File exists: {c['photo_path']}")
            else:
                print(f"  ❌ File MISSING: {c['photo_path']}")
        else:
            print("  ❌ No photo path in database")
        print("-"*40)
    
    # Check folder
    print("\n📁 Photos Folder Check:")
    photos_dir = 'static/photos'
    if os.path.exists(photos_dir):
        files = os.listdir(photos_dir)
        print(f"  Found {len(files)} files in {photos_dir}:")
        for f in files:
            print(f"    - {f}")
    else:
        print(f"  ❌ Folder '{photos_dir}' does not exist!")
        print("  💡 Creating folder now...")
        os.makedirs(photos_dir, exist_ok=True)
        print("  ✅ Folder created!")

if __name__ == '__main__':
    check_photos()