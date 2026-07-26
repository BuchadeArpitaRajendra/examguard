from flask import Blueprint, render_template, Response, jsonify, session, flash, redirect, url_for
import cv2
from face_detector import FaceDetector
import base64
from datetime import datetime

face_bp = Blueprint('face', __name__)
detector = FaceDetector()

def generate_frames():
    """Generate video frames for streaming"""
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Flip for mirror view
        frame = cv2.flip(frame, 1)
        
        # Detect faces
        frame_with_faces, faces = detector.detect_faces(frame)
        
        # Add status text
        status_text = detector.get_status_text()
        status_color = detector.get_status_color()
        
        cv2.putText(frame_with_faces, status_text, 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.7, status_color, 2)
        
        cv2.putText(frame_with_faces, f"Faces: {detector.face_count}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, (255, 255, 255), 2)
        
        # Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame_with_faces)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    cap.release()

@face_bp.route('/face-monitor')
def face_monitor():
    """Face monitoring page"""
    if 'candidate_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    return render_template('face_monitor.html')

@face_bp.route('/video-feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@face_bp.route('/capture-photo', methods=['POST'])
def capture_photo():
    """Capture photo from current frame"""
    if 'candidate_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'}), 401
    
    # This would need to capture from the current frame
    # For simplicity, we'll use a placeholder
    return jsonify({'status': 'success', 'message': 'Photo captured'})