# TRUVEX — AI-Powered Universal Trust Infrastructure

> **Verify. Connect. Trust.**  
> *B2B2C Independent Communication Verification Platform*  
> **CMRIT × DetectifAI Hackathon — Track 03: The Trust Layer**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![DetectifAI](https://img.shields.io/badge/DetectifAI-Aletheia%20%26%20Eidos-000000)](https://platform.detectif.ai)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## The Problem
Customers frequently receive fraudulent phone calls and messages from individuals impersonating bank representatives, insurance agents, recruiters, and customer support personnel. Traditional caller ID cannot establish:
1. Whether the caller is genuinely employed by the stated enterprise.
2. Whether the caller's voice is biologically authentic or an AI deepfake clone.
3. Whether the caller possesses actual corporate authority to initiate that conversation.
4. Whether the session is currently active and valid.

## The Solution: Five-Layer Trust Engine
TRUVEX provides an independent, out-of-band verification layer. When an enterprise representative prepares to contact a customer, TRUVEX issues an ephemeral, cryptographically secure **Trust ID** after evaluating five verification layers:

1. **Business Verification**: Enterprise vetting and platform administrator approval.
2. **Employee Identity Verification**: Active directory records, credential status, and role validation.
3. **Voice Authenticity Assessment**: DetectifAI **Aletheia** deepfake detection (`/v1/deepfake/detect`) ensuring the audio is a real human vocal tract.
4. **Speaker Biometrics**: DetectifAI **Eidos** speaker verification (`/v1/speakers/verify`) matching the voice against the enrolled employee profile.
5. **Session Verification**: Ephemeral high-entropy Trust ID (`TRX-XXXX-XXXX`) with short TTL (5–10 min) and customer challenge binding.

---

## Technology Stack

- **Frontend**: Semantic HTML5, modern CSS3, Vanilla JavaScript (zero external framework bloat), Browser MediaRecorder API.
- **Backend**: Python 3.14, FastAPI, SQLAlchemy, SQLite, Pydantic v2, HTTPX.
- **AI Models**: DetectifAI **Aletheia** (deepfake detection) & **Eidos** (speaker enrollment & verification).

---

## Directory Structure

```text
truvex-platform/
├── frontend/             # HTML5/CSS3/Vanilla JS portals
├── backend/              # FastAPI application, SQLAlchemy models & services
│   ├── routes/           # Auth, Companies, Employees, Sessions
│   ├── services/         # DetectifAI Aletheia, Eidos, Trust Engine
│   └── tests/            # Automated test suite
├── docs/                 # Architecture, API contract, and team tasks
├── PROJECT_RULES.md      # Security standards and AI guidelines
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # Project documentation
```

---

## Quickstart (Development Setup)

### 1. Clone & Navigate
```bash
git clone https://github.com/rounitraj7416/Truvex.git truvex-platform
cd truvex-platform
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and insert your DetectifAI API key:
# DETECTIF_API_KEY=dtf_live_...
```

### 3. Setup Virtual Environment & Install Dependencies
```bash
python -m venv .venv

# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# On Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 4. Start the Development Server
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

- **TRUVEX Portal**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **System Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## Team & Roles

- **Anany**: Principal Architect & AI Integration Specialist (Architecture, DetectifAI integration, Trust Engine)
- **Arunav**: Senior Frontend Engineer (Portals, UI/UX, Audio recording interface)
- **Rounit**: Senior Backend & Security Engineer (Database, Auth, Session management, Tests)
