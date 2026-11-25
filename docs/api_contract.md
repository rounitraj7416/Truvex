# TRUVEX API Contract & Specification

**Specification Version**: 1.0.0  
**Base URL**: `http://127.0.0.1:8000/api`  
**Content-Type**: `application/json` (unless `multipart/form-data` for audio uploads)

---

## 1. General Principles & Error Standards

### 1.1 Authentication
Endpoints marked with `[Protected]` require an HTTP Authorization header:
```http
Authorization: Bearer <jwt_access_token>
```

### 1.2 Standard Error Response Schema
All error responses adhere to the standard JSON structure:
```json
{
  "success": false,
  "error": {
    "code": "resource_not_found",
    "message": "The requested entity could not be found.",
    "param": "trust_id",
    "status_code": 404
  },
  "timestamp": "2026-11-25T10:00:00Z"
}
```

---

## 2. Core Internal Endpoints

### 2.1 System Health
#### `GET /api/health`
Checks backend service availability and configuration state.
- **Access**: Public
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "app": "TRUVEX",
  "version": "0.1.0",
  "environment": "development",
  "timestamp": "2026-11-25T10:00:00.000Z"
}
```

---

### 2.2 Authentication & Identity

#### `POST /api/auth/register`
Registers a new enterprise administrator or platform user.
- **Access**: Public
- **Request Body**:
```json
{
  "email": "security@apexbank.example",
  "password": "StrongPassword123!",
  "full_name": "Sarah Connor",
  "role": "enterprise_admin",
  "company_id": null
}
```
- **Response `201 Created`**:
```json
{
  "success": true,
  "user": {
    "id": "usr_99f2b8a1",
    "email": "security@apexbank.example",
    "full_name": "Sarah Connor",
    "role": "enterprise_admin",
    "created_at": "2026-11-25T10:00:00Z"
  }
}
```

#### `POST /api/auth/login`
Authenticates a user and issues a JWT token.
- **Access**: Public
- **Request Body**:
```json
{
  "email": "security@apexbank.example",
  "password": "StrongPassword123!"
}
```
- **Response `200 OK`**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "expires_in_seconds": 3600,
  "user": {
    "id": "usr_99f2b8a1",
    "email": "security@apexbank.example",
    "role": "enterprise_admin"
  }
}
```

---

### 2.3 Company Management

#### `POST /api/companies/register`
Submits an organization for TRUVEX onboarding.
- **Access**: `[Protected: Enterprise Admin]`
- **Request Body**:
```json
{
  "name": "Apex Global Bank",
  "domain": "apexbank.example",
  "registration_number": "REG-IN-2026-0912",
  "industry": "Banking & Financial Services",
  "contact_email": "security@apexbank.example"
}
```
- **Response `201 Created`**:
```json
{
  "success": true,
  "company": {
    "id": "comp_a81b3c4d",
    "name": "Apex Global Bank",
    "status": "pending_approval",
    "created_at": "2026-11-25T10:00:00Z"
  }
}
```

#### `PATCH /api/companies/{company_id}/status`
Allows a platform administrator to approve or suspend an organization.
- **Access**: `[Protected: Platform Superadmin]`
- **Request Body**:
```json
{
  "status": "approved",
  "notes": "Verified business charter and compliance."
}
```
- **Response `200 OK`**:
```json
{
  "success": true,
  "company_id": "comp_a81b3c4d",
  "status": "approved",
  "updated_at": "2026-11-25T10:05:00Z"
}
```

---

### 2.4 Employee Directory & Voice Enrollment

#### `POST /api/employees`
Enrolls an employee under an approved enterprise.
- **Access**: `[Protected: Enterprise Admin]`
- **Request Body**:
```json
{
  "company_id": "comp_a81b3c4d",
  "full_name": "Marcus Vance",
  "employee_code": "AV-4089",
  "email": "m.vance@apexbank.example",
  "department": "Fraud Prevention Operations",
  "can_initiate_calls": true
}
```
- **Response `201 Created`**:
```json
{
  "success": true,
  "employee": {
    "id": "emp_018f9e12",
    "company_id": "comp_a81b3c4d",
    "speaker_id": "trx_spk_emp_018f9e12",
    "voice_enrolled": false,
    "status": "active"
  }
}
```

#### `POST /api/employees/{employee_id}/enroll-voice`
Submits an audio sample (15–60s) to enroll the employee's voiceprint via DetectifAI Eidos.
- **Access**: `[Protected: Employee / Admin]`
- **Content-Type**: `multipart/form-data`
- **Form Fields**:
  - `file`: Audio binary (WAV, MP3, WebM; min 10s speech).
  - `consent`: `true` (Boolean, mandatory).
- **Response `200 OK`**:
```json
{
  "success": true,
  "employee_id": "emp_018f9e12",
  "speaker_id": "trx_spk_emp_018f9e12",
  "samples_enrolled": 1,
  "speech_duration_seconds": 18.4,
  "status": "voice_enrolled"
}
```

---

### 2.5 Verification & Session Lifecycle

