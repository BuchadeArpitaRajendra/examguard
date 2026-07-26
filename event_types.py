class EventTypes:
    """Constants for all event types"""
    
    # Session Events
    EXAM_STARTED = 'exam_started'
    EXAM_PAUSED = 'exam_paused'
    EXAM_RESUMED = 'exam_resumed'
    EXAM_SUBMITTED = 'exam_submitted'
    EXAM_ENDED = 'exam_ended'
    
    # Browser Events
    TAB_SWITCHED = 'tab_switched'
    FOCUS_LOST = 'focus_lost'
    FOCUS_GAINED = 'focus_gained'
    COPY_ATTEMPT = 'copy_attempted'
    PASTE_ATTEMPT = 'paste_attempted'
    RIGHT_CLICK = 'right_click_detected'
    
    # Face Events
    FACE_DETECTED = 'face_detected'
    FACE_NOT_DETECTED = 'face_not_detected'
    FACE_ABSENT_START = 'face_absent_start'
    FACE_ABSENT_END = 'face_absent_end'
    
    # Suspicious Events
    SUSPICIOUS_ACTIVITY = 'suspicious_activity'
    MULTIPLE_TAB_SWITCHES = 'multiple_tab_switches'
    EXTENDED_FACE_ABSENCE = 'extended_face_absence'
    
    # Security Events
    INVALID_ACCESS = 'invalid_access'
    SESSION_TIMEOUT = 'session_timeout'

# Event categories for grouping
EVENT_CATEGORIES = {
    'session': [EventTypes.EXAM_STARTED, EventTypes.EXAM_PAUSED, 
                EventTypes.EXAM_RESUMED, EventTypes.EXAM_SUBMITTED, 
                EventTypes.EXAM_ENDED],
    'browser': [EventTypes.TAB_SWITCHED, EventTypes.FOCUS_LOST, 
                EventTypes.FOCUS_GAINED, EventTypes.COPY_ATTEMPT, 
                EventTypes.PASTE_ATTEMPT, EventTypes.RIGHT_CLICK],
    'face': [EventTypes.FACE_DETECTED, EventTypes.FACE_NOT_DETECTED, 
             EventTypes.FACE_ABSENT_START, EventTypes.FACE_ABSENT_END],
    'suspicious': [EventTypes.SUSPICIOUS_ACTIVITY, EventTypes.MULTIPLE_TAB_SWITCHES, 
                   EventTypes.EXTENDED_FACE_ABSENCE],
    'security': [EventTypes.INVALID_ACCESS, EventTypes.SESSION_TIMEOUT]
}