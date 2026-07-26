/**
 * Exam Event Logger - Browser Monitoring
 */

var ExamEventLogger = function(sessionId, candidateId) {
    this.sessionId = sessionId;
    this.candidateId = candidateId;
    this.isExamActive = false;
    this.tabSwitchCount = 0;
    this.focusLossCount = 0;
    this.focusGainedCount = 0;
    this.startTime = null;
    this.eventLog = [];
    this.isFocused = true;
    this.inactiveStartTime = null;
    this.totalInactiveDuration = 0;
    
    this.init();
};

ExamEventLogger.prototype.init = function() {
    var self = this;

    // ===== TRACK PAGE VISIBILITY (Tab Switches) =====
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            // Tab switched - browser not visible
            self.onTabSwitch();
        } else {
            // Tab regained - browser visible
            self.onFocusGained();
        }
    });

    // ===== TRACK WINDOW FOCUS =====
    window.addEventListener('blur', function() {
        // Window lost focus
        self.onFocusLost();
    });

    window.addEventListener('focus', function() {
        // Window gained focus
        self.onFocusGained();
    });

    // ===== TRACK COPY ATTEMPTS =====
    document.addEventListener('copy', function(e) {
        self.logEvent('copy_attempted', 'Copy attempt detected');
    });

    // ===== TRACK PASTE ATTEMPTS =====
    document.addEventListener('paste', function(e) {
        self.logEvent('paste_attempted', 'Paste attempt detected');
    });

    // ===== TRACK RIGHT-CLICK =====
    document.addEventListener('contextmenu', function(e) {
        self.logEvent('right_click_detected', 'Right-click detected');
        e.preventDefault();
    });

    // ===== TRACK KEY COMBINATIONS =====
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey) {
            switch(e.key) {
                case 'c':
                    self.logEvent('copy_attempted', 'Ctrl+C copy attempt');
                    break;
                case 'v':
                    self.logEvent('paste_attempted', 'Ctrl+V paste attempt');
                    break;
                case 'u':
                    self.logEvent('view_source_attempt', 'Ctrl+U view source attempt');
                    e.preventDefault();
                    break;
                case 's':
                    self.logEvent('save_attempt', 'Ctrl+S save attempt');
                    e.preventDefault();
                    break;
            }
        }
        if (e.key === 'F12') {
            self.logEvent('dev_tools_attempt', 'F12 developer tools attempt');
            e.preventDefault();
        }
    });

    // ===== TRACK BEFORE UNLOAD =====
    window.addEventListener('beforeunload', function(e) {
        self.logEvent('session_timeout', 'Page refresh or close detected');
    });

    // ===== UPDATE DISPLAY EVERY SECOND =====
    setInterval(function() {
        self.updateBrowserDisplay();
    }, 1000);

    console.log('✅ Exam Event Logger initialized');
    console.log('📋 Session ID: ' + this.sessionId);
    console.log('👤 Candidate ID: ' + this.candidateId);
    console.log('🌐 Browser monitoring active');
};

ExamEventLogger.prototype.onFocusLost = function() {
    if (this.isFocused) {
        this.isFocused = false;
        this.focusLossCount++;
        this.inactiveStartTime = new Date();
        this.logEvent('browser_focus_lost', 'Browser focus lost');
        this.updateBrowserDisplay();
        console.log('🟡 Browser Focus Lost');
    }
};

ExamEventLogger.prototype.onFocusGained = function() {
    if (!this.isFocused) {
        this.isFocused = true;
        this.focusGainedCount++;
        if (this.inactiveStartTime) {
            var duration = (new Date() - this.inactiveStartTime) / 1000;
            this.totalInactiveDuration += duration;
            this.inactiveStartTime = null;
        }
        this.logEvent('browser_focus_gained', 'Browser focus regained');
        this.updateBrowserDisplay();
        console.log('🟢 Browser Focus Regained');
    }
};

ExamEventLogger.prototype.onTabSwitch = function() {
    this.tabSwitchCount++;
    this.logEvent('tab_switched', 'Browser tab switched');
    
    // Check for suspicious activity
    if (this.tabSwitchCount > 3) {
        this.logEvent('multiple_tab_switches', 
            'Multiple tab switches detected: ' + this.tabSwitchCount);
    }
    
    this.updateBrowserDisplay();
    console.log('🔄 Tab Switched');
};

