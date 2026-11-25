# TRUVEX Project Rules & Engineering Standards

## 1. Security & Credentials
- **Zero Frontend Secret Exposure**: Under no circumstances should any API key, signing secret, or internal credential (including `DETECTIF_API_KEY`) be referenced, hardcoded, or exposed in frontend code, client-side scripts, or HTML templates.
- **Environment Isolation**: All credentials and environment configurations must be loaded via server-side environment variables (`.env`) through `pydantic-settings`.
- **Git Hygiene**: Never commit `.env`, `*.db`, `*.sqlite`, `.venv`, or temporary audio capture directories (`temp_audio/`, `uploads/`). The `.gitignore` must remain strictly enforced.
- **Cryptographic Trust IDs**: Trust IDs must be generated using cryptographically strong pseudo-random number generators (`secrets` module) with high entropy (e.g., base32/base62 alphanumeric strings formatted as `TRX-XXXX-XXXX`), never sequential IDs or timestamps.
- **Session Expiry & Revocation**: Trust IDs must be bound to a strict Time-To-Live (TTL) of 5 to 10 minutes. Expired or revoked Trust IDs must immediately be rejected with an explicit rejection status.

## 2. AI Ethics & DetectifAI Standards
- **Authentic API Integration**: All external calls to DetectifAI must strictly use the official API endpoints (`/v1/deepfake/detect`, `/v1/speakers/enroll`, `/v1/speakers/verify`) as documented in [https://platform.detectif.ai/docs](https://platform.detectif.ai/docs).
- **No Fabricated AI Responses**: Never invent response fields or manufacture fake AI confidence metrics in production code. If the DetectifAI service is unavailable, unreachable, or in development mock mode, the system must clearly report `status: "manual_review"` or `status: "mock_test_mode"` with an explicit indicator.
- **Informed Consent**: Explicit user/employee consent is legally and architecturally required before capturing, recording, or storing any biometric voice sample.
- **Audio Lifecycle & Privacy**: Temporary audio clips submitted for verification must be securely handled, processed in-memory or in isolated temporary storage, and deleted promptly after scoring is completed.
- **Signals, Not Absolute Proof**: In accordance with DetectifAI guidelines, AI scores are probabilistic evidence rather than absolute legal proof. Borderline scores must trigger a Step-Up Authentication or Manual Verification flag rather than a silent failure or blind pass.

## 3. Scope & Truth in Advertising
- **Out-of-Band Session Verification**: TRUVEX provides out-of-band communication verification through cryptographically bound Trust IDs. Do not claim direct carrier-level telephone interception or telecommunication signaling hacking.
- **Demonstration Data**: All organizations and accounts created for testing and demonstration must use clearly designated fictional entities (e.g., "Apex Global Bank", "Northwind Insurance", "Starlight Health").

## 4. Architecture & Coding Conventions
- **Backend (Python 3.14 / FastAPI)**:
  - Strict PEP 8 styling, type annotations, and Pydantic v2 schemas for all request/response models.
  - Async route handlers where appropriate, utilizing `httpx.AsyncClient` for DetectifAI external HTTP calls.
  - Layered architecture: `routes/` -> `services/` -> `database.py` / `models.py`.
- **Frontend (Vanilla HTML5 / CSS3 / JavaScript)**:
  - Clean semantic markup with an accessible, dark-themed cyberpunk/fintech aesthetic.
  - Modular JS files with clear separation of DOM operations, API calls, and Web Audio / MediaRecorder management.
  - Clear user-facing error states, loading spinners, and audio recording progress feedback.

## 5. Collaboration & Review Gates
- **Branching & Commits**: Work through feature branches with semantic commit messages (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`).
- **Review Gates**: Destructive commands (dropping tables, force pushing, hard resets) and remote git pushes require explicit review and approval.
