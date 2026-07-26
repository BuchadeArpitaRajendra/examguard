import time
from datetime import datetime
from event_logger import EventLogger

class BrowserMonitor:
    """Browser activity monitoring system"""
    
    def __init__(self, candidate_id=None, session_id=None, event_logger=None):
        self.candidate_id = candidate_id
        self.session_id = session_id
        self.event_logger = event_logger or EventLogger()
        
        # Browser state
        self.is_active = True
        self.is_focused = True
        self.focus_lost_count = 0
        self.focus_gained_count = 0
        self.tab_switch_count = 0
        
        # Timing
        self.last_focus_lost_time = None
        self.last_focus_gained_time = None
        self.last_tab_switch_time = None
        
        # Total absence duration
        self.total_inactive_duration = 0
        self.inactive_start_time = None
        
        # Callbacks
        self.status_callback = None
        
        print("✅ BrowserMonitor initialized")
    
    def on_focus_lost(self):
        """Handle browser focus lost event"""
        current_time = datetime.now()
        timestamp = current_time.strftime('%H:%M:%S')
        
        if self.is_focused:
            self.is_focused = False
            self.focus_lost_count += 1
            self.last_focus_lost_time = current_time
            self.inactive_start_time = current_time
            
            # Log event
            if self.session_id and self.candidate_id:
                self.event_logger.log_browser_focus_lost(
                    self.session_id,
                    self.candidate_id,
                    f"Focus lost at {timestamp}"
                )
            
            print(f"🟡 Browser Focus Lost - {timestamp}")
            
            # Update display
            self.update_display('browser_focus_lost', timestamp)
    
    def on_focus_gained(self):
        """Handle browser focus regained event"""
        current_time = datetime.now()
        timestamp = current_time.strftime('%H:%M:%S')
        
        if not self.is_focused:
            self.is_focused = True
            self.focus_gained_count += 1
            self.last_focus_gained_time = current_time
            
            # Calculate inactive duration
            if self.inactive_start_time:
                duration = (current_time - self.inactive_start_time).total_seconds()
                self.total_inactive_duration += duration
                self.inactive_start_time = None
            
            # Log event
            if self.session_id and self.candidate_id:
                self.event_logger.log_browser_focus_gained(
                    self.session_id,
                    self.candidate_id,
                    f"Focus regained at {timestamp}"
                )
            
            print(f"🟢 Browser Focus Regained - {timestamp}")
            
            # Update display
            self.update_display('browser_focus_gained', timestamp)
    
    def on_tab_switch(self):
        """Handle tab switch event"""
        current_time = datetime.now()
        timestamp = current_time.strftime('%H:%M:%S')
        
        self.tab_switch_count += 1
        self.last_tab_switch_time = current_time
        
        # Log event
        if self.session_id and self.candidate_id:
            self.event_logger.log_tab_switched(
                self.session_id,
                self.candidate_id,
                f"Tab switched at {timestamp}"
            )
        
        print(f"🔄 Tab Switched - {timestamp}")
        
        # Update display
        self.update_display('tab_switched', timestamp)
    
    def get_status(self):
        """Get current browser status"""
        status = {
            'is_focused': self.is_focused,
            'is_active': self.is_active,
            'focus_lost_count': self.focus_lost_count,
            'focus_gained_count': self.focus_gained_count,
            'tab_switch_count': self.tab_switch_count,
            'last_focus_lost': self.last_focus_lost_time.strftime('%H:%M:%S') if self.last_focus_lost_time else None,
            'last_focus_gained': self.last_focus_gained_time.strftime('%H:%M:%S') if self.last_focus_gained_time else None,
            'last_tab_switch': self.last_tab_switch_time.strftime('%H:%M:%S') if self.last_tab_switch_time else None,
            'total_inactive_duration': self.total_inactive_duration
        }
        return status
    
    def get_status_text(self):
        """Get browser status text"""
        if self.is_focused:
            return "🟢 Browser Active"
        else:
            return "🔴 Browser Inactive"
    
    def get_status_color(self):
        """Get status color for display"""
        if self.is_focused:
            return (0, 255, 0)  # Green
        else:
            return (0, 0, 255)  # Red
    
    def get_inactive_duration(self):
        """Get current inactive duration in seconds"""
        if not self.is_focused and self.inactive_start_time:
            return (datetime.now() - self.inactive_start_time).total_seconds()
        return 0
    
    def set_event_logger(self, event_logger, candidate_id, session_id):
        """Set event logger for tracking"""
        self.event_logger = event_logger
        self.candidate_id = candidate_id
        self.session_id = session_id
    
    def update_display(self, event_type, timestamp):
        """Update display with browser status"""
        # This method will be called from the JavaScript side
        # We'll implement it in the HTML template
        pass
    
    def reset_counters(self):
        """Reset all counters"""
        self.focus_lost_count = 0
        self.focus_gained_count = 0
        self.tab_switch_count = 0
        self.total_inactive_duration = 0
        self.inactive_start_time = None
        print("🔄 Browser counters reset")