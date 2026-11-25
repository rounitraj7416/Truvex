# TRUVEX Architecture Blueprint
**AI-Powered Universal Trust Infrastructure**  
*Tagline: Verify. Connect. Trust.*  
*Hackathon Track: The Trust Layer (Track 03) — CMRIT × DetectifAI*

---

## 1. Executive Summary & Problem Space

### 1.1 The Vulnerability
Modern enterprise-to-customer communication is suffering a catastrophic collapse of trust. Impersonation fraud, synthetic voice cloning, and caller ID spoofing cost consumers and institutions billions annually:
- **Bank Impersonation**: Attackers clone executive or fraud department voices to authorize urgent wire transfers or demand one-time passcodes (OTPs).
- **Recruitment Scams**: Fraudsters pose as corporate recruiters issuing false offers and extracting identity credentials.
- **Support Impersonation**: Fake technical or customer service agents deceive users into granting remote computer access.

Traditional caller ID and telephony mechanisms authenticate neither the caller's true employer, their authority to conduct the conversation, nor the biological authenticity of their vocal tract.

### 1.2 The TRUVEX Solution
TRUVEX establishes an independent, out-of-band **Trust Infrastructure (B2B2C)**. Before an authorized enterprise representative reaches out to a customer, TRUVEX verifies their corporate standing, employee permissions, voice biometrics, and deepfake signals, generating an ephemeral, single-use **Trust ID**. The customer independently validates this Trust ID on the TRUVEX portal or widget to inspect verifiable cryptographic proof of communication authority.

---

## 2. The Five-Layer Trust Engine

TRUVEX calculates a comprehensive **Trust Index (0–100%)** across five independent verification boundaries:

```mermaid
flowchart TD
    subgraph L1 [Layer 1: Business Verification]
        B1[Company Registered] --> B2[Admin Approved & Active Status]
    end

    subgraph L2 [Layer 2: Employee Verification]
        E1[Active Employee Record] --> E2[Department & Role Match]
    end

    subgraph L3 [Layer 3: Voice Authenticity]
        V1[Audio Sample Capture] --> V2[DetectifAI Aletheia: Deepfake Detection]
        V1 --> V3[DetectifAI Eidos: Speaker Biometrics]
    end

    subgraph L4 [Layer 4: Authority Verification]
        A1[Outbound Calling Permission] --> A2[Time Window & Topic Clearance]
    end

    subgraph L5 [Layer 5: Session Verification]
        S1[Cryptographic Trust ID Generation] --> S2[Customer Challenge-Response Binding]
        S2 --> S3[TTL Expiration & Single-Use Invalidation]
    end

    L1 --> TE[Five-Layer Trust Engine]
    L2 --> TE
    L3 --> TE
    L4 --> TE
    L5 --> TE
    TE --> Score[Composite Trust Index & Risk Verdict]
```

### Layer 1: Business Verification (Weight: 20%)
- Ensures the originating enterprise is vetted and currently in good standing.
- Admin approval gate prevents fraudulent business registrations.
- Fictional business identities are enforced in staging/hackathon environments.

### Layer 2: Employee Identity Verification (Weight: 20%)
- Confirms the employee exists in the active corporate directory.
- Verifies that the employee's status is not suspended, terminated, or under security review.

### Layer 3: Voice Authenticity & Biometrics (Weight: 30%)
- **DetectifAI Aletheia (`/v1/deepfake/detect`)**: Evaluates whether the fresh voice sample shows synthetic artifacts, neural vocoder anomalies, or generative audio signatures. Returns `verdict` (`real` or `fake`) and `score` (0.0 to 1.0).
- **DetectifAI Eidos (`/v1/speakers/verify`)**: Matches the voiceprint against the employee's enrolled voice profile (`speaker_id`), returning `decision` (`match` or `no_match`) and acoustic `similarity` (-1.0 to 1.0).

### Layer 4: Communication Authority Verification (Weight: 15%)
- Assesses whether the employee has explicit administrative authorization to initiate customer contact for the designated topic (e.g., "Account Security Alert", "Loan Verification", "Billing").
- Enforces corporate operating hours and maximum daily session allowances.

### Layer 5: Session & Challenge Verification (Weight: 15%)
- Generates an ephemeral alphanumeric token (`TRX-XXXX-XXXX`) with a 5-to-10-minute validity window.
- When the customer validates the Trust ID, an optional interactive challenge code or verification confirmation establishes mutual session binding.

---

## 3. System Architecture & Components

