import cv2
import os
import time
from datetime import datetime
import threading

class FaceDetector:
    """Face detection with continuous monitoring and event logging"""
    
    def __init__(self, candidate_id=None, session_id=None, event_logger=None):
        # Load Haar Cascade
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if self.face_cascade.empty():
            print("❌ Failed to load Haar Cascade classifier")
            print("💡 Trying alternative path...")
            self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        
        if not self.face_cascade.empty():
            print("✅ Haar Cascade loaded successfully!")
        else:
            print("❌ Still failed to load Haar Cascade")
        
        # Detection state
        self.face_detected = False
        self.face_count = 0
        self.captured_photo = None
        
        # Absence tracking
        self.face_absent = False
        self.absence_start_time = None
        self.total_absence_duration = 0  # in seconds
        self.current_absence_duration = 0  # current session absence
        self.is_absence_logged = False
        
        # Session info
        self.candidate_id = candidate_id
        self.session_id = session_id
        self.event_logger = event_logger
        
        # Status callback
        self.status_callback = None
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
        # Last frame for capture
        self.last_frame = None
    
    def detect_faces(self, frame):
        """Detect faces and update status"""
        if self.face_cascade is None or self.face_cascade.empty():
            return frame, []
        
        # Store frame for capture
        self.last_frame = frame.copy()
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        with self.lock:
            previous_state = self.face_detected
            self.face_count = len(faces)
            self.face_detected = len(faces) > 0
            
            # Track absence
            self.update_absence_tracking(previous_state)
        
        # Draw rectangles around faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            # Add label
            cv2.putText(frame, "Face", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame, faces
    
    def update_absence_tracking(self, previous_state):
        """Update face absence tracking"""
        current_time = time.time()
        
        if self.face_detected:
            # Face is detected
            if previous_state == False:
                # Face was absent, now detected
                if self.absence_start_time:
                    duration = current_time - self.absence_start_time
                    self.total_absence_duration += duration
                    self.current_absence_duration = duration
                    
                    # Log face detected event
                    if self.event_logger and self.session_id:
                        self.event_logger.log_event(
                            self.session_id,
                            self.candidate_id,
                            'face_detected',
                            f"Face detected after absence of {duration:.2f} seconds"
                        )
                    
                    # Reset absence tracking
                    self.absence_start_time = None
                    self.is_absence_logged = False
            
            self.current_absence_duration = 0
            
        else:
            # Face is not detected
            if previous_state == True:
                # Face was detected, now absent
                self.absence_start_time = current_time
                
                # Log face not detected event
                if self.event_logger and self.session_id:
                    self.event_logger.log_event(
                        self.session_id,
                        self.candidate_id,
                        'face_not_detected',
                        f"Face not detected at {datetime.now().strftime('%H:%M:%S')}"
                    )
                    self.is_absence_logged = True
            
            # Calculate current absence duration
            if self.absence_start_time:
                self.current_absence_duration = current_time - self.absence_start_time
    
    def get_absence_duration(self):
        """Get current absence duration in seconds"""
        with self.lock:
            if self.face_detected:
                return 0
            elif self.absence_start_time:
                return time.time() - self.absence_start_time
            return 0
    
    def get_total_absence(self):
        """Get total absence duration in seconds"""
        with self.lock:
            total = self.total_absence_duration
            if not self.face_detected and self.absence_start_time:
                total += time.time() - self.absence_start_time
            return total
    
    def get_status_text(self):
        """Get face detection status text"""
        if self.face_detected:
            return "✅ Face Detected"
        else:
            return "❌ Face Not Detected"
    
    def get_status_color(self):
        """Get status color for display"""
        if self.face_detected:
            return (0, 255, 0)  # Green
        else:
            return (0, 0, 255)  # Red
    
    def capture_frame(self, frame=None):
        """Capture and save the current frame"""
        try:
            if frame is None:
                frame = self.last_frame
            
            if frame is None:
                print("❌ No frame available to capture")
                return None
            
            # Create photos directory
            photos_dir = 'static/photos'
            os.makedirs(photos_dir, exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"captured_{timestamp}.jpg"
            filepath = os.path.join(photos_dir, filename)
            
            # Save image
            cv2.imwrite(filepath, frame)
            
            self.captured_photo = filepath
            print(f"✅ Photo captured and saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error capturing photo: {e}")
            return None
    
    def set_event_logger(self, event_logger, candidate_id, session_id):
        """Set event logger for tracking"""
        self.event_logger = event_logger
        self.candidate_id = candidate_id
        self.session_id = session_id
    
    def reset_absence_timer(self):
        """Reset absence timer manually"""
        with self.lock:
            self.total_absence_duration = 0
            self.current_absence_duration = 0
            self.absence_start_time = None
            self.is_absence_logged = False
            print("🔄 Absence timer reset")