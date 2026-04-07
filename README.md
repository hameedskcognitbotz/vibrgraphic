# AI Infographic Generator Backend

A fully functional, asynchronous, and scalable backend for generating AI-powered infographics. Built with **FastAPI**, **Celery**, **Redis**, and **PostgreSQL**.

## 🏗️ Architecture Overview

The backend uses a standard service-oriented architecture designed to handle long-running generation jobs asynchronously.

- **FastAPI**: The core web framework acting as the API gateway.
- **PostgreSQL**: Stores robust relational data (Users and generation Jobs). 
- **Redis**: Acts as the high-speed message broker for queuing background jobs.
- **Celery**: The asynchronous task queue runner that executes the actual LLM extraction and image generation steps.
- **Pillow (PIL)**: Used by our `rendering_engine` to programmatically draw and export PNG infographics.

---

## 📂 Project Structure

```
ai backend/
│
├── app/
│   ├── api/          # API Routers (v1) and Dependencies
│   │   ├── deps.py   # JWT user validation
│   │   └── v1/endpoints/ # auth.py, generate.py
│   ├── core/         # Settings, Database Config, and Security (JWT/Argon2)
│   ├── models/       # SQLAlchemy Database Models (User, Job)
│   ├── schemas/      # Pydantic Schemas for Validation
│   ├── services/     # Core Business Logic (AI Service, Render Engine, Export S3)
│   ├── worker/       # Celery configuration and Tasks
│   └── main.py       # FastAPI Entry Point (Uvicorn starts here)
│
├── media/            # Locally generated output images
├── docker-compose.yml# Spins up Redis and Postgres containers
├── init_db.py        # Script to initialize SQLAlchemy tables
└── requirements.txt  # Python package dependencies
```

---

## 🛠️ Step-by-Step Setup Guide

### 1. Prerequisites
Ensure you have the following installed on your machine:
- **Python 3.9+**
- **Docker Desktop** (To run PostgreSQL and Redis containers)

### 2. Environment Setup
Open a terminal in the root folder (`c:\Users\aslam\OneDrive\Desktop\ai backend`) and install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Start Database & Message Broker
We use Docker to quickly spin up instances of PostgreSQL and Redis:

```bash
docker compose up -d
```
> Wait a few seconds for the containers to fully start before proceeding.

### 4. Initialize Database Tables
Run the database initialization script to create the `users` and `jobs` tables:

```bash
python init_db.py
```

### 5. Start the API Server
Start the Uvicorn web server in your terminal:

```bash
uvicorn app.main:app --reload
```
The server will now be live at `http://localhost:8000/`. You can navigate here to see the beautiful frontend dashboard showing your latest creations!

### 6. Start the Celery Worker
In a **separate** terminal window (while the Uvicorn server is running), start the background worker:

```bash
# We use the threads pool on Windows to ensure maximum asyncio compatibility
celery -A app.worker.celery_app worker -Q main-queue,celery -l info -P threads
```

---

## 📖 API Documentation & Usage

FastAPI automatically generates comprehensive documentation.
**Head to:** [http://localhost:8000/docs](http://localhost:8000/docs)

### Core Endpoints

#### User Authentication
- `POST /api/v1/auth/register` - Create a new user account with an email and password.
- `POST /api/v1/auth/login` - Authenticate and receive your JWT access token.

#### Core Functionality (Requires JWT Token)
*Use the "Authorize" button in the Swagger UI (`/docs`) to input your token before calling these.*

- `POST /api/v1/infographics/generate` - Pass a `{"topic": "Your Topic"}` payload. Returns an ID and places the job in the pending background queue.
- `GET /api/v1/infographics/status/{job_id}` - Poll this endpoint to check if the background task is `pending`, `processing`, or `completed`.
- `GET /api/v1/infographics/download/{job_id}` - Once completed, this returns the URL string pointing to your newly created graphic.

### Viewing your outputs
All locally generated infographics are saved automatically to the `media/infographics/` directory.

You can preview the most recently generated infographic right on the main homepage dashboard: [http://localhost:8000/](http://localhost:8000/) !