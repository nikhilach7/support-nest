# Support Nest

**Resolve every ticket faster — together.**

A modern, AI-powered support ticket management system built with Django, React, PostgreSQL, and Google Gemini API.

---

## Features

- **AI-Powered Classification** - Gemini automatically suggests category and priority
- **Real-Time Dashboard** - Live queue status with ticket metrics
- **Search & Filter** - Find tickets by category, priority, status, or keyword
- **Beautiful UI** - Dark-mode-first design with responsive layout
- **One-Click Deploy** - Start everything with a single Docker command

---

## Tech Stack

- **Backend:** Django 4.2 + Django REST Framework
- **Frontend:** React 18 with custom CSS
- **Database:** PostgreSQL 15
- **AI:** Google Gemini 1.5 Flash
- **Infra:** Docker & Docker Compose

---

## Prerequisites

- Docker Desktop 
- Google Gemini API key 
- Ports 3000, 8000, 5432 available

---

## Quick Start

### 1. Create `.env` File

```bash
GEMINI_API_KEY=your-api-key-here
```

### 2. Start Everything

```bash
docker-compose up -d
```

### 3. Open Browser

```
http://localhost:3000
```

Done! The app is running. 

---

## Usage

 **Create Ticket** : Submit Ticket → Title & Description → AI suggests category/priority → Create 
**View Tickets** :Tickets tab → Filter by category/priority/status/search 
**Update Ticket** :Click ticket → Change status → Auto-saves 
**View Stats** :Statistics tab → See live metrics & breakdown 

---

## Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Logs
docker-compose logs backend -f
docker-compose logs frontend -f

# Restart
docker-compose restart frontend

# Reset (deletes all data)
docker-compose down -v && docker-compose up -d
```

---

## Endpoints

```
GET  /api/tickets/           - List tickets
POST /api/tickets/           - Create ticket
PATCH /api/tickets/{id}/     - Update ticket
GET  /api/tickets/stats/     - Stats
POST /api/tickets/classify/  - AI classify
```

---

## CI/CD

Every push to `master` or `main` automatically:

1. Runs Django backend tests against a real PostgreSQL service
2. Builds the React frontend to catch compile errors

Powered by GitHub Actions — see [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

---

## Deploying to Render (Free Tier)

This repo includes a [`render.yaml`](render.yaml) for one-click infrastructure setup.

### Step 1 — Push to GitHub

```bash
# First time only
gh auth login
gh repo create support-nest --public --source=. --remote=origin --push
```

Or if the repo already exists:

```bash
git remote add origin https://github.com/<your-username>/support-nest.git
git push -u origin master
```

### Step 2 — Connect to Render

1. Go to [render.com](https://render.com) and sign in with GitHub
2. Click **New → Blueprint** and select your `support-nest` repository
3. Render reads `render.yaml` and creates:
   - PostgreSQL database (`support-nest-db`)
   - Django backend web service (`support-nest-backend`)
   - React frontend static site (`support-nest-frontend`)

### Step 3 — Set Secret Environment Variables

In the Render dashboard, set these two values that are marked `sync: false`:

| Service | Key | Value |
|---|---|---|
| `support-nest-backend` | `GEMINI_API_KEY` | Your Gemini API key |
| `support-nest-frontend` | `REACT_APP_API_URL` | `https://support-nest-backend.onrender.com/api` |
| `support-nest-backend` | `CORS_ALLOWED_ORIGINS` | `https://support-nest-frontend.onrender.com` |

> **Note:** The exact URLs are shown in the Render dashboard after the first deploy.

### Step 4 — Deploy

Click **Deploy** on both services. The backend runs migrations automatically on startup.

---
