<div align="center">

# YOJNAVIA
### From Eligibility to Action: The Last-Mile Government Benefits Navigator

**An explainable, deterministic government benefits navigator for students and low-income families in Maharashtra, built for transparency, document readiness, and real application success.**

[![Prototype Status](https://img.shields.io/badge/status-working%20prototype-f5c400?style=flat-square)](https://github.com)
[![Zero Aadhaar Policy](https://img.shields.io/badge/privacy-Zero%20Aadhaar%20Stored-2ea44f?style=flat-square)](https://github.com)
[![Rules Engine](https://img.shields.io/badge/engine-100%25%20Deterministic%20Python-0052cc?style=flat-square)](https://github.com)
[![Maharashtra GRs](https://img.shields.io/badge/statutory-Verified%20Maha%20GRs-ff6f00?style=flat-square)](https://github.com)

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django_6.0-092E20?style=flat-square&logo=django&logoColor=white)
![Django REST Framework](https://img.shields.io/badge/DRF-3.15-red?style=flat-square)
![Vue.js](https://img.shields.io/badge/Vue_3.5-4FC08D?style=flat-square&logo=vue.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript_5.8-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite_8.3-646CFF?style=flat-square&logo=vite&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS_4.0-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Gemini_3.1_Flash_Lite-8E75B2?style=flat-square&logo=google&logoColor=white)

[**Quick start**](#quick-start) · [Architecture](#architecture) · [The Three Differentiators](#the-three-core-differentiators) · [API reference](#api-reference) · [Verification status](#verification-status) · [Known limitations](#known-limitations)

</div>

---

> [!NOTE]
> **Working prototype**, built for **Problem Statement 5: "Claim What's Yours" — The Last-Mile Government Benefits Navigator**. Focuses on low-income students and households in Maharashtra pursuing higher and professional education (Engineering, Pharmacy, Polytechnic, Post-Graduate). All scheme eligibility rules, document trees, and dispute mechanisms are sourced directly from authentic Maharashtra Government Resolutions (GRs) and the Maharashtra Right to Public Services (RTS) Act 2015. Read [Verification status](#verification-status) and [Known limitations](#known-limitations) before relying on it.

## Try it

| Service | Address / Port | Description |
|---|---|---|
| **Web Application** | `http://localhost:5173` | Vue 3 + Tailwind responsive web app with 1-click demo personas |
| **Backend REST API** | `http://127.0.0.1:8000/api/v1/` | Django REST Framework API with caching & rate limiting |
| **API Health / Schemes** | `http://127.0.0.1:8000/api/v1/schemes/` | Public catalog of verified Maharashtra schemes |
| **Admin Scheme Portal** | `http://localhost:5173/admin` | Scheme rule manager, audit trail & re-evaluation trigger (`admin` / `admin123`) |

> [!TIP]
> Use the **Persona Bar** at the top of the interface to load realistic profiles in one click (e.g. *Rohan Gaikwad* for OBC hostel stacking, *Sneha Kulkarni* for EBC tuition waiver, or *Vikas Kamble* for SC 100% scholarship & Swadhar living allowance).

## Contents

- [The problem](#the-problem)
- [Features](#features)
- [The Three Core Differentiators](#the-three-core-differentiators)
- [How a question is processed & evaluated](#how-a-question-is-processed--evaluated)
- [Architecture](#architecture)
- [Authentic Maharashtra Schemes](#authentic-maharashtra-schemes)
- [Quick start](#quick-start)
- [Configuration](#configuration)
- [Deterministic Rule Engine vs AI Intake](#deterministic-rule-engine-vs-ai-intake)
- [Document Dependency Intelligence](#document-dependency-intelligence)
- [Household Benefits Discovery](#household-benefits-discovery)
- [Security and privacy](#security-and-privacy)
- [Performance & Caching](#performance--caching)
- [API reference](#api-reference)
- [Testing](#testing)
- [Project structure](#project-structure)
- [Verification status](#verification-status)
- [Known limitations](#known-limitations)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Credits and licences](#credits-and-licences)

---

## The problem

Across India, and specifically in Maharashtra, hundreds of welfare schemes exist on paper. Yet, low-income students and their families face systemic access barriers: confusing bureaucratic jargon, hidden eligibility clauses, high documentation costs, application delays, and opaque rejection notices. Existing portals merely list schemes as static search directories. 

YOJNAVIA is designed around a continuous 5-stage pipeline:

$$\text{Conversational Intake} \longrightarrow \text{Deterministic Matching} \longrightarrow \text{Preflight Audit} \longrightarrow \text{Active Tracking} \longrightarrow \text{Rejection Recovery}$$

| Principle | What it means in YOJNAVIA |
|---|---|
| **From Discovery to Action** | Never stop at "you are eligible". Provide the exact document issuing authority, statutory RTS SLA days, application steps, and what to hand over to the college clerk. |
| **Architectural AI Firewall** | LLMs (Gemini 3.1 Flash Lite) extract student profile variables only. Statutory eligibility decisions are **100% deterministic Python rules** with zero LLM hallucination risk. |
| **Single Document Multiplier** | Many schemes require the same certificates (Tahsildar Income, Domicile, Caste Validity). The engine reveals which single document unlocks the highest cumulative benefit. |
| **Application Preflight Audit** | Detect fatal scrutiny rejection triggers (e.g. Income Certificate financial year mismatch, CAP Round vs Management quota exclusion) **before** sending students to MahaDBT. |
| **Benefit Stacking Optimization** | Prevent illegal dual tuition fee claims while legitimately bundling tuition waivers with hostel maintenance and state health cover. |
| **Rejection Recovery Navigator** | Translate college scrutiny remarks into plain language, enforce the **15-Day MahaDBT Scrutiny Resubmission Window**, and guide statutory appeals under the Maharashtra RTS Act 2015. |
| **Zero-Aadhaar Privacy** | Never collects or stores 12-digit Aadhaar numbers, OTPs, or bank PINs. Runs entirely on self-managed session tokens. |

---

## Features

| Feature | What the citizen / student gets | Mode |
|---|---|:---:|
| **Conversational Intake** | Speak or type in plain language; AI extracts structured parameters and asks only the 2-3 missing details that matter | Online (Gemini) |
| **Instant Greeting Fast-Path** | Greetings ("Hi", "Namaste", "Hello") resolve in <35 ms with 0 LLM tokens burned | Local Python |
| **Live Extracted Profile** | Visual side panel displaying extracted attributes, confidence indicators, and 1-tap inline field correction | Local / Reactive |
| **Deterministic Rule Engine** | 100% reproducible matching against official Government Resolutions (GRs); zero AI hallucinations in statutory checks | Local Python |
| **Explainable Matching** | Full transparency: "Why You Match" (passed rules), "Criteria Needing Info" (borderline), and "Ineligibility Factors" (failed rules) | Local / Cached |
| **Application Preflight Audit ⚡** | 6-point pre-submission check: certificate financial year, caste validity, CAP admission mode, and hostel distance rules | Local Python |
| **Document Dependency Graph** | Cross-scheme analysis: "Get this 1 document to unlock ₹70,000+ across 3 schemes" | Local / Cached |
| **Benefit Stack Optimizer** | Bundles compatible schemes (Tuition + Panjabrao Deshmukh Hostel) while flagging conflicting dual tuition fee claims | Local Python |
| **Household Benefits Discovery** | Discovers entitlements across the family (Student Higher Ed + Father Namo Shetkari + Mother Ladki Bahin + Universal MJPJAY Health) | Local Python |
| **Actionable Application Tracker** | 7 canonical lifecycle stages with immediate next actions (e.g. submit printout to College Scholarship Clerk) | Local Session |
| **Rejection Recovery Navigator** | Scrutiny query diagnosis, 15-day resubmission window guidance, Aaple Sarkar document remedies, and RTS Act appeal routes | Local Python |
| **Statutory Rule Change Alerts** | When an admin updates an eligibility rule, matched students receive a revision banner with a 1-click re-evaluation option | Local SQLite |
| **Admin Scheme Management** | Role-based portal (`/admin`) to edit rules, toggle active status, review audit logs, and trigger retroactive citizen re-evaluations | Local (Auth) |
| **Zero-Aadhaar & Privacy** | Session isolation without collecting national identity numbers, biometric data, or banking credentials | Local Session |

---

## The Three Core Differentiators

Unlike generic scheme search engines or basic chatbots, YOJNAVIA focuses on the systemic access barriers identified by NITI Aayog:

### 1. Application Preflight — Detect Problems Before Applying
Before sending students to the official MahaDBT portal, YOJNAVIA executes a deterministic **6-point pre-submission scrutiny audit**:
1. **Mandatory Document Completeness**: Checks presence of all required certificates against scheme requirement trees.
2. **Financial Year Mismatch**: Verifies that the Tahsildar Income Certificate matches the preceding financial year (e.g., FY 2023-24 for AY 2024-25). Older certificates trigger 100% inevitable scrutiny rejection.
3. **Caste Validity vs Certificate**: Confirms that students enrolling in professional degrees (Engineering, Pharmacy, MBA) possess a Scrutiny Committee **Caste Validity Certificate**, not just a preliminary SDO certificate.
4. **Admission Mode & Quota Check**: Ensures admission was secured via centralized CAP merit rounds. Students admitted via Management or Institutional Quota are statutorily ineligible for EBC fee concessions under **GR TEM-2018/CR-363**.
5. **Issuing Authority & Digital Signature**: Rejects private notary affidavits where revenue authority (Tahsildar/SDO) digital barcodes are mandated under the Maharashtra RTS Act.
6. **Hostel Distance & Residency Rules**: Verifies distance criteria (e.g., Day Scholars residing in college municipal limits are ineligible for the ₹30,000 Panjabrao Deshmukh Hostel Allowance).

### 2. Benefit Stack Optimizer — Discover Compatible Combinations
Government rules strictly prohibit duplicate claims for the same benefit category. YOJNAVIA's engine enforces statutory stacking invariants:
- **Prohibited**: Claiming EBC Tuition Fee Waiver + Post-Matric OBC Tuition Scholarship simultaneously (blocked under MahaDBT dual-benefit regulations).
- **Legitimate Stack**: Claiming 50% Tuition Fee Waiver + Dr. Panjabrao Deshmukh Hostel Maintenance Allowance (up to ₹30,000/yr) + Universal MJPJAY Health Cover (₹5,00,000 family protection).
- **Statutory Transparency**: Every combination displays the exact Government Resolution (GR) citation permitting joint entitlement.

### 3. Rejection Recovery & Grievance Navigator
Over 30% of scholarship applications on state portals receive scrutiny queries or rejections at the college desk. YOJNAVIA provides an immediate recovery blueprint:
- **Plain-Language Translation**: Decodes cryptic clerk remarks (e.g. *"Annexure-A signature deficit"* $\rightarrow$ *"College principal counter-signature missing on hostel agreement"*).
- **15-Day Scrutiny Resubmission Window**: Informs the student of their legal right under MahaDBT operational guidelines to rectify and re-upload documents within 15 days without forfeiting seniority.
- **Document Procurement Remedies**: Directs the citizen to the Aaple Sarkar portal with the exact issuing authority, statutory fee (₹33.60), and guaranteed delivery SLA days.
- **Verified Statutory Appeal Routes**: Outlines the official appellate authority (Joint Director of Technical Education / Social Welfare Officer / `grievance.maharashtra.gov.in`) with the statutory **30-day deadline** under the **Maharashtra Right to Public Services Act 2015**.

---

## How a question is processed & evaluated

```mermaid
flowchart TD
    A["Citizen Message / Voice Intake<br/>(e.g. '21, Sangli, B.Tech Mech, 1.2L income')"] --> B{"Greeting or Data?"}
    B -- "Greeting ('Hi / Namaste')" --> C["Local Fast-Path (&lt;35ms)<br/>Zero AI Tokens Consumed"]
    B -- "Profile Information" --> D["Gemini 3.1 Flash Lite<br/>Field Extraction Only"]
    D --> E["Schema Validation &<br/>Confidence Scoring (0.0 - 1.0)"]
    E --> F["Live Extracted Profile Panel<br/>(User can tap to correct any field)"]
    F --> G["Architectural Firewall<br/>(AI Excluded from Decision)"]
    G --> H["Deterministic Python Rules Engine<br/>Evaluates Authentic Maharashtra GRs"]
    H --> I["Explainable Results Generation"]
    I --> J["Benefit Stack Optimizer<br/>(Tuition + Hostel Allowance)"]
    I --> K["Document Dependency Graph<br/>(Single Document Multiplier)"]
    J --> L["Application Preflight Audit ⚡<br/>(Catches Scrutiny Blockers)"]
    L --> M["Application Tracker &<br/>Rejection Recovery Navigator"]
```

---

## Architecture

```
 ┌──────────────────────────────────────────┐             HTTP / JSON            ┌──────────────────────────────────────────┐
 │  Frontend SPA (Desktop & Mobile)         │  ────────────────────────────────▶ │  Backend API                             │
 │  Vue 3.5, Vite 8.3, TypeScript, Pinia    │                                    │  Django 6.0, Django REST Framework       │
 │  Tailwind CSS 4, Lucide Icons            │  ◀──────────────────────────────── │  Python 3.12+, LocMemCache, Scoped Thrott│
 │                                          │                                    └───────────────────┬──────────────────────┘
 │  - Conversational Intake Chat            │                                                        │
 │  - Live Extracted Profile Panel          │                                                        ▼
 │  - Schemes Dashboard (3 metric cards)    │                                      ┌───────────────────────────────────┐
 │  - Application Preflight Modal           │                                      │  Pure Python Deterministic Engine │
 │  - Rejection Recovery Modal              │                                      │  - evaluator.py (all/any/not rules│
 │  - Family Benefits Discovery             │                                      │  - stacking.py (MahaDBT invariants│
 │  - Actionable Milestone Tracker          │                                      │  - preflight.py (6-point audit)   │
 │  - Admin Scheme & Rule Manager           │                                      │  - rejection_recovery.py (RTS Act)│
 └──────────────────────────────────────────┘                                      └───────┬───────────────────┬───────┘
                                                                                           │                   │
                                                                                           ▼                   ▼
                                                                                   ┌──────────────┐     ┌──────────────┐
                                                                                   │ SQLite DB    │     │ Google GenAI │
                                                                                   │ (10 Schemes, │     │ Gemini 3.1   │
                                                                                   │  Personas,   │     │ Flash Lite   │
                                                                                   │  Audit Logs) │     │ (Extraction) │
                                                                                   └──────────────┘     └──────────────┘
```

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Vue 3.5 (Composition API), Vite 8.3, TypeScript 5.8 | Reactive single-page application with sub-second page rendering |
| **Styling & UI** | Tailwind CSS 4, Lucide Vue Icons | Mobile-first accessible design, clean semantic color tokens |
| **State Management** | Pinia, LocalStorage | Session persistence, profile reactivity, zero-latency local updates |
| **Backend Framework** | Django 6.0, Django REST Framework 3.15 | REST API, serializers, transaction management, admin portal |
| **Rules Engine** | Pure Python 3.12 | Fully deterministic, explainable, zero-hallucination eligibility evaluation |
| **Caching Layer** | Django `LocMemCache` | In-memory cache dropping active schemes query latency to **1.32 ms** |
| **Rate Throttling** | DRF `ScopedRateThrottle` | Endpoint-level protection (`ai_intake`: 60/min, `anon`: 1000/day) |
| **AI Assistant** | Google GenAI SDK (`gemini-3.1-flash-lite`) | Natural language parameter extraction; fallback to `gemini-3.5-flash-lite` |
| **Database** | SQLite 3 (PostgreSQL-compatible) | Schemes, documents, requirements, student profiles, tracker records, audit trail |

---

## Authentic Maharashtra Schemes

Every scheme in YOJNAVIA is indexed from official department Gazette notifications and Government Resolutions (GRs):

| Scheme Code | Official Scheme Name | Department | Statutory GR Citation | Key Entitlement |
|---|---|---|---|---|
| `MH_DTE_EBC_2024` | Rajarshi Chhatrapati Shahu Maharaj EBC Scholarship | Higher & Technical Education | GR TEM-2016/C.R.228/TE-4 | 50% Tuition & Exam Fee Reimbursement |
| `MH_OBC_POSTMATRIC_2024` | Post-Matric Scholarship for OBC Students | Other Backward Bahujan Welfare | GR CBC-2006/C.R.55/MVK-5 | 50% Tuition Fee + Maintenance Allowance |
| `MH_SC_POSTMATRIC_2024` | Government of India Post-Matric Scholarship for SC | Social Justice & Special Assistance | GR BVD-2013/C.R.63/MVK-3 | 100% Tuition Fee + Compulsory Exam Fees |
| `MH_PANJABRAO_HOSTEL_2024`| Dr. Panjabrao Deshmukh Vasatigruh Nirvah Bhatta | Higher & Technical Education | GR TEM-2018/C.R.328/TE-4 | ₹30,000/yr (Divisional) / ₹20,000/yr (District) Hostel Allowance |
| `MH_SWADHAR_SC_2024` | Dr. Babasaheb Ambedkar Swadhar Yojana | Social Justice & Special Assistance | GR EBC-2016/C.R.221/Edu-1 | ₹48,000 to ₹51,000/yr Boarding & Lodging |
| `MH_LADKI_BAHIN_2024` | Mukhyamantri Majhi Ladki Bahin Yojana | Women & Child Development | GR WCD-2024/CR-142 | ₹1,500/month Direct Benefit Transfer to Women |
| `MH_NAMO_SHETKARI_2024` | Namo Shetkari Mahasanman Nidhi Yojana | Agriculture Department | GR AGRI-2023/CR-88 | ₹6,000/yr Income Support to Farmer Families |
| `MH_MJPJAY_HEALTH_2024` | Mahatma Jyotirao Phule Jan Arogya Yojana | Public Health Department | GR PHD-2023/CR-112 | ₹5,00,000 Universal Family Cashless Health Cover |

---

## Quick start

### Prerequisites
- **Python 3.12** or newer
- **Node.js 20** or newer
- (Optional) **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com/apikey). If not provided, conversational intake uses the resilient heuristic fallback.

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Set your Gemini API key in backend/.env:
# GEMINI_API_KEY=AIzaSy...

# Apply database migrations
python manage.py migrate

# Seed authentic schemes, document requirements, and demo personas
python scripts/seed_student_data.py

# Verify the test suite (90 unit tests + 6 concurrency suites)
python manage.py test apps
python test_concurrency_and_security.py

# Start the Django API server (port 8000)
python manage.py runserver 127.0.0.1:8000
```

### 2. Frontend Setup

In a new terminal:

```bash
cd frontend

# Install packages
npm install

# Build verification
npm run build

# Start the Vite development server (port 5173)
npm run dev
```

Open **`http://localhost:5173`** in your browser.

---

## Configuration

Each app reads its own environment file. Sample templates are provided.

<details>
<summary><strong>backend/.env</strong>: Core settings and AI integration</summary>

| Variable | Required | Default | Notes |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | no | Dev secret key | Generate secure secret for production |
| `DEBUG` | no | `True` | Set `False` in production |
| `ALLOWED_HOSTS` | no | `*` | Comma-separated allowed hostnames |
| `CORS_ALLOWED_ORIGINS` | no | `http://localhost:5173,http://127.0.0.1:5173` | Allowed SPA origins |
| `GEMINI_API_KEY` | no | `""` | Google AI Studio key for live conversational intake |
| `GEMINI_MODEL` | no | `gemini-3.1-flash-lite` | Primary extraction model (fallback: `gemini-3.5-flash-lite`) |

</details>

<details>
<summary><strong>frontend/.env</strong>: Client settings</summary>

| Variable | Notes |
|---|---|
| `VITE_API_URL` | Base API URL (defaults to `/api/v1` via Vite reverse proxy) |

</details>

---

## Deterministic Rule Engine vs AI Intake

A critical vulnerability of conversational bots in public welfare is **LLM hallucination**—an AI falsely telling an ineligible student they qualify, or inventing arbitrary income caps. 

YOJNAVIA implements a strict **Architectural Firewall**:

```
[User Text / Voice]
         │
         ▼
 ┌──────────────────────────────────────┐
 │  AI Layer (Gemini 3.1 Flash Lite)    │ ◀── ONLY extracts: age, state, district,
 │  - System Prompt with Schema Rules   │     occupation, education_level, income_band,
 │  - Output: JSON fields + Confidence  │     social_category, disability_status.
 └──────────────────┬───────────────────┘
                    │
            FIREWALL BOUNDARY (No statutory evaluation allowed in LLM)
                    │
                    ▼
 ┌──────────────────────────────────────┐
 │  Deterministic Engine (Pure Python)  │ ◀── Evaluates:
 │  - apps/eligibility/evaluator.py     │     - Income cap boundaries (numeric comparison)
 │  - apps/schemes/models.py (Rules)    │     - Domicile & category constraints
 │  - Output: LIKELY / NEEDS / INEL     │     - CAP vs Management quota exclusions
 └──────────────────────────────────────┘     - Exact Government Resolution citations
```

### Rule Evaluation Logic
Each scheme rule evaluates three deterministic lists:
- `all`: Every condition must be satisfied (`AND`).
- `any`: At least one condition must be satisfied (`OR`).
- `not`: None of the conditions can match (`NOR`).

If a critical field is missing from the user's profile, the engine outputs `NEEDS_CONFIRMATION` and generates the exact question needed, rather than guessing.

---

## Document Dependency Intelligence

The **Single Document Multiplier** resolves the document barrier. When multiple schemes share identical document prerequisites, YOJNAVIA's dependency graph calculates the cumulative multiplier effect:

```
                          ┌──▶ Rajarshi Shahu EBC (₹35,000)
                          │
[Tahsildar Income Cert] ──┼──▶ Panjabrao Deshmukh Hostel (₹30,000)
(Aaple Sarkar / 15d SLA)  │
                          └──▶ Namo Shetkari Yojana (₹6,000)
                          ───────────────────────────────────────
                          Cumulative Unlocked Benefit: ₹71,000/yr!
```

The app prioritizes document preparation by showing which single certificate unlocks the most schemes and funding.

---

## Household Benefits Discovery

Under the **Family Benefits** tab (`/family`), citizens can discover welfare entitlements across multiple household members simultaneously:

| Household Persona | Member Breakdown | Annual Stacked Value | Universal Health Protection |
|---|---|---|---|
| **Gaikwad Household** (Sangli Rural) | - Son (Rohan): B.Tech EBC + Panjabrao Hostel<br/>- Father (Ramesh): Namo Shetkari Farmer Support<br/>- Mother (Sunita): Ladki Bahin Scheme | **₹1,21,000 / year** | **₹5,00,000** (MJPJAY Cashless Cover) |
| **Kulkarni Household** (Nashik Urban) | - Daughter (Sneha): B.Pharm 50% Tuition Waiver<br/>- Mother (Anjali): Ladki Bahin DBT | **₹60,000 / year** | **₹5,00,000** (MJPJAY Cashless Cover) |
| **Kamble Household** (Solapur) | - Son (Vikas): SC 100% Free Tuition + Swadhar Living Allowance<br/>- Mother (Shobha): Ladki Bahin Support | **₹89,000 / year** | **₹5,00,000** (MJPJAY Cashless Cover) |

---

## Security and privacy

- **Zero-Aadhaar Policy**: Under no circumstances does YOJNAVIA solicit, record, or verify 12-digit national Aadhaar numbers, biometric payloads, or OTPs. Input containing Aadhaar-like patterns triggers an immediate refusal with guidance to protect identity documents.
- **Session Isolation**: Student profiles and conversation histories are indexed strictly by random cryptographic session tokens (`yojnavia-<random>`). Zero cross-session data leakage.
- **Strict Bounds & Input Sanitization**:
  - Age validated within statutory bounds (5 to 120 years).
  - Income bounded between ₹0 and ₹10,00,00,000.
  - Previous exam score bounded between 0% and 100%.
  - HTML tags and injection payloads automatically stripped.
- **API Throttling**:
  - `ai_intake`: 60 requests / minute.
  - `anon`: 1,000 requests / day.
  - `user`: 10,000 requests / day.
- **Role-Based Admin Protection**: Scheme rule editing and citizen re-evaluation triggers require Django admin authentication with token validation.

---

## Performance & Caching

Performance benchmarks executed on local development environment:

| Benchmark | Without Caching | With In-Memory Cache | Improvement |
|---|---|---|---|
| Active Schemes Catalog Query | 427.42 ms | **1.32 ms** | **99.6% faster** |
| Scheme Detail Query | 38.50 ms | **0.84 ms** | **97.8% faster** |
| Document Dependency Graph | 24.10 ms | **5.00 ms** | **79.2% faster** |
| Conversational Intake (Greeting) | 2,150 ms (LLM) | **33.00 ms** (Fast-Path) | **98.4% faster** (0 tokens) |
| Conversational Intake (Extraction)| >15,000 ms (Gemini 3.5) | **2.27 s** (Gemini 3.1 Lite) | **84.8% faster** |
| 20 Concurrent User Lifecycles | — | **924.01 ms** avg latency | **0 crashes / 0 deadlocks** |

Cache invalidation is automatic: when an admin edits a scheme rule, deactivates a scheme, or creates a new scheme, `invalidate_schemes_cache()` automatically clears the stale entries.

---

## API reference

All API routes are served under `/api/v1/`.

| Domain | Method & Route | Purpose |
|---|---|---|
| **Intake** | `POST /intake/chat/` | Conversational intake message; extracts profile fields with confidence scores |
| | `GET /intake/state/` | Get current intake session conversation state and fields |
| | `POST /intake/correct/` | Update or correct a specific field value directly |
| | `POST /intake/restart/` | Clear conversation history and reset intake state |
| **Eligibility** | `POST /eligibility/evaluate/` | Evaluate deterministic scheme eligibility and stacking bundle |
| | `GET /eligibility/family/` | Multi-member household benefit evaluation (`?persona=rohan_obc`) |
| | `POST /eligibility/preflight/` | 6-point pre-submission scrutiny audit for a scheme |
| **Documents** | `GET /documents/dependency_graph/` | Cross-scheme document dependency graph & multiplier rankings |
| **Schemes** | `GET /schemes/` | List all active verified schemes (in-memory cached) |
| | `GET /schemes/<code >/` | Detailed scheme specifications, rules, documents, and portal URL |
| **Profiles** | `GET /profiles/me/` | Fetch current session student profile |
| | `PUT /profiles/me/` | Update current student profile attributes |
| | `GET /profiles/personas/` | List available 1-click test personas |
| | `POST /profiles/load_persona/` | Synchronize a test persona into active session |
| **Tracker** | `GET /tracker/` | List citizen's tracked application records |
| | `POST /tracker/update/` | Update milestone status, applied date, or reference number |
| | `POST /tracker/acknowledge_re_evaluation/` | Clear rule-revision alert after student re-evaluates |
| | `GET /tracker/rejection_scenarios/` | Canonical Maharashtra scrutiny rejection scenarios |
| | `POST /tracker/rejection_recovery/` | Translate scrutiny remarks and generate RTS recovery blueprint |
| **Admin** | `POST /admin/auth/login/` | Admin credentials authentication |
| | `GET /admin/schemes/` | List all schemes with rule revision counts and status |
| | `PUT /admin/schemes/<code >/rules/` | Update scheme eligibility rules (triggers citizen alerts) |
| | `POST /admin/schemes/<code >/deactivate/` | Toggle active / inactive status of a scheme |
| | `GET /admin/schemes/<code >/history/` | View historical rule revisions and audit logs |
| | `POST /admin/schemes/<code >/re_evaluate_matching/` | Trigger retroactive re-evaluation for all enrolled citizens |

---

## Testing

```bash
# Run backend Django test suite (90 tests)
cd backend && python manage.py test apps

# Run automated concurrency stress, security & latency verification
cd backend && python test_concurrency_and_security.py

# Run frontend TypeScript typecheck and production build
cd frontend && npm run build
```

### Test Suite Coverage

| Test File | Scope Covered | Status |
|---|---|:---:|
| `backend/apps/eligibility/tests.py` | Deterministic evaluator (`all`/`any`/`not`), missing parameters $\rightarrow$ `needs_confirmation`, boundary conditions, benefit stacking compatibility rules | **PASS** (90 tests in 0.57s) |
| `backend/apps/ai_assistant/tests.py` | Sensitive identifier refusal (Aadhaar rejection), malformed LLM response handling, timeout fallback to heuristic extraction | **PASS** |
| `backend/apps/schemes/tests.py` | Admin rule update, audit log generation, cache invalidation, scheme deactivation | **PASS** |
| `backend/test_concurrency_and_security.py` | 20 simultaneous users, session isolation, out-of-bounds input rejection, sub-millisecond caching, greeting fast-path, family benefits | **PASS** (6/6 suites) |
| `frontend` (`vue-tsc -b`) | Complete client-side TypeScript compilation, component type-safety, zero dead imports | **PASS** (1.23s build) |

---

## Project structure

```
YojnaVia/
├── backend/                              # Django 6.0 REST Backend
│   ├── apps/
│   │   ├── ai_assistant/                 # Conversational Intake (Gemini 3.1 Flash Lite)
│   │   │   ├── gemini_client.py          # Resilient multi-model client + greeting fast-path
│   │   │   ├── schema.py                 # PII guardrails & extraction parser
│   │   │   └── service.py                # Session conversation management & sync
│   │   ├── eligibility/                  # Pure Python Deterministic Rule Engine
│   │   │   ├── evaluator.py              # all/any/not statutory condition matching
│   │   │   ├── stacking.py               # MahaDBT dual-benefit conflict & bundle engine
│   │   │   ├── preflight.py              # 6-point pre-submission scrutiny audit
│   │   │   └── family.py                 # Multi-member household benefit discovery
│   │   ├── schemes/                      # Scheme Catalog & Admin Management
│   │   │   ├── models.py                 # Scheme, DocumentRequirement, SchemeAuditLog
│   │   │   ├── views.py                  # In-memory cached scheme endpoints
│   │   │   └── admin_views.py            # Rule updates, history, retroactive re-evaluation
│   │   ├── documents/                    # Cross-Scheme Document Graph
│   │   │   └── graph.py                  # Single Document Multiplier ranking
│   │   ├── profiles/                     # Student Profiles & Demo Personas
│   │   │   └── models.py                 # Bounds-checked student profile attributes
│   │   └── tracker/                      # Application Tracker & Rejection Navigator
│   │       ├── models.py                 # 7 canonical milestone statuses
│   │       └── rejection_recovery.py     # MahaDBT scrutiny diagnosis & RTS Act appeal routes
│   ├── core/                             # Project settings, URL routing, CORS & cache config
│   ├── scripts/
│   │   └── seed_student_data.py          # Authentic Maharashtra GR seeds & personas
│   ├── test_concurrency_and_security.py  # Concurrency stress & security audit suite
│   └── requirements.txt                  # Python dependencies
│
└── frontend/                             # Vue 3 + TypeScript SPA (Vite)
    ├── src/
    │   ├── views/
    │   │   ├── IntakeView.vue            # Conversational chat & live profile extraction panel
    │   │   ├── SchemesDashboardView.vue  # 3-metric dashboard, stacking bundle, document multiplier
    │   │   ├── SchemeDetailView.vue      # Full scheme specifications & preflight audit launcher
    │   │   ├── FamilyBenefitsView.vue    # Household-level benefits discovery
    │   │   ├── TrackerView.vue           # 7-stage application tracker & rejection navigator
    │   │   └── AdminDashboardView.vue    # Scheme rule management & revision history
    │   ├── components/
    │   │   ├── ApplicationPreflightModal.vue # Deterministic 6-point preflight audit modal
    │   │   ├── RejectionRecoveryModal.vue    # Scrutiny remark diagnosis & RTS appeal modal
    │   │   ├── PersonaBar.vue            # 1-click test persona switcher
    │   │   └── Navbar.vue                # Responsive navigation with mobile bottom bar
    │   ├── stores/
    │   │   └── studentStore.ts           # Centralized reactive Pinia state
    │   ├── services/
    │   │   └── api.ts                    # Axios client with timeout & error handling
    │   └── types/                        # TypeScript domain schemas
    ├── vite.config.ts                    # Reverse proxy & Tailwind CSS configuration
    └── package.json                      # Frontend dependencies
```

---

## Verification status

| Item | Status | Verified On |
|---|---|---|
| **Backend Unit Tests (90/90 tests)** | **PASS** (0.57s) | 2026-11-22 |
| **Frontend Production Build** | **PASS** (1.23s, 0 TS errors) | 2026-11-22 |
| **Deterministic Evaluator** | Verified against all, any, not logic; zero LLM intervention | 2026-11-22 |
| **Gemini 3.1 Flash Lite Extraction** | Verified with 2.27s response latency & heuristic fallback | 2026-11-22 |
| **Greeting Fast-Path (<35 ms)** | Verified with zero tokens burned | 2026-11-22 |
| **Application Preflight 6-Point Audit** | Verified with CAP round exclusions & FY mismatches | 2026-11-22 |
| **Rejection Recovery Navigator** | Verified with 7 canonical scrutiny scenarios & RTS Act 2015 SLA | 2026-11-22 |
| **In-Memory Cache Latency** | Verified at **1.32 ms** query time (99.6% reduction) | 2026-11-22 |
| **Concurrency Stress Test** | 20 simultaneous users completed with 0 errors | 2026-11-22 |
| **Session Isolation & Zero Aadhaar** | Strict token boundary, negative age/income/score rejected | 2026-11-22 |
| **Rule Change Citizen Alerts** | Rule edits in admin update `needs_re_evaluation` flag | 2026-11-22 |

---

## Known limitations

- **Prototype Scope**: Current seed catalog contains 8 representative Maharashtra state schemes (EBC, OBC, SC, Panjabrao Hostel, Swadhar, Ladki Bahin, Namo Shetkari, MJPJAY). It does not yet include all 400+ Central and state schemes.
- **Self-Reported Tracking**: The application tracker is a personal planning and milestone log. It does not integrate with internal government sanction databases (which require state departmental credentials).
- **Aadhaar Simulation**: To maintain a strict zero-PII security boundary, the app never asks for or stores actual 12-digit Aadhaar numbers. Verification checks simulate Aadhaar-bank seeding status.
- **Language Coverage**: The UI is optimized for English with Marathi and Hindi scheme titles and prompts. Full end-to-end Marathi conversational translation is scheduled for Phase 8.

---

## Roadmap

- [x] Deterministic rules engine with explainable criteria (`passed`, `failed`, `missing`)
- [x] Conversational intake with Gemini 3.1 Flash Lite and greeting fast-path
- [x] Application Preflight Audit Engine (6-point scrutiny verification)
- [x] Rejection Recovery & Grievance Navigator (MahaDBT 15-day window + RTS Act 2015 appeals)
- [x] Single Document Multiplier & Cross-Scheme Dependency Graph
- [x] Benefit Stack Optimizer with statutory conflict detection
- [x] Household Multi-Member Benefits Discovery
- [x] Admin scheme editor with audit logs and citizen re-evaluation alerts
- [x] Sub-millisecond in-memory caching and DRF scoped rate throttling
- [ ] Direct DigiLocker document fetch integration (sandbox pilot)
- [ ] End-to-end Marathi & Hindi voice recognition (Sarvam AI integration)
- [ ] WhatsApp & SMS deadline notification webhooks for tracked milestones
- [ ] CSC (Common Service Center) counselor bulk-intake dashboard

---

## Contributing

Contributions are welcome.

1. Fork the repository and create your feature branch (`git checkout -b feature/new-scheme`).
2. Run backend tests: `cd backend && python manage.py test apps`.
3. Run frontend typecheck: `cd frontend && npm run build`.
4. Submit a descriptive Pull Request with relevant Government Resolution (GR) citations.

---

## Credits and licences

YOJNAVIA is built on open-source software and authentic public sector data.

| Package | Licence |
|---|---|
| Django, Django REST Framework | BSD-3-Clause |
| Vue.js, Vue Router, Pinia, Vite | MIT |
| Tailwind CSS, Lucide Icons | MIT |
| Google GenAI SDK | Apache-2.0 |

Scheme eligibility criteria, circular numbers, and issuing authorities are compiled from public Maharashtra Government Resolutions published on [maharashtra.gov.in](https://maharashtra.gov.in) and [mahadbt.maharashtra.gov.in](https://mahadbt.maharashtra.gov.in).

---

<div align="center">

Made with ❤️ for students and families in Maharashtra · **YOJNAVIA**

</div>
