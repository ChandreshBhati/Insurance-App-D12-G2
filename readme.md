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

## 🐳 Docker Deployment

### Build and Push

```bash
# Build image
docker build -t yourusername/insurance-app:v1 .

# Login to Docker Hub
docker login

# Push image
docker push yourusername/insurance-app:v1
```

### Run with Docker

```bash
docker run -d \
  -p 5000:5000 \
  -e GROQ_API_KEY=your_key \
  -e HF_TOKEN=your_token \
  -e SECRET_KEY=your_secret \
  yourusername/insurance-app:v1
```

---

## ☸️ Kubernetes Deployment (AWS EC2)

### Setup kubeadm

```bash
# Install kubelet, kubeadm, kubectl
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | \
  sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] \
  https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /' | \
  sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt update && sudo apt install -y kubelet kubeadm kubectl

# Initialize cluster
sudo swapoff -a
sudo kubeadm init --pod-network-cidr=10.244.0.0/16

# Configure kubectl
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Install Flannel CNI
kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml

# Untaint control plane (single node)
kubectl taint nodes --all node-role.kubernetes.io/control-plane-
```

### Deploy App

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check status
kubectl get pods
kubectl get services
```

Access at: `http://<EC2_PUBLIC_IP>:30007`

---

## 📋 API Keys Summary

| Service | Purpose | Free Tier | Link |
|---|---|---|---|
| Groq | LLM text generation | ✅ Yes — generous limits | [console.groq.com](https://console.groq.com) |
| Hugging Face | Image generation | ✅ Yes — free token | [huggingface.co](https://huggingface.co/settings/tokens) |

---

## 🔒 Security Features

- Passwords hashed with Werkzeug `generate_password_hash`
- All routes protected with `@login_required`
- Policy ownership enforced — users can only edit/delete their own policies
- API keys stored in `.env` — never hardcoded
- `.env` excluded from version control via `.gitignore`

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

## 🚀 Resume Bullets

1. Built a Flask-based multimodal GenAI Insurance Management app integrating Groq Llama 3.3 70B for text-to-text policy explanations and Hugging Face FLUX.1-dev for text-to-image risk infographic generation
2. Implemented complete user authentication with Flask-Login and Werkzeug, including CRUD policy management with ownership-based access control using SQLite + SQLAlchemy ORM
3. Containerized the application with Docker, pushed to Docker Hub, and deployed on AWS EC2 with Kubernetes (kubeadm) using NodePort service on port 30007 with Flannel CNI networking
4. Designed a responsive multi-page UI with AI Studio featuring tab-based interface, animated loading states, base64 image embedding, and one-click copy functionality
5. Debugged real-world AI integration issues including deprecated HF inference endpoints (HTTP 410), Pollinations.ai authentication blocks, and OpenAI quota limits — implementing graceful fallback error handling throughout

---

## 👨‍💻 Author

**Chandresh Bhati**
GitHub: [ChandreshBhati/Insurance-App-D12-G2](https://github.com/ChandreshBhati/Insurance-App-D12-G2)

---

## 📄 License

This project is developed for educational purposes as part of a GenAI cloud deployment course.
