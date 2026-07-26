import cv2
from face_detector import FaceDetector

def main():
    """Main function to test webcam and face detection"""
    
    # Initialize face detector
    detector = FaceDetector()
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Cannot open webcam")
        return
    
    print("✅ Webcam opened successfully")
    print("📋 Instructions:")
    print("   Press 'c' - Capture photo")
    print("   Press 'q' - Quit")
    print("   Press 'r' - Reset capture")
    print("-" * 40)
    
    captured_image = None
    
    while True:
        # Read frame from webcam
        ret, frame = cap.read()
        
        if not ret:
            print("❌ Failed to grab frame")
            break
        
        # Flip frame horizontally for mirror view
        frame = cv2.flip(frame, 1)
        
        # Detect faces
        frame_with_faces, faces = detector.detect_faces(frame)
        
        # Get status
        status_text = detector.get_status_text()
        status_color = detector.get_status_color()
        
        # Display status on frame
        cv2.putText(frame_with_faces, status_text, 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.7, status_color, 2)
        
        # Display face count
        cv2.putText(frame_with_faces, f"Faces: {detector.face_count}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, (255, 255, 255), 2)
        
        # Display instructions
        cv2.putText(frame_with_faces, "Press 'c' to capture, 'q' to quit", 
                   (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.5, (200, 200, 200), 1)
        
        # Show captured image preview if exists
        if captured_image:
            cv2.putText(frame_with_faces, "✅ Photo Captured!", 
                       (frame.shape[1] - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 255, 0), 2)
        
        # Show the frame
        cv2.imshow('Face Detection - ExamGuard', frame_with_faces)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            print("👋 Exiting...")
            break
            
        elif key == ord('c'):
            # Capture photo
            captured_image = detector.capture_frame(frame)
            if captured_image:
                print(f"✅ Photo saved: {captured_image}")
        
        elif key == ord('r'):
            # Reset capture
            captured_image = None
            detector.captured_photo = None
            print("🔄 Reset capture")
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Webcam released")

if __name__ == '__main__':
    main()