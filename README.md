# 🔳 QR Code Generator

A full-stack **QR Code Generator** web application built as a college mini-project using **FastAPI** (backend) and **Streamlit** (frontend). Supports multiple QR code types with live preview, custom styling, and one-click downloads.

---

## 🚀 Live Demo

| Service  | URL |
|----------|-----|
| 🌐 Frontend (Streamlit) | [qr-generator-web.streamlit.app](https://qr-generator-web.streamlit.app/) |
| ⚙️ Backend API (FastAPI) | [qr-code-backend.up.railway.app](https://qr-code-backend.up.railway.app) |
| 📚 API Docs (Swagger UI) | [qr-code-backend.up.railway.app/docs](https://qr-code-backend.up.railway.app/docs) |

---

## ✨ Features

- 🔗 **Multiple QR Types** — URL, Plain Text, Email, Phone, Wi-Fi, vCard (Contact)
- 🎨 **Custom Styling** — Foreground & background color pickers, transparent background support
- 📐 **Size Control** — Adjustable QR code size with slider
- 🖼️ **Format Options** — Export as PNG, JPG, or JPEG
- 👁️ **Live Preview** — Instant QR code preview after generation
- ⬇️ **One-Click Download** — Download the generated QR code directly from the UI
- 🌗 **Dark / Light Theme** — Switchable themes with a polished glassmorphism UI
- 🧪 **Test Coverage** — Automated tests using Pytest

---

## 🛠️ Tech Stack

| Layer     | Technology            |
|-----------|-----------------------|
| Frontend  | Streamlit             |
| Backend   | FastAPI (Python)      |
| Validation| Pydantic              |
| QR Engine | `qrcode` library      |
| Image     | Pillow (PIL)          |
| Testing   | Pytest + pytest-cov   |
| Deploy FE | Streamlit Community Cloud |
| Deploy BE | Railway               |

---

## 📂 Project Structure

```
Qr-Code-Generator/
├── backend/
│   ├── app/
│   │   ├── api/          # API route handlers (v1)
│   │   ├── core/         # Config, logger, settings
│   │   ├── schemas/      # Pydantic request/response models
│   │   ├── services/     # QR code generation logic
│   │   ├── utils/        # Helper utilities
│   │   └── main.py       # FastAPI app entry point
│   └── tests/            # Pytest test suite
├── frontend/
│   ├── components/       # Streamlit UI components (sidebar, header, forms, preview)
│   ├── services/         # Config loader, API client
│   ├── utils/            # Frontend utilities
│   └── app.py            # Streamlit app entry point
├── configs/
│   ├── app.yaml          # Application configuration
│   └── themes.yaml       # UI theme definitions
├── requirements.txt      # Python dependencies
├── Procfile              # Railway deployment config (backend)
└── README.md
```

---

## 🏃 Running Locally

### Prerequisites

- Python 3.10+
- Git

### 1. Clone the repository

```bash
git clone https://github.com/ashrma0502/Qr-Code-Generator.git
cd Qr-Code-Generator
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Backend (FastAPI)

```bash
# From the project root
python -m uvicorn app.main:app --reload --app-dir backend
```

The API will be available at: `http://localhost:8000`  
Swagger docs at: `http://localhost:8000/docs`

### 5. Run the Frontend (Streamlit)

Open a second terminal (with venv activated):

```bash
python -m streamlit run frontend/app.py
```

The app will open in your browser at: `http://localhost:8501`

> **Note:** The frontend automatically connects to `http://localhost:8000` when no `BACKEND_URL` environment variable is set.

### 6. Run Tests

```bash
PYTHONPATH=backend python -m pytest
```

---

## ⚙️ Environment Variables

| Variable      | Description                           | Default                   |
|---------------|---------------------------------------|---------------------------|
| `BACKEND_URL` | URL of the FastAPI backend            | `http://localhost:8000`   |
| `PORT`        | Port for the backend server (Railway) | `8000`                    |

For Streamlit Cloud, set `BACKEND_URL` in the **Secrets** section of your app settings:

```toml
# .streamlit/secrets.toml
BACKEND_URL = "https://qr-code-backend.up.railway.app"
```

---

## 🌐 Deployment

### Backend → Railway

The backend is deployed on [Railway](https://railway.app) using the `Procfile` at the project root:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT --app-dir backend
```

### Frontend → Streamlit Community Cloud

The frontend is deployed on [Streamlit Community Cloud](https://streamlit.io/cloud):

- **Repository:** `ashrma0502/Qr-Code-Generator`
- **Main file path:** `frontend/app.py`
- **Secret:** `BACKEND_URL = https://qr-code-backend.up.railway.app`

---

## 📡 API Endpoints

| Method | Endpoint              | Description            |
|--------|-----------------------|------------------------|
| GET    | `/`                   | API info               |
| GET    | `/health`             | Health check           |
| POST   | `/api/v1/qr/generate` | Generate a QR code     |
| GET    | `/docs`               | Swagger UI (API docs)  |
| GET    | `/redoc`              | ReDoc (API docs)       |

---

## 🧑‍💻 Author

Built as a **College Mini Project** using FastAPI & Streamlit.

---

## 📄 License

This project is for educational purposes.
