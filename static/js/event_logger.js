class ExamEventLogger {
    constructor(sessionId, candidateId) {
        this.sessionId = sessionId;
        this.candidateId = candidateId;
        this.isExamActive = false;
        this.tabSwitchCount = 0;
        this.focusLossCount = 0;
        this.startTime = null;
        this.eventLog = [];
        
        this.init();
    }

    init() {
        // Track page visibility (tab switches)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.logEvent('tab_switched', 'Browser tab switched');
                this.tabSwitchCount++;
                
                // Check for suspicious activity
                if (this.tabSwitchCount > 3) {
                    this.logEvent('multiple_tab_switches', 
                        `Multiple tab switches detected: ${this.tabSwitchCount}`);
                }
            }
        });

        // Track window focus
        window.addEventListener('blur', () => {
            this.logEvent('focus_lost', 'Browser focus lost');
            this.focusLossCount++;
        });

        window.addEventListener('focus', () => {
            this.logEvent('focus_gained', 'Browser focus regained');
        });

        // Track copy attempts
        document.addEventListener('copy', (e) => {
            this.logEvent('copy_attempted', 'Copy attempt detected');
        });

        // Track paste attempts
        document.addEventListener('paste', (e) => {
            this.logEvent('paste_attempted', 'Paste attempt detected');
        });

        // Track right-click
        document.addEventListener('contextmenu', (e) => {
            this.logEvent('right_click_detected', 'Right-click detected');
            e.preventDefault(); // Prevent context menu
        });

        // Track key combinations (Ctrl+C, Ctrl+V, Ctrl+U, Ctrl+S)
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey) {
                switch(e.key) {
                    case 'c':
                        this.logEvent('copy_attempted', 'Ctrl+C copy attempt');
                        break;
                    case 'v':
                        this.logEvent('paste_attempted', 'Ctrl+V paste attempt');
                        break;
                    case 'u':
                        this.logEvent('view_source_attempt', 'Ctrl+U view source attempt');
                        e.preventDefault();
                        break;
                    case 's':
                        this.logEvent('save_attempt', 'Ctrl+S save attempt');
                        e.preventDefault();
                        break;
                }
            }
            // F12 key (developer tools)
            if (e.key === 'F12') {
                this.logEvent('dev_tools_attempt', 'F12 developer tools attempt');
                e.preventDefault();
            }
        });

        // Track before unload (page refresh/close)
        window.addEventListener('beforeunload', (e) => {
            this.logEvent('session_timeout', 'Page refresh or close detected');
        });

        console.log('✅ Exam Event Logger initialized');
        console.log(`📋 Session ID: ${this.sessionId}`);
        console.log(`👤 Candidate ID: ${this.candidateId}`);
    }

    logEvent(eventType, remarks = '') {
        const eventData = {
            session_id: this.sessionId,
            candidate_id: this.candidateId,
            event_type: eventType,
            remarks: remarks,
            timestamp: new Date().toISOString()
        };

        // Store locally
        this.eventLog.push(eventData);

        // Send to server
        this.sendToServer(eventData);

        // Console log for debugging
        console.log(`📝 Event: ${eventType} - ${remarks}`);
        
        // Update counters
        this.updateDisplay(eventType);
    }

    sendToServer(eventData) {
        fetch('/log-event', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(eventData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log('✅ Event logged successfully');
            } else {
                console.log('❌ Failed to log event:', data.message);
            }
        })
        .catch(error => {
            console.error('Error logging event:', error);
        });
    }

    updateDisplay(eventType) {
        // Update the UI with event counts
        const tabSwitchElement = document.getElementById('tabSwitchCount');
        const focusLossElement = document.getElementById('focusLossCount');
        const eventLogElement = document.getElementById('eventLogList');

        if (tabSwitchElement && eventType === 'tab_switched') {
            tabSwitchElement.textContent = this.tabSwitchCount;
        }

        if (focusLossElement && eventType === 'focus_lost') {
            focusLossElement.textContent = this.focusLossCount;
        }

        // Add to event log display
        if (eventLogElement) {
            const li = document.createElement('li');
            li.textContent = `${new Date().toLocaleTimeString()} - ${eventType}`;
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
    }

    getEventSummary() {
        return {
            sessionId: this.sessionId,
            candidateId: this.candidateId,
            totalEvents: this.eventLog.length,
            tabSwitches: this.tabSwitchCount,
            focusLoss: this.focusLossCount,
            events: this.eventLog
        };
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    const sessionId = document.getElementById('sessionId')?.value;
    const candidateId = document.getElementById('candidateId')?.value;
    
    if (sessionId && candidateId) {
        window.eventLogger = new ExamEventLogger(sessionId, candidateId);
    }
});