# Problem Statement

Implement a multimodal GenAI application for Insurance concept visualization. This system integrates LLMs with Image Generation models (via API) to translate textual prompts into both descriptive narratives and high-fidelity visual representations (e.g., Risk Infographic). This workflow demonstrates the synergy between text-to-text and text-to-image models to create comprehensive, multi-dimensional content for educational and professional presentations.

# 🛡️ Insurance Hub — Multimodal GenAI Insurance Management Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-green?style=for-the-badge&logo=flask)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker)
![AWS](https://img.shields.io/badge/AWS-EC2-FF9900?style=for-the-badge&logo=amazonaws)
![Groq](https://img.shields.io/badge/LLM-Groq_Llama_3.3-orange?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Image-Gemini_Flash-4285F4?style=for-the-badge&logo=google)

**A production-grade, cloud-deployed Multimodal GenAI web application for intelligent insurance management.**

[Features](#-features) · [Tech Stack](#-tech-stack) · [Project Structure](#-project-structure) · [Screenshots](#-application-walkthrough) · [Deployment](#-deployment)

</div>

---

## 📌 Overview

**Insurance Hub** is a full-stack web application that combines traditional insurance policy management with cutting-edge Generative AI capabilities. Built with Flask and deployed on AWS EC2 using Kubernetes, the platform enables authenticated users to manage their insurance policies while leveraging AI to understand complex insurance concepts and generate professional visual infographics — all through an intuitive, modern chat-based interface.

The project demonstrates the real-world synergy between **text-to-text** and **text-to-image** AI models in a production environment, addressing genuine user problems in the Indian insurance market.

---

## ✨ Features

### 🔐 User Authentication System
A complete, secure authentication system built from scratch using Flask-Login and Werkzeug password hashing.

- **User Registration** with real-time form validation, password strength indicator, and duplicate email/username detection
- **Secure Login** with session management and persistent login state
- **User Profile Dropdown** in the navbar showing the user's avatar (first letter of username), full name, and email
- **Protected Routes** — every page requires authentication via `@login_required` decorator
- **Ownership Enforcement** — users can only view, edit, or delete their own policies; unauthorized access attempts are blocked with flash messages

---

### 📋 Policy Management — Full CRUD Operations
A complete Create, Read, Update, Delete system for managing insurance policies, with data scoped per user.

**Dashboard (Home Page)**
- Displays all policies belonging to the logged-in user in a clean, sortable table
- Shows policy type, customer name, email, premium amount, and creation date
- Newest policies appear first (ordered by ID descending)
- Empty state with a friendly call-to-action when no policies exist.
- Analytics chart based on user policies.

**Add Policy**
- Clean form card with dropdown for policy type selection (Health / Term / Vehicle)
- Input fields for customer name, email, and premium amount with validation
- Form submission with error handling and database rollback on failure
- Instant redirect to dashboard with success notification on completion

**Edit Policy**
- Pre-populated form with existing policy data for easy modification
- Same validation rules as add policy

**Delete Policy**
- One-click delete with ownership verification

---

## ER diagram

<img width="1226" height="701" alt="Screenshot 2026-04-23 215738" src="https://github.com/user-attachments/assets/c9a80ecb-9ee0-4e55-b0e2-a04451eb6ead" />


---

### 🤖 AI Studio — Multimodal Chat Interface
The flagship feature of Insurance Hub — a real-time, chat-based AI interface with two distinct modes, designed to look and feel like a modern AI assistant.

**Chat UI Design:**
- Left sidebar with mode selector, quick suggestion chips, and policy type selector
- Wide scrollable chat window with message bubbles (user right, AI left)
- Animated typing indicator (3 bouncing dots) while AI processes
- Persistent chat history within the session
- Clear chat button to reset conversation
- Mobile-friendly responsive layout

**Tab 1 — Policy Explainer (Text-to-Text)**
Powered by Groq API with Llama 3.3 70B Versatile — one of the fastest LLMs available.

- User types any insurance question in natural language
- AI responds with a structured explanation including Overview, Key Benefits, Important Warning, and Premium Range — all tailored for the Indian market
- Response appears as a chat bubble with a **Copy to clipboard** button
- Clickable example prompt chips: *"What is cashless hospitalization?"*, *"Explain term insurance for a 28 year old"*, *"What does zero depreciation mean?"*
- Async fetch() call — page never reloads, conversation flows naturally

**Tab 2 — Risk Infographic Generator (Text-to-Image)**
Powered by Gemini Flash Image Generation with multi-provider fallback to FLUX.1-Dev.

- User selects policy type from a pill selector embedded in the input bar
- User types a visual concept in the chat input
- Live progress bar with real-time timer shows generation progress across 4 stages: Sending → Rendering → Encoding → Ready
- Generated image appears as a chat bubble with a **Save Image** button for direct download
- Images returned as base64 data URLs — no external URL expiry issues, no browser security blocks
- Clickable example prompt chips: *"Common health risks in urban India"*, *"Life insurance claim process"*, *"Vehicle accident risk statistics"*

**Async Architecture — No Page Freezes:**
- Two dedicated REST API endpoints: `/api/explain` and `/api/generate-image`
- Both called via JavaScript `fetch()` in the background
- UI remains fully interactive during the 10-60 second generation process
- Error messages appear inline in the chat if any service fails

---

### 🎨 Design System
A fully custom design system built with vanilla CSS and CSS variables — no UI framework used.

- **Color palette:** Warm off-white background (`#f7f8f4`), Navy (`#1b2a4a`), Sage green (`#6aaa78`), Pure white cards
- **Typography:** Playfair Display (headings, serif, professional) + DM Sans (body, clean, readable)
- **Components:** Glassmorphism navbar, card shadows, animated hover states, pill badges, form cards with icon headers
- **Animations:** `fadeInUp` entry animations on cards, bouncing dot loaders, shimmer skeleton screens, smooth tab transitions
- **Icons:** Font Awesome 6 throughout — consistent iconography for every action and category
- **Flash messages:** Color-coded notifications (green for success, red for danger, yellow for warning) with icons

---

### 🔌 RESTful Async API Endpoints
Two JSON API endpoints consumed by the frontend JavaScript:

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/api/explain` | POST | Required | Returns AI policy explanation as JSON |
| `/api/generate-image` | POST | Required | Returns base64 image as JSON |
| `/add-policy` | GET/POST | Required | Create new policy |
| `/edit/<id>` | GET/POST | Required | Update existing policy |
| `/delete/<id>` | POST | Required | Delete policy |
| `/health-policy` | GET | Required | Health insurance info page |
| `/term-policy` | GET | Required | Term insurance info page |
| `/vehicle-policy` | GET | Required | Vehicle insurance info page |
| `/ai-studio` | GET/POST | Required | AI Studio chat interface |
| `/register` | GET/POST | Public | User registration |
| `/login` | GET/POST | Public | User login |
| `/logout` | GET | Required | Logout and session clear |

---

## 🛠️ Tech Stack

| Category | Technology | Purpose |
|---|---|---|
| **Backend** | Python 3.11, Flask 3.0 | Web framework and routing |
| **Database** | SQLite + SQLAlchemy ORM | Data persistence with relationships |
| **Authentication** | Flask-Login, Werkzeug | Session management, password hashing |
| **LLM** | Groq API — Llama 3.3 70B | Ultra-fast text generation (~1-2s) |
| **Image Gen** | Gemini Flash Image API | Text-to-image generation |
| **Image Fallback** | Hugging Face FLUX.1-Dev | Same model as Raphael AI |
| **Frontend** | Jinja2, Vanilla CSS, Vanilla JS | Templating, styling, async calls |
| **Icons** | Font Awesome 6 | UI iconography |
| **Fonts** | Google Fonts (Playfair + DM Sans) | Typography |
| **Containerization** | Docker, Docker Hub | Image packaging and registry |
| **Orchestration** | Kubernetes (kubeadm) | Container orchestration |
| **Cloud** | AWS EC2 (Ubuntu 24) | Production hosting |
| **Networking** | Flannel CNI, NodePort | Kubernetes pod networking |
| **WSGI** | Gunicorn | Production Python server |

---

## 🗂️ Project Structure

```
Insurance_app/
├── app/
│   ├── __init__.py          # App factory — extensions, blueprints, DB init
│   ├── models.py            # SQLAlchemy models (User, Policy)
│   ├── routes.py            # Main blueprint — all routes + API endpoints
│   ├── auth.py              # Auth blueprint — register, login, logout
│   ├── ai.py                # GenAI module — LLM + image generation logic
│   ├── static/
│   │   ├── css/style.css    # Complete custom design system (1200+ lines)
│   │   └── js/script.js     # Frontend interactions and helpers
│   └── templates/
│       ├── base.html        # Base layout — navbar, footer, flash messages
│       ├── index.html       # Dashboard — policy table with CRUD actions
│       ├── add_policy.html  # Add policy form card
│       ├── edit_policy.html # Pre-populated edit form
│       ├── health.html      # Health insurance — 4 interactive info cards
│       ├── term.html        # Term insurance — 4 interactive info cards
│       ├── vehicle.html     # Vehicle insurance — 4 interactive info cards
│       ├── ai_studio.html   # AI Studio — full chat interface with sidebar
│       ├── login.html       # Login page with password toggle
│       └── register.html    # Registration with strength meter
├── k8s/
│   ├── deployment.yaml      # Kubernetes deployment (2 replicas)
│   └── service.yaml         # NodePort service on port 30007
├── Dockerfile               # Multi-stage container build
├── requirements.txt         # Python dependencies
└── run.py                   # App entry point
```

---

## 🗃️ Database Schema

### User Table
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | Integer | Primary Key | Auto-increment unique ID |
| username | String(100) | Unique, Not Null | Display name |
| email | String(150) | Unique, Not Null | Login email |
| password_hash | String(256) | Not Null | Werkzeug hashed password |
| created_at | DateTime | Default: now | Account creation timestamp |

### Policy Table
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | Integer | Primary Key | Auto-increment unique ID |
| policy_type | String(100) | Not Null | Health / Term / Vehicle |
| customer_name | String(150) | Not Null | Policy holder name |
| email | String(150) | Not Null | Contact email |
| premium_amount | Float | Not Null | Annual premium in INR |
| created_at | DateTime | Default: now | Policy creation timestamp |
| user_id | Integer | FK → User.id | Owner reference |

---



---

## 🚀 Deployment

### Local Development
```bash
# Clone and setup
git clone https://github.com/ChandreshBhati/Insurance-App-D12-G2.git
cd Insurance-App-D12-G2

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run
python run.py
# Visit: http://localhost:5000
```

### Docker
```bash
# Build image
docker build -t insurance-hub:v1 .

# Run container
docker run -p 5000:5000 insurance-hub:v1
```

### Kubernetes on AWS EC2
```bash
# Initialize cluster
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml
kubectl taint nodes --all node-role.kubernetes.io/control-plane-

# Deploy application
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Access at:
http://<EC2_PUBLIC_IP>:30007
```

---

## 🔒 Security Features

- Passwords never stored in plain text — Werkzeug `generate_password_hash` with PBKDF2-SHA256
- All routes protected with `@login_required` — unauthenticated users redirected to login
- Policy ownership enforced on every edit/delete — cross-user data access impossible
- Flask `SECRET_KEY` for secure session cookies
- Database rollback on every failed transaction — no partial/corrupt writes
- Flash message feedback on all unauthorized access attempts

---

## 📦 Dependencies

```
flask                 # Web framework
flask-sqlalchemy      # ORM + database management
flask-login           # User session management
werkzeug              # Password hashing utilities
gunicorn              # Production WSGI server
python-dotenv         # Environment variable management
groq                  # Groq LLM API client
huggingface_hub       # Hugging Face inference SDK
Pillow                # Image processing (PIL)
requests              # HTTP client for API calls
google-generativeai   # Gemini image generation
```

---

## Future scope 

**Target** :- Design and implement an architecture of collaborative Insurance agents featuring specialization and hand-off protocols. The system consists of a Researcher Agent dedicated to sourcing information (e.g., Policy Coverage) and a Writer Agent tasked with synthesizing and formatting the data. This project demonstrates advanced inter-agent communication, state management, and the orchestration of complex workflows to achieve high-quality, structured outputs. RAG based integration for more precise outputs catering to indian customers and market.

---

## 👨‍💻 Author

**Chandresh Bhati**
GitHub: [@ChandreshBhati](https://github.com/ChandreshBhati)
Repository: [Insurance-App-D12-G2](https://github.com/ChandreshBhati/Insurance-App-D12-G2)

---

## 📄 License

This project is developed for educational purposes as part of a GenAI Cloud Deployment course — Batch D12, Group 2.

---

<div align="center">
Built with ❤️ using Flask, Groq, Gemini, Docker & Kubernetes
</div>