```text
+-----------------------------------------------------------------------------------+
|                                 CLIENT TIER                                       |
|  +--------------------+   +---------------------+   +--------------------------+  |
|  |   Customer Portal  |   |   Employee Portal   |   |   Admin & Enterprise     |  |
|  | (Trust ID Lookup & |   | (Voice Verification |   |   (Company Onboarding &  |  |
|  |   Fraud Reporting) |   |   & Session Start)  |   |    Policy Management)    |  |
|  +--------------------+   +---------------------+   +--------------------------+  |
+------------------------------------------+----------------------------------------+
                                           | HTTPS / JSON / Multipart
                                           v
+-----------------------------------------------------------------------------------+
|                              FASTAPI BACKEND TIER                                 |
|  +-----------------------------------------------------------------------------+  |
|  | Routes: /api/auth | /api/companies | /api/employees | /api/sessions | ...   |  |
|  +-----------------------------------------------------------------------------+  |
|  | Services:                                                                   |  |
|  |  +---------------------+   +---------------------+   +-------------------+  |  |
|  |  |  aletheia.py        |   |  eidos.py           |   |  trust_engine.py  |  |  |
|  |  | (Deepfake Analysis) |   | (Speaker Match)     |   | (5-Layer Scorer)  |  |  |
|  |  +---------------------+   +---------------------+   +-------------------+  |  |
|  +-----------------------------------------------------------------------------+  |
|  | Database Layer: SQLAlchemy ORM + SQLite (truvex.db)                         |  |
+------------------------------------------+----------------------------------------+
                                           | HTTPS / Authorization: Bearer
                                           v
+-----------------------------------------------------------------------------------+
|                              DETECTIFAI CLOUD API                                 |
|  +-------------------------------------+   +-----------------------------------+  |
|  | Aletheia: /v1/deepfake/detect       |   | Eidos: /v1/speakers/enroll        |  |
|  | (Is this voice real or synthetic?)  |   | Eidos: /v1/speakers/verify        |  |
+-----------------------------------------------------------------------------------+
```

---

## 4. End-to-End Sequence Workflows

### 4.1 Enterprise & Employee Voice Enrollment
```mermaid
sequenceDiagram
    autonumber
    actor Employee
    actor EnterpriseAdmin
    participant Backend as TRUVEX Backend
    participant Detectif as DetectifAI Eidos

    EnterpriseAdmin->>Backend: Register Company & Invite Employee
    Backend-->>EnterpriseAdmin: Company Approved & Employee Created
    Employee->>Backend: Access Voice Enrollment Portal
    Employee->>Backend: Record & Submit Enrollment Clip (15-60s)
    Backend->>Detectif: POST /v1/speakers/enroll (speaker_id=emp_uuid, file)
    Detectif-->>Backend: 200 OK (samples count, speech_seconds)
    Backend-->>Employee: Enrollment Confirmed (Status: ACTIVE)
```

### 4.2 Pre-Call Verification & Trust ID Issuance
```mermaid
sequenceDiagram
    autonumber
    actor Employee
    participant Backend as TRUVEX Backend
    participant Aletheia as DetectifAI Aletheia
    participant Eidos as DetectifAI Eidos

    Employee->>Backend: Select Customer Ref & Call Topic
    Employee->>Backend: Record Fresh Voice Passphrase (4-15s)
    Backend->>Aletheia: POST /v1/deepfake/detect (file)
    Aletheia-->>Backend: verdict: "real", score: 0.04
    Backend->>Eidos: POST /v1/speakers/verify (speaker_id, file)
    Eidos-->>Backend: decision: "match", similarity: 0.82
    Backend->>Backend: Run 5-Layer Trust Algorithm
    Backend->>Backend: Generate Secure Trust ID (TRX-9481-2849, TTL: 10m)
    Backend-->>Employee: Trust ID Issued & Active
```

### 4.3 Customer Independent Verification
```mermaid
sequenceDiagram
    autonumber
    actor Customer
    actor Employee
    participant Backend as TRUVEX Backend

    Employee->>Customer: Initiates Phone Call: "Hello, my TRUVEX Trust ID is TRX-9481-2849"
    Customer->>Backend: Navigates to TRUVEX -> Inputs TRX-9481-2849
    Backend->>Backend: Validate Session & Expiration
    Backend-->>Customer: Display Trust Dashboard:
    Note over Customer,Backend: - Company: Apex Global Bank (Verified)<br/>- Representative: John Doe (Identity Verified)<br/>- Voice Authenticity: 98% (Real Human Voice)<br/>- Biometric Match: 94% (Verified Speaker)<br/>- Stated Reason: Fraud Review
    Customer->>Backend: Optional: Acknowledge & Bind Session
```

---

## 5. Security & Threat Modeling

| Threat Vector | Mitigation in TRUVEX |
| :--- | :--- |
| **Synthetic Voice Impersonation** | DetectifAI Aletheia analyzes micro-acoustic spectral artifacts to catch neural TTS and voice conversion tools. |
| **Replay Attacks** | Employees must speak a dynamic daily phrase or randomized prompt; session recordings are hashed and verified once. |
| **Trust ID Brute-Forcing** | High-entropy random IDs with strict IP rate limiting (5 attempts/min) and short 10-minute TTL. |
| **Compromised Employee Account** | Even if credentials leak, an attacker cannot generate a Trust ID without passing Eidos biometric speaker verification. |
| **Carrier / Telco Blindness** | Independent out-of-band verification decouples authenticity from vulnerable cellular signaling (SS7 / caller ID spoofing). |
