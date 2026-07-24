from db_helper import DatabaseHelper

def test_database_operations():
    print("🧪 Testing Database Operations")
    print("-" * 40)
    
    # Test 1: Add candidate
    print("\n📝 Test 1: Adding candidate...")
    try:
        candidate_id = DatabaseHelper.add_candidate(
            'Test User', 
            'test@example.com', 
            'testpassword123'
        )
        print(f"   ✅ Candidate added with ID: {candidate_id}")
    except Exception as e:
        print(f"   ⚠️  {e}")
    
    # Test 2: Get candidate
    print("\n🔍 Test 2: Getting candidate...")
    candidate = DatabaseHelper.get_candidate_by_email('test@example.com')
    if candidate:
        print(f"   ✅ Found: {candidate['name']} ({candidate['email']})")
    
    # Test 3: Create session
    print("\n📋 Test 3: Creating session...")
    candidate = DatabaseHelper.get_candidate_by_email('test@example.com')
    if candidate:
        session_id = DatabaseHelper.create_session(candidate['candidate_id'])
        print(f"   ✅ Session created with ID: {session_id}")
    
    # Test 4: Get active session
    print("\n📊 Test 4: Getting active session...")
    candidate = DatabaseHelper.get_candidate_by_email('test@example.com')
    if candidate:
        session = DatabaseHelper.get_active_session(candidate['candidate_id'])
        if session:
            print(f"   ✅ Active session: ID {session['session_id']}")
            print(f"      Start time: {session['start_time']}")
    
    # Test 5: End session
    print("\n⏹️  Test 5: Ending session...")
    candidate = DatabaseHelper.get_candidate_by_email('test@example.com')
    if candidate:
        session = DatabaseHelper.get_active_session(candidate['candidate_id'])
        if session:
            DatabaseHelper.end_session(session['session_id'])
            print(f"   ✅ Session {session['session_id']} ended")
    
    # Test 6: Get all candidates
    print("\n👥 Test 6: Getting all candidates...")
    candidates = DatabaseHelper.get_all_candidates()
    print(f"   ✅ Found {len(candidates)} candidates:")
    for c in candidates[:3]:  # Show first 3
        print(f"      - {c['name']} ({c['email']})")
    
    print("\n🎉 All tests completed!")

if __name__ == '__main__':
    test_database_operations()