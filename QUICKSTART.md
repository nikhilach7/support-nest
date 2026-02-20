# ⚡ Quick Start Guide

## 1️⃣ Setup (2 minutes)

### Get Your Gemini API Key
1. Go to https://aistudio.google.com/app/apikey
2. Sign in or create account
3. Go to API Keys section
4. Create new secret key
5. Copy the key (starts with `sk-...`)

### Configure Environment
```bash
# Copy example env file
copy .env.example .env

# Edit .env file and add your key:
GEMINI_API_KEY=your-gemini-api-key-here
```

## 2️⃣ Run (1 command)

```bash
docker-compose up --build
```

**Wait for:**
- ✅ PostgreSQL ready
- ✅ Migrations applied
- ✅ Django server started on 8000
- ✅ React dev server started on 3000

## 3️⃣ Use (3 URLs)

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000/api/
- **Admin:** http://localhost:8000/admin/

## 🎯 Test It Out

### In the Browser (Frontend)

1. Go to http://localhost:3000
2. Click "Submit Ticket"
3. Type a description: "I was charged twice for my subscription"
4. Watch AI auto-fill category (billing) and priority (high)
5. Submit the ticket
6. See it appear in "All Tickets"
7. Click "Statistics" to see metrics

### With curl (Backend API)

```bash
# Create a ticket
curl -X POST http://localhost:8000/api/tickets/ -H "Content-Type: application/json" -d "{\"title\":\"Test\",\"description\":\"Test ticket\",\"category\":\"general\",\"priority\":\"low\"}"

# Get all tickets
curl http://localhost:8000/api/tickets/

# Get statistics
curl http://localhost:8000/api/tickets/stats/

# Test AI classification
curl -X POST http://localhost:8000/api/tickets/classify/ -H "Content-Type: application/json" -d "{\"description\":\"Cannot login to my account\"}"
```

## 🛑 Stop

```bash
# Press Ctrl+C in terminal, then:
docker-compose down
```

## 🔄 Restart

```bash
docker-compose up
```

## 🧹 Clean Reset

```bash
# Remove database and start fresh
docker-compose down -v
docker-compose up --build
```

## ❓ Troubleshooting

### "Port already in use"
```bash
# Windows - Find and kill process
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

### "Cannot connect to Docker"
- Open Docker Desktop
- Wait for it to start
- Try again

### "Gemini API error"
- Check your API key in .env
- Verify your key at https://aistudio.google.com/app/apikey
- System works with fallback (category: general, priority: medium)

### "Frontend won't load"
```bash
docker-compose logs frontend
docker-compose restart frontend
```

## 📖 More Help

- Full docs: [README.md](README.md)
- API reference: [API_REFERENCE.md](API_REFERENCE.md)
- Project structure: [STRUCTURE.md](STRUCTURE.md)
- Complete summary: [SUMMARY.md](SUMMARY.md)

---

**That's it! You're ready to go! 🚀**
