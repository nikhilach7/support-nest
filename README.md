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

## Deploying to Vercel

Use Vercel for the React frontend. Your Django backend can remain on your preferred host (for example a VM, Railway, Render, Fly.io, or any Docker host).

### Step 1 — Push to GitHub

```bash
git push origin main
```

### Step 2 — Import Project in Vercel

1. Go to https://vercel.com and sign in with GitHub.
2. Click **Add New Project**.
3. Select this repository.
4. Set **Root Directory** to `frontend`.
5. Keep framework preset as **Create React App**.

### Step 3 — Configure Frontend Environment Variable

Set this in Vercel project settings:

| Key | Value |
|---|---|
| `REACT_APP_API_URL` | `https://<your-backend-domain>/api` |

### Step 4 — Configure Backend CORS

Add your Vercel frontend URL to backend allowed origins:

| Key | Value |
|---|---|
| `CORS_ALLOWED_ORIGINS` | `https://<your-vercel-app>.vercel.app` |

### Step 5 — Deploy

Trigger deploy from Vercel UI (or by pushing new commits). Vercel will build and host the frontend.

---
