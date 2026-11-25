# TRUVEX Team Responsibilities & File Ownership Matrix

## 1. Team Role Allocation

### **Anany** — Principal Architect & AI Integration Lead
- **Domain**: Overall system architecture, DetectifAI API integration, AI services, and Five-Layer Trust Engine.
- **Key Responsibilities**:
  - Design and enforce system architecture and API contracts.
  - Implement DetectifAI Aletheia deepfake detection client (`aletheia.py`).
  - Implement DetectifAI Eidos speaker enrollment and verification client (`eidos.py`).
  - Engineer the composite Five-Layer Trust Engine scoring algorithm (`trust_engine.py`).
  - Orchestrate end-to-end integration across frontend, backend, and external AI services.
  - Final security audit, credential hygiene, and system hardening.

### **Arunav** — Senior Frontend Engineer
- **Domain**: Complete user interface, browser audio recording, and client-side interactions.
- **Key Responsibilities**:
  - Design and build the TRUVEX design system and responsive UI in modern vanilla HTML5, CSS3, and JavaScript.
  - Build the public Landing Page (`index.html`).
  - Build the Unified Login Portal (`login.html`).
  - Build the Employee Verification & Voice Enrollment Console (`employee.html`).
  - Build the Customer Trust ID Lookup & Fraud Reporting View (`customer.html`).
  - Build the Enterprise Management Dashboard (`enterprise.html`).
  - Build the Platform Superadmin Panel (`admin.html`).
  - Implement browser audio recording via the Web Audio & `MediaRecorder` API with countdowns and visual audio level meters.

### **Rounit** — Senior Backend & Security Engineer
- **Domain**: Database persistence, authentication, company/employee management, and session lifecycle.
- **Key Responsibilities**:
  - Design SQLAlchemy database schema and migration models (`database.py`, `models.py`).
  - Build Pydantic request/response validation schemas (`schemas.py`).
  - Implement secure user authentication using bcrypt password hashing and JWT access tokens (`routes/auth.py`).
  - Build Company Onboarding & Approval workflow (`routes/companies.py`).
  - Build Employee Directory & Permissions management (`routes/employees.py`).
  - Implement cryptographically secure Trust ID generation and TTL-based session management (`routes/verification.py`).
  - Develop automated unit and integration tests with `pytest` (`tests/`).

---

## 2. File Ownership Matrix

| File / Directory | Primary Owner | Secondary Reviewer | Status in Phase 1 |
| :--- | :--- | :--- | :--- |
| `docs/architecture.md` | **Anany** | Arunav, Rounit | Complete |
| `docs/api_contract.md` | **Anany** | Rounit | Complete |
| `docs/team_tasks.md` | **Anany** | Arunav, Rounit | Complete |
| `PROJECT_RULES.md` | **Anany** | Arunav, Rounit | Complete |
| `requirements.txt` | **Anany** | Rounit | Complete |
| `.env.example` | **Anany** | Rounit | Complete |
| `.gitignore` | **Anany** | Rounit | Complete |
| `backend/main.py` | **Anany** | Rounit | Scaffolded (Phase 1) |
| `backend/database.py` | **Rounit** | Anany | Placeholder (Phase 1) |
| `backend/models.py` | **Rounit** | Anany | Placeholder (Phase 1) |
| `backend/schemas.py` | **Rounit** | Anany | Placeholder (Phase 1) |
| `backend/routes/auth.py` | **Rounit** | Anany | Placeholder (Phase 1) |
| `backend/routes/companies.py` | **Rounit** | Anany | Placeholder (Phase 1) |
| `backend/routes/employees.py` | **Rounit** | Anany | Placeholder (Phase 1) |
| `backend/routes/verification.py` | **Rounit** | Anany | Placeholder (Phase 1) |
| `backend/routes/admin.py` | **Rounit** | Anany | Placeholder (Phase 1) |
| `backend/services/aletheia.py` | **Anany** | Rounit | Skeleton (Phase 1) |
| `backend/services/eidos.py` | **Anany** | Rounit | Skeleton (Phase 1) |
| `backend/services/trust_engine.py` | **Anany** | Rounit | Skeleton (Phase 1) |
| `backend/tests/test_health.py` | **Rounit** | Anany | Complete (Phase 1) |
| `frontend/index.html` | **Arunav** | Anany | Scaffolded (Phase 1) |
| `frontend/login.html` | **Arunav** | Rounit | Placeholder (Phase 1) |
| `frontend/employee.html` | **Arunav** | Anany | Placeholder (Phase 1) |
| `frontend/customer.html` | **Arunav** | Anany | Placeholder (Phase 1) |
| `frontend/enterprise.html` | **Arunav** | Rounit | Placeholder (Phase 1) |
| `frontend/admin.html` | **Arunav** | Rounit | Placeholder (Phase 1) |
| `frontend/css/style.css` | **Arunav** | Anany | Scaffolded (Phase 1) |
| `frontend/js/main.js` | **Arunav** | Anany | Scaffolded (Phase 1) |