ExamEventLogger.prototype.updateBrowserDisplay = function() {
    // Update browser status display
    var statusElement = document.getElementById('browserStatus');
    var statusIcon = document.getElementById('browserStatusIcon');
    var focusLostElement = document.getElementById('focusLostCount');
    var focusGainedElement = document.getElementById('focusGainedCount');
    var tabSwitchElement = document.getElementById('tabSwitchCount');
    var lastFocusLostElement = document.getElementById('lastFocusLost');
    
    if (statusElement) {
        if (this.isFocused) {
            statusElement.textContent = '🟢 Active';
            statusElement.style.color = '#27ae60';
        } else {
            statusElement.textContent = '🔴 Inactive';
            statusElement.style.color = '#e74c3c';
        }
    }
    
    if (statusIcon) {
        if (this.isFocused) {
            statusIcon.className = 'fas fa-check-circle';
            statusIcon.style.color = '#27ae60';
        } else {
            statusIcon.className = 'fas fa-exclamation-circle';
            statusIcon.style.color = '#e74c3c';
        }
    }
    
    if (focusLostElement) {
        focusLostElement.textContent = this.focusLossCount;
    }
    
    if (focusGainedElement) {
        focusGainedElement.textContent = this.focusGainedCount;
    }
    
    if (tabSwitchElement) {
        tabSwitchElement.textContent = this.tabSwitchCount;
    }
    
    if (lastFocusLostElement) {
        lastFocusLostElement.textContent = this.getLastFocusLostTime();
    }
};

ExamEventLogger.prototype.getLastFocusLostTime = function() {
    if (this.focusLossCount === 0) {
        return 'Never';
    }
    // Return time of last focus loss event
    var events = this.eventLog.filter(function(e) {
        return e.event_type === 'browser_focus_lost';
    });
    if (events.length > 0) {
        var lastEvent = events[events.length - 1];
        var date = new Date(lastEvent.timestamp);
        return date.toLocaleTimeString();
    }
    return 'Never';
};

ExamEventLogger.prototype.logEvent = function(eventType, remarks) {
    if (typeof remarks === 'undefined') {
        remarks = '';
    }

    var eventData = {
        session_id: this.sessionId,
        candidate_id: this.candidateId,
        event_type: eventType,
        remarks: remarks,
        timestamp: new Date().toISOString()
    };

    this.eventLog.push(eventData);
    this.sendToServer(eventData);
    
    // Add to event log display
    this.addEventToDisplay(eventType, remarks);
};

ExamEventLogger.prototype.addEventToDisplay = function(eventType, remarks) {
    var eventLogElement = document.getElementById('eventLogList');
    
    if (eventLogElement) {
        var li = document.createElement('li');
        var time = new Date().toLocaleTimeString();
        
        // Add event type class for styling
        var eventSpan = document.createElement('span');
        eventSpan.className = 'event-type ' + eventType;
        eventSpan.textContent = eventType;
        
        var timeSpan = document.createElement('span');
        timeSpan.className = 'event-time';
        timeSpan.textContent = time;
        
        var remarksSpan = document.createElement('span');
        remarksSpan.className = 'event-remarks';
        remarksSpan.textContent = remarks;
        
        li.appendChild(timeSpan);
        li.appendChild(eventSpan);
        li.appendChild(remarksSpan);
        
        // Remove waiting message if present
        var waitingMessage = eventLogElement.querySelector('.waiting-message');
        if (waitingMessage) {
            waitingMessage.remove();
        }
        
        if (eventLogElement.firstChild) {
            eventLogElement.insertBefore(li, eventLogElement.firstChild);
        } else {
            eventLogElement.appendChild(li);
        }
        
        // Keep only last 50 events
        while (eventLogElement.children.length > 50) {
            eventLogElement.removeChild(eventLogElement.lastChild);
        }
    }
};

ExamEventLogger.prototype.sendToServer = function(eventData) {
    var self = this;

    fetch('/log-event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(eventData)
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.status === 'success') {
            console.log('✅ Event logged successfully');
        } else {
            console.log('❌ Failed to log event:', data.message);
        }
    })
    .catch(function(error) {
        console.error('Error logging event:', error);
    });
};

ExamEventLogger.prototype.getEventSummary = function() {
    return {
        sessionId: this.sessionId,
        candidateId: this.candidateId,
        totalEvents: this.eventLog.length,
        tabSwitches: this.tabSwitchCount,
        focusLoss: this.focusLossCount,
        focusGained: this.focusGainedCount,
        totalInactiveDuration: this.totalInactiveDuration,
        events: this.eventLog
    };
};

// ===== INITIALIZE ON PAGE LOAD =====
document.addEventListener('DOMContentLoaded', function() {
    var sessionIdElement = document.getElementById('sessionId');
    var candidateIdElement = document.getElementById('candidateId');
    
    var sessionId = sessionIdElement ? sessionIdElement.value : null;
    var candidateId = candidateIdElement ? candidateIdElement.value : null;
    
    if (sessionId && candidateId) {
        window.eventLogger = new ExamEventLogger(sessionId, candidateId);
    } else {
        console.log('⚠️ Session ID or Candidate ID not found. Event logger not initialized.');
    }
});