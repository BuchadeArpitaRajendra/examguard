# Database Design - ExamGuard

## 📊 Overview

This document describes the database design for the ExamGuard online examination monitoring system. SQLite is used as the database management system.

---

## 🎯 Database Purpose

The database stores:
- Candidate registration information
- Exam session data
- (Future: Event logs, integrity scores, alerts)

---

## 📐 Entity Relationship Diagram (ERD)
┌─────────────────────────────┐
│ Candidate │
├─────────────────────────────┤
│ candidate_id (PK) INTEGER │◄────┐
│ name TEXT │ │
│ email TEXT (UK) │ │
│ password TEXT │ │
│ photo_path TEXT │ │
│ created_at TIMESTAMP │ │
└─────────────────────────────┘ │
│ 1 to Many
│
┌─────────────────────────────┐ │
│ Session │ │
├─────────────────────────────┤ │
│ session_id (PK) INTEGER │ │
│ candidate_id (FK) INTEGER ├─────┘
| start_time TIMESTAMP│
│ end_time TIMESTAMP│
│ status TEXT │
└─────────────────────────────┘


---

## 📋 Table Definitions

### 1. Candidate Table

**Purpose:** Stores registered candidate information.

**Table Name:** `candidate`

| Column Name | Data Type | Constraints | Description |
|-------------|-----------|-------------|-------------|
| `candidate_id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier for each candidate |
| `name` | TEXT | NOT NULL | Candidate's full name |
| `email` | TEXT | NOT NULL, UNIQUE | Candidate's email address (used for login) |
| `password` | TEXT | NOT NULL | Hashed password (never store plain text!) |
| `photo_path` | TEXT | NULL | File path to candidate's profile photo |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Registration date and time |

**SQL Creation Statement:**
```sql
CREATE TABLE IF NOT EXISTS candidate (
    candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    photo_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


### 2.Session Table
Purpose: Tracks exam sessions for candidates.

Table Name: session

Column Name	Data Type	Constraints	Description
session_id	INTEGER	PRIMARY KEY, AUTOINCREMENT	Unique identifier for each session
candidate_id	INTEGER	NOT NULL, FOREIGN KEY	References candidate.candidate_id
start_time	TIMESTAMP	DEFAULT CURRENT_TIMESTAMP	Session start timestamp
end_time	TIMESTAMP	NULL	Session end timestamp (NULL if active)
status	TEXT	DEFAULT 'active'	Session status: 'active', 'paused', 'completed'

CREATE TABLE IF NOT EXISTS session (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    status TEXT DEFAULT 'active',
    FOREIGN KEY (candidate_id) REFERENCES candidate(candidate_id)
);