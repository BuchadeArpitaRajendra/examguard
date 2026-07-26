import cv2
import time
from datetime import datetime
from face_detector import FaceDetector
from event_logger import EventLogger
from database import get_db_connection

class FaceMonitor:
    """Continuous face presence monitoring system"""
    
    def __init__(self, candidate_id=None, session_id=None):
        self.candidate_id = candidate_id
        self.session_id = session_id
        self.detector = FaceDetector(candidate_id, session_id, EventLogger)
        self.running = False
        self.cap = None
        self.start_time = None
        
        # Display settings
        self.window_name = 'Face Monitoring - ExamGuard'
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Colors
        self.colors = {
            'green': (0, 255, 0),
            'red': (0, 0, 255),
            'white': (255, 255, 255),
            'yellow': (0, 255, 255),
            'blue': (255, 0, 0)
        }
    
    def start_monitoring(self):
        """Start face monitoring"""
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            print("❌ Cannot open webcam")
            return
        
        self.running = True
        self.start_time = time.time()
        
        print("✅ Face Monitoring Started")
        print("📋 Instructions:")
        print("   Press 'c' - Capture photo")
        print("   Press 'r' - Reset absence timer")
        print("   Press 'q' - Quit monitoring")
        print("-" * 50)
        
        while self.running:
            ret, frame = self.cap.read()
            
            if not ret:
                print("❌ Failed to grab frame")
                break
            
            # Flip for mirror view
            frame = cv2.flip(frame, 1)
            
            # Detect faces
            frame_with_faces, faces = self.detector.detect_faces(frame)
            
            # Display information on frame
            self.display_info(frame_with_faces)
            
            # Show the frame
            cv2.imshow(self.window_name, frame_with_faces)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("👋 Stopping monitoring...")
                break
            
            elif key == ord('c'):
                self.detector.capture_frame(frame)
            
            elif key == ord('r'):
                self.detector.reset_absence_timer()
                print("🔄 Absence timer reset")
        
        self.stop_monitoring()
    
    def display_info(self, frame):
        """Display monitoring information on frame"""
        # Get current time
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # Get status
        status_text = self.detector.get_status_text()
        status_color = self.detector.get_status_color()
        
        # Get absence duration
        absence_duration = self.detector.get_absence_duration()
        total_absence = self.detector.get_total_absence()
        
        # Format absence duration
        absence_str = f"{absence_duration:.1f}s" if absence_duration > 0 else "0.0s"
        total_absence_str = f"{total_absence:.1f}s" if total_absence > 0 else "0.0s"
        
        # Display panel
        panel_y = 20
        line_height = 30
        
        # Background panel
        cv2.rectangle(frame, (5, 5), (320, 150), (0, 0, 0), -1)
        cv2.rectangle(frame, (5, 5), (320, 150), (255, 255, 255), 1)
        
        # Face Status
        cv2.putText(frame, f"Face Status:", (15, panel_y + line_height), 
                   self.font, 0.6, self.colors['white'], 1)
        cv2.putText(frame, status_text, (15, panel_y + line_height * 2), 
                   self.font, 0.7, status_color, 2)
        
        # Face Count
        cv2.putText(frame, f"Faces: {self.detector.face_count}", (15, panel_y + line_height * 3), 
                   self.font, 0.6, self.colors['white'], 1)
        
        # Current Time
        cv2.putText(frame, f"Time: {current_time}", (15, panel_y + line_height * 4), 
                   self.font, 0.6, self.colors['white'], 1)
        
        # Absence Duration
        absence_color = self.colors['red'] if absence_duration > 0 else self.colors['green']
        cv2.putText(frame, f"Absence: {absence_str}", (15, panel_y + line_height * 5), 
                   self.font, 0.6, absence_color, 1)
        
        # Total Absence
        cv2.putText(frame, f"Total Absence: {total_absence_str}", (15, panel_y + line_height * 6), 
                   self.font, 0.6, self.colors['yellow'], 1)
        
        # Instructions at bottom
        cv2.putText(frame, "c: Capture | r: Reset | q: Quit", 
                   (10, frame.shape[0] - 20), self.font, 
                   0.5, (200, 200, 200), 1)
        
        # Alert if face absent for too long
        if absence_duration > 5:
            warning_color = self.colors['red'] if absence_duration > 10 else self.colors['yellow']
            cv2.putText(frame, f"⚠️ WARNING: Face absent for {absence_str}!", 
                       (frame.shape[1] - 350, 30), self.font, 
                       0.7, warning_color, 2)
    
    def stop_monitoring(self):
        """Stop face monitoring"""
        self.running = False
        
        if self.cap:
            self.cap.release()
        
        cv2.destroyAllWindows()
        
        # Log session end
        total_absence = self.detector.get_total_absence()
        print(f"\n📊 Monitoring Summary:")
        print(f"   Total face absence: {total_absence:.1f} seconds")
        print(f"   Total events logged: {len(self.detector.event_logger.get_session_events(self.session_id)) if self.session_id else 'N/A'}")
        print("✅ Monitoring stopped")

def main():
    """Main function to run face monitoring"""
    print("="*60)
    print("📸 ExamGuard - Face Presence Monitoring")
    print("="*60)
    
    # You can pass candidate_id and session_id here
    # For testing, use dummy values
    candidate_id = 1
    session_id = 1
    
    # Start monitoring
    monitor = FaceMonitor(candidate_id, session_id)
    monitor.start_monitoring()

if __name__ == '__main__':
    main()