#### `POST /api/sessions/create-trust-id`
Employee records fresh voice sample before outbound call; system evaluates through DetectifAI Aletheia & Eidos.
- **Access**: `[Protected: Employee]`
- **Content-Type**: `multipart/form-data`
- **Form Fields**:
  - `file`: Fresh voice recording (3–60s, min 2s speech).
  - `customer_ref`: Masked identifier (e.g. `CUST-***-9921`).
  - `call_topic`: `Account Security Review`.
- **Response `200 OK`**:
```json
{
  "success": true,
  "trust_id": "TRX-4821-9943",
  "expires_in_seconds": 600,
  "expires_at": "2026-11-25T10:15:00Z",
  "trust_score": 96.5,
  "verdict": "VERIFIED",
  "layer_results": {
    "business_verification": {"status": "PASS", "score": 100},
    "employee_verification": {"status": "PASS", "score": 100},
    "voice_authenticity": {"status": "PASS", "score": 97.2, "verdict": "real", "raw_score": 0.028},
    "speaker_biometrics": {"status": "PASS", "score": 92.0, "decision": "match", "similarity": 0.84},
    "authority_verification": {"status": "PASS", "score": 100}
  }
}
```

#### `GET /api/verify/{trust_id}`
Allows a customer to look up and independently inspect the validity of a Trust ID.
- **Access**: Public
- **Response `200 OK`**:
```json
{
  "valid": true,
  "trust_id": "TRX-4821-9943",
  "status": "ACTIVE",
  "company_name": "Apex Global Bank",
  "company_verified": true,
  "representative_name": "Marcus Vance",
  "department": "Fraud Prevention Operations",
  "call_topic": "Account Security Review",
  "created_at": "2026-11-25T10:05:00Z",
  "expires_at": "2026-11-25T10:15:00Z",
  "remaining_seconds": 540,
  "trust_level": "MAXIMUM_TRUST",
  "audio_checks": {
    "deepfake_verdict": "real",
    "voice_biometrics_match": true
  }
}
```

#### `POST /api/reports/fraud`
Enables a customer to report a suspicious, spoofed, or unverified interaction.
- **Access**: Public
- **Request Body**:
```json
{
  "claimed_trust_id": "TRX-4821-9943",
  "claimed_company": "Apex Global Bank",
  "caller_phone": "+919876543210",
  "description": "Caller claimed to be Marcus Vance but Trust ID had expired.",
  "severity": "high"
}
```
- **Response `201 Created`**:
```json
{
  "success": true,
  "report_id": "rep_7f01a93b",
  "message": "Incident report logged. Security team notified."
}
```

---

## 3. Official External DetectifAI Integration Contracts

### 3.1 Aletheia: Deepfake Detection
- **URL**: `POST https://platform.detectif.ai/v1/deepfake/detect`
- **Headers**:
  - `Authorization`: `Bearer <DETECTIF_API_KEY>`
  - `Idempotency-Key`: `<UUIDv4>`
- **Body**: `multipart/form-data`
  - `file`: Audio binary (WAV, MP3, WebM; max 100 MB).
- **Official Success Response `200 OK`**:
```json
{
  "request_id": "req_8f14e45fceea167a5a36dedd",
  "operation_id": "op_6f1ed002ab5595859014ebf0951522d9",
  "object": "deepfake.detection",
  "result": {
    "verdict": "real",
    "score": 0.07,
    "duration_seconds": 12.4
  }
}
```

### 3.2 Eidos: Voice Enrollment
- **URL**: `POST https://platform.detectif.ai/v1/speakers/enroll`
- **Headers**:
  - `Authorization`: `Bearer <DETECTIF_API_KEY>`
  - `Idempotency-Key`: `<UUIDv4>`
- **Body**: `multipart/form-data`
  - `file`: Audio binary (15–60s, min 10s speech).
  - `speaker_id`: String (`^[A-Za-z0-9_.:-]{1,64}$`).
  - `display_name`: Optional string (max 128 chars).
- **Official Success Response `200 OK`**:
```json
{
  "request_id": "req_a912...",
  "operation_id": "op_b192...",
  "object": "speaker.enrollment",
  "speaker": {
    "speaker_id": "trx_spk_emp_018f9e12",
    "display_name": "Marcus Vance",
    "samples": 1,
    "created_at": "2026-11-25T10:00:00Z",
    "updated_at": "2026-11-25T10:00:00Z"
  },
  "quality": {
    "speech_seconds": 18.2,
    "duration_seconds": 22.0
  },
  "model": {
    "name": "eidos",
    "version": "1.0"
  }
}
```

### 3.3 Eidos: Speaker Verification
- **URL**: `POST https://platform.detectif.ai/v1/speakers/verify`
- **Headers**:
  - `Authorization`: `Bearer <DETECTIF_API_KEY>`
  - `Idempotency-Key`: `<UUIDv4>`
- **Body**: `multipart/form-data`
  - `file`: Audio binary (3–60s, min 2s speech).
  - `speaker_id`: Enrolled speaker identifier.
  - `detect_deepfake`: `true` (optional boolean to run both checks in one call).
- **Official Success Response `200 OK`**:
```json
{
  "request_id": "req_c341...",
  "operation_id": "op_d491...",
  "object": "speaker.verification",
  "speaker_id": "trx_spk_emp_018f9e12",
  "result": {
    "decision": "match",
    "similarity": 0.7812,
    "duration_seconds": 6.4
  }
}
```
