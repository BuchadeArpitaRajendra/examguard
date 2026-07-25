import csv
import random
from faker import Faker
from datetime import datetime

# Initialize Faker
fake = Faker()

def generate_candidates(num_records=20):
    """Generate sample candidate data using Faker"""
    
    # List of exam subjects
    subjects = [
        'Mathematics', 'Physics', 'Chemistry', 'Biology', 
        'Computer Science', 'English Literature', 'History', 
        'Geography', 'Economics', 'Psychology', 
        'Statistics', 'Data Science', 'Artificial Intelligence',
        'Machine Learning', 'Robotics', 'Civil Engineering',
        'Mechanical Engineering', 'Electrical Engineering',
        'Business Administration', 'Finance'
    ]
    
    candidates = []
    
    for i in range(num_records):
        candidate = {
            'candidate_id': f'C{str(i+1).zfill(4)}',
            'name': fake.name(),
            'email': fake.email(),
            'age': random.randint(18, 40),
            'exam_subject': random.choice(subjects),
            'city': fake.city(),
            'country': fake.country(),
            'phone': fake.phone_number(),
            'registration_date': fake.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d')
        }
        candidates.append(candidate)
    
    return candidates

def save_to_csv(candidates, filename='sample_candidates.csv'):
    """Save candidates to CSV file"""
    if not candidates:
        print("❌ No data to save!")
        return False
    
    try:
        # Define CSV headers
        headers = ['candidate_id', 'name', 'email', 'age', 'exam_subject', 
                  'city', 'country', 'phone', 'registration_date']
        
        # Write to CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(candidates)
        
        print(f"✅ Successfully saved {len(candidates)} candidates to {filename}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving CSV: {e}")
        return False

def display_sample_candidates(candidates, count=5):
    """Display first few candidates as preview"""
    print("\n" + "="*80)
    print("📊 SAMPLE CANDIDATES PREVIEW")
    print("="*80)
    
    print(f"\n✅ Generated {len(candidates)} candidates\n")
    print(f"{'ID':<10} {'Name':<25} {'Email':<30} {'Age':<5} {'Subject'}")
    print("-"*80)
    
    for c in candidates[:count]:
        print(f"{c['candidate_id']:<10} {c['name']:<25} {c['email']:<30} {c['age']:<5} {c['exam_subject']}")
    
    if len(candidates) > count:
        print(f"\n... and {len(candidates) - count} more candidates")
    
    print("\n" + "="*80)
    print(f"📊 Statistics:")
    print(f"   Total: {len(candidates)}")
    print(f"   Age Range: {min(c['age'] for c in candidates)} - {max(c['age'] for c in candidates)} years")
    print(f"   Subjects: {len(set(c['exam_subject'] for c in candidates))} different subjects")
    print("="*80)

def generate_and_save_candidates(num_records=20, filename='sample_candidates.csv'):
    """Main function to generate and save candidates"""
    print(f"🚀 Generating {num_records} sample candidates...")
    
    # Generate data
    candidates = generate_candidates(num_records)
    
    # Display preview
    display_sample_candidates(candidates)
    
    # Save to CSV
    save_to_csv(candidates, filename)
    
    # Also save to database (optional)
    print("\n💡 To add these to your database, run:")
    print("   python import_candidates.py")
    
    return candidates

if __name__ == '__main__':
    # Generate 20 sample candidates
    generate_and_save_candidates(20, 'sample_candidates.csv')