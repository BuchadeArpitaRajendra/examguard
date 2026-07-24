# Agile Documentation - ExamGuard

## 📋 Project Overview

**Project Name:** ExamGuard - Online Exam Monitoring Platform  
**Team Member:** Buchade Arpita Rajendra  
**Start Date:** July 2026  
**Status:** In Progress  

---

## 🎯 Project Vision

Build a secure online examination monitoring platform that helps educational institutions conduct fair assessments with integrity analytics.

---

## 📊 Sprint Backlog

### Sprint 1: Foundation (Week 1-2) ✅ In Progress

**Goal:** Setup project infrastructure and database

| Task ID | Task Description | Status | Story Points | Priority |
|---------|------------------|--------|--------------|----------|
| S1-001 | Setup Flask application | ✅ Done | 3 | High |
| S1-002 | Design SQLite database | ✅ Done | 5 | High |
| S1-003 | Create Candidate and Session tables | ✅ Done | 5 | High |
| S1-004 | Setup GitHub repository | ✅ Done | 2 | High |
| S1-005 | Add MIT License | ✅ Done | 1 | Medium |
| S1-006 | Create Registration page (HTML) | ⬜ Pending | 5 | High |
| S1-007 | Create Registration page (CSS styling) | ⬜ Pending | 3 | High |
| S1-008 | Connect registration to database | ⬜ Pending | 5 | High |
| S1-009 | Implement password hashing | ⬜ Pending | 3 | High |
| S1-010 | Create Login system | ⬜ Pending | 5 | High |
| S1-011 | User session management | ⬜ Pending | 3 | Medium |

**Sprint Goal:** ✅ Complete core authentication and database setup

---

### Sprint 2: Monitoring Modules (Week 3-4) ⬜ Not Started

**Goal:** Implement face detection and browser monitoring

| Task ID | Task Description | Status | Story Points | Priority |
|---------|------------------|--------|--------------|----------|
| S2-001 | OpenCV integration setup | ⬜ Pending | 5 | High |
| S2-002 | Photo capture at registration | ⬜ Pending | 3 | High |
| S2-003 | Real-time face detection | ⬜ Pending | 8 | High |
| S2-004 | Face presence logging | ⬜ Pending | 5 | High |
| S2-005 | Browser activity logging (JS) | ⬜ Pending | 5 | High |
| S2-006 | Tab-switch detection | ⬜ Pending | 5 | High |
| S2-007 | Event storage in SQLite | ⬜ Pending | 3 | Medium |

---

### Sprint 3: Scoring & Analytics (Week 5-6) ⬜ Not Started

**Goal:** Implement integrity scoring and analytics

| Task ID | Task Description | Status | Story Points | Priority |
|---------|------------------|--------|--------------|----------|
| S3-001 | Design integrity scoring algorithm | ⬜ Pending | 5 | High |
| S3-002 | Implement weighted event scoring | ⬜ Pending | 5 | High |
| S3-003 | Calculate face presence ratio | ⬜ Pending | 3 | High |
| S3-004 | Normalize scores (0-100) | ⬜ Pending | 3 | Medium |
| S3-005 | Risk labelling (LOW/MEDIUM/HIGH) | ⬜ Pending | 3 | Medium |
| S3-006 | Data Science analytics setup | ⬜ Pending | 5 | Medium |
| S3-007 | Generate score distributions | ⬜ Pending | 3 | Medium |
| S3-008 | Event frequency heatmaps | ⬜ Pending | 5 | Medium |
| S3-009 | K-Means clustering implementation | ⬜ Pending | 8 | Medium |

---

### Sprint 4: AI & Dashboard (Week 7-8) ⬜ Not Started

**Goal:** Implement AI reports and dashboard

| Task ID | Task Description | Status | Story Points | Priority |
|---------|------------------|--------|--------------|----------|
| S4-001 | LangChain setup | ⬜ Pending | 5 | High |
| S4-002 | AI report generation | ⬜ Pending | 8 | High |
| S4-003 | Streamlit dashboard setup | ⬜ Pending | 5 | High |
| S4-004 | Live monitoring view | ⬜ Pending | 5 | High |
| S4-005 | Real-time alerts view | ⬜ Pending | 3 | Medium |
| S4-006 | Analytics visualization | ⬜ Pending | 5 | Medium |
| S4-007 | Export module (JSON/CSV) | ⬜ Pending | 3 | Medium |
| S4-008 | End-to-end testing | ⬜ Pending | 5 | High |
| S4-009 | Documentation and presentation | ⬜ Pending | 5 | High |

---

## 📝 Daily Standup Log

### Sprint 1

**Date: 2026-07-23**
- **Yesterday (What I did):** ✅ Flask application setup completed, ✅ GitHub repository created, ✅ MIT License added
- **Today (What I'll do):** 🔄 Designing SQLite database, 🔄 Creating Candidate and Session tables
- **Blockers:** None
- **Notes:** Database design is going well. Next will be registration page.

**Date: 2026-07-24**
- **Yesterday (What I did):** ✅ Database created, ✅ Tables designed, ✅ AGILE.md created
- **Today (What I'll do):** 🔄 Start building registration page HTML, 🔄 Design CSS styling
- **Blockers:** None
- **Notes:** Ready to move to frontend development.

---

## 🔄 Sprint Retrospective

### Sprint 1 Retrospective (To be completed after Sprint 1)

**What went well:**
- Flask setup was smooth
- Database design completed successfully
- GitHub repository properly configured

**What could be improved:**
- Need to break down tasks into smaller pieces
- Start frontend work earlier

**Action items for next sprint:**
- Create detailed user stories
- Implement password hashing
- Complete registration and login

---

## 📊 Burn Down Chart

| Date | Planned Tasks | Completed | Remaining |
|------|---------------|-----------|-----------|
| Week 1 | 5 | 4 | 1 |
| Week 2 | 6 | - | 6 |
| **Total** | **11** | **4** | **7** |

---

## 📋 Definition of Done

A task is considered "Done" when:
- [ ] Code is written and works as expected
- [ ] Unit tests are written and passing
- [ ] Code is reviewed
- [ ] Documentation is updated
- [ ] Changes are committed and pushed to GitHub
- [ ] No breaking changes introduced

---

## 📎 User Stories

### Sprint 1 User Stories

**US-001:** As a candidate, I want to register on the platform so that I can take exams.
- **Acceptance Criteria:**
  - Registration form with name, email, password
  - Data stored in SQLite database
  - Password is hashed for security
  - Success message after registration

**US-002:** As a candidate, I want to log in securely so that I can access my exam dashboard.
- **Acceptance Criteria:**
  - Login form with email and password
  - Password verification
  - Session creation on successful login
  - Redirect to dashboard

**US-003:** As an administrator, I want to view candidate data so that I can manage users.
- **Acceptance Criteria:**
  - List all registered candidates
  - View candidate details
  - View session history

---

## 🚨 Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Database performance issues | Medium | Low | Use proper indexes |
| Security vulnerabilities | High | Medium | Implement password hashing, input validation |
| OpenCV integration issues | High | Medium | Test early with webcam |
| Time constraints | High | Medium | Focus on core features first |

---

## 🔗 Resources

- [Project Repository](https://github.com/BuchadeArpitaRajendra/examguard)
- [MIT License](LICENSE)
- [Database Design](docs/database_design.md)

---

**Last Updated:** 2026-07-24


---

## 🚀 Part 3: Add to Git and Push

### Step 3.1: Add Files to Git

```bash
# Add AGILE.md
git add AGILE.md

# Add docs folder
git add docs/

# Check status
git status