# 🛡️ Insurance Hub — Multimodal GenAI Insurance Management App

> A full-stack Flask web application for insurance policy management, enhanced with a **Multimodal GenAI AI Studio** that integrates LLM-powered policy explanations and AI-generated risk infographics.

---

## 📌 Project Overview

**Insurance Hub** is a cloud-deployed insurance management platform built with Flask. It allows authenticated users to manage their insurance policies (Health, Term, Vehicle) and leverages **Generative AI** to explain insurance concepts and generate professional visual infographics — demonstrating the synergy between **text-to-text** and **text-to-image** AI models.

This project fulfills the **Multimodal GenAI Insurance Creator** specification:

| Requirement | Implementation |
|---|---|
| GenAI Application | AI Studio feature with LLM + Image Generation |
| LLM API | Groq API — Llama 3.3 70B Versatile |
| Image Generation | Hugging Face InferenceClient — FLUX.1-dev |
| Text-to-Text | Policy Explainer — structured insurance explanations |
| Text-to-Image | Risk Infographic Generator — professional visuals |
| Educational/Professional | Structured output for presentations and learning |

---

## ✨ Features

### Core Application
- **User Authentication** — Register, login, logout with Flask-Login and Werkzeug password hashing
- **Policy Management (CRUD)** — Create, read, update, delete insurance policies
- **User Isolation** — Each user sees only their own policies with ownership enforcement
- **Policy Types** — Health Insurance, Term Insurance, Vehicle Insurance
- **Responsive UI** — Clean light theme with Playfair Display + DM Sans fonts

### 🤖 AI Studio (GenAI Features)
- **Policy Explainer (Text-to-Text)**
  - Powered by Groq API with Llama 3.3 70B Versatile
  - Structured output: Overview, Key Benefits, Important Info, Premium Range
  - Tailored for Indian insurance market
  - Clickable example prompt chips
  - One-click copy to clipboard

- **Risk Infographic Generator (Text-to-Image)**
  - Powered by Hugging Face FLUX.1-dev model
  - Generates professional insurance infographics from text prompts
  - Base64 embedded — no external URL issues or browser blocks
  - Animated skeleton loader while generating
  - Right-click to save generated image

### UX Features
- Animated loading dots while AI generates responses
- Tab-based interface (Explainer / Infographic)
- Flash messages for all user actions
- User avatar dropdown with username initial
- Auth-aware navbar

---

## 🗂️ Project Structure

```
INSURANCE_APP/
├── app/
│   ├── __init__.py          # Flask app factory, extensions, blueprints
│   ├── models.py            # User + Policy SQLAlchemy models
│   ├── routes.py            # Main blueprint — CRUD + AI Studio routes
│   ├── auth.py              # Auth blueprint — register/login/logout
│   ├── ai.py                # GenAI logic — Groq LLM + HF image generation
│   ├── static/
│   │   ├── css/style.css    # Full design system
│   │   └── js/script.js     # Frontend interactions
│   └── templates/
│       ├── base.html        # Base layout with navbar
│       ├── index.html       # Dashboard with policy table
│       ├── add_policy.html  # Add policy form
│       ├── edit_policy.html # Edit policy form
│       ├── health.html      # Health insurance info page
│       ├── term.html        # Term insurance info page
│       ├── vehicle.html     # Vehicle insurance info page
│       ├── ai_studio.html   # AI Studio — GenAI interface
│       ├── login.html       # Login page
│       └── register.html    # Register page
├── .env                     # Environment variables (never commit)
├── .env.example             # Template for .env
├── requirements.txt         # Python dependencies
└── run.py                   # App entry point
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask, Flask-SQLAlchemy, Flask-Login |
| Database | SQLite (dev) — easily switchable to PostgreSQL |
| ORM | SQLAlchemy |
| Auth | Flask-Login + Werkzeug password hashing |
| LLM API | Groq API — `llama-3.3-70b-versatile` |
| Image Generation | Hugging Face InferenceClient — `FLUX.1-dev` |
| Frontend | Jinja2, Vanilla CSS, Font Awesome 6 |
| Fonts | Playfair Display + DM Sans (Google Fonts) |
| Deployment | Docker, AWS EC2, Kubernetes (kubeadm) |
| Container Registry | Docker Hub |

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9+
- pip
- A free [Groq API key](https://console.groq.com)
- A free [Hugging Face token](https://huggingface.co/settings/tokens)

### 1. Clone the Repository

```bash
git clone https://github.com/ChandreshBhati/Insurance-App-D12-G2.git
cd Insurance-App-D12-G2
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
pip install groq huggingface_hub Pillow python-dotenv
```

### 3. Create `.env` File

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys:

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxx
SECRET_KEY=your-random-secret-key-here
```

#### Getting API Keys

**Groq API Key (Free)**
```
1. Go to: https://console.groq.com
2. Sign up → API Keys → Create Key
3. Copy key starting with gsk_...
```

**Hugging Face Token (Free)**
```
1. Go to: https://huggingface.co/settings/tokens
2. Sign up → New Token → Type: Read
3. Copy token starting with hf_...
```

### 4. Run the App

```bash
python run.py
```

Visit: **http://localhost:5000**

---

## 🤖 AI Studio — How It Works

### Text-to-Text Pipeline

```
User types question
        ↓
routes.py → ai_studio() route
        ↓
ai.py → generate_policy_explanation()
        ↓
Groq API (Llama 3.3 70B)
  + System prompt with Indian insurance context
        ↓
Structured response returned
  📋 Overview | ✅ Benefits | ⚠️ Warning | 💰 Premium Range
        ↓
Displayed in AI output card
```

### Text-to-Image Pipeline

```
User types visual concept
        ↓
routes.py → ai_studio() route
        ↓
ai.py → generate_risk_infographic()
        ↓
Hugging Face InferenceClient
  → FLUX.1-dev model
  → Returns PIL Image object
        ↓
Converted to base64 data URL
        ↓
Embedded directly in <img> tag
  (no external URL, no browser blocks)
```

---

## 🗃️ Database Schema

### User Table
| Column | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| username | String(100) | Unique username |
| email | String(150) | Unique email |
| password_hash | String(256) | Hashed password |
| created_at | DateTime | Account creation time |

### Policy Table
| Column | Type | Description |
|---|---|---|
| id | Integer | Primary key |
| policy_type | String(100) | Health / Term / Vehicle |
| customer_name | String(150) | Policy holder name |
| email | String(150) | Contact email |
| premium_amount | Float | Annual premium in INR |
| created_at | DateTime | Policy creation time |
| user_id | Integer | FK → User.id |


---

## 📋 API Keys Summary

| Service | Purpose | Free Tier | Link |
|---|---|---|---|
| Groq | LLM text generation | ✅ Yes — generous limits | [console.groq.com](https://console.groq.com) |
| Hugging Face | Image generation | ✅ Yes — free token | [huggingface.co](https://huggingface.co/settings/tokens) |



---

## 📦 Dependencies

```
flask
flask-sqlalchemy
flask-login
werkzeug
gunicorn
groq
huggingface_hub
Pillow
python-dotenv
requests
```


---

## 👨‍💻 Author

**Chandresh Bhati**
GitHub: [ChandreshBhati/Insurance-App-D12-G2](https://github.com/ChandreshBhati/Insurance-App-D12-G2)

---

## 📄 License

This project is developed for educational purposes as part of a GenAI cloud deployment course.

