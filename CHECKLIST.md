# ✅ Pre-Launch Checklist

## Before Running `docker-compose up --build`

### 1. ✅ Environment Configuration
- [ ] `.env` file exists in root directory
- [ ] `GEMINI_API_KEY` is set (not `your-gemini-api-key-here`)
- [ ] Get API key from: https://aistudio.google.com/app/apikey
- [ ] API key starts with `sk-`

**Edit `.env` file:**
```env
GEMINI_API_KEY=your-gemini-api-key-here
```

### 2. ✅ Docker Desktop
- [ ] Docker Desktop is installed
- [ ] Docker Desktop is running
- [ ] Docker version: `docker --version`
- [ ] Docker Compose version: `docker-compose --version`

### 3. ✅ Ports Available
- [ ] Port 3000 is free (React frontend)
- [ ] Port 8000 is free (Django backend)
- [ ] Port 5432 is free (PostgreSQL)

**Check ports (Windows):**
```powershell
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :5432
```

### 4. ✅ System Requirements
- [ ] 4GB RAM minimum
- [ ] 2GB free disk space
- [ ] Internet connection (for Docker images)

---

## Launch Steps

### Step 1: Navigate to Project
```bash
cd "c:\Users\Akhila\OneDrive\Desktop\sample projects\support ticket"
```

### Step 2: Verify Files Exist
```bash
dir
```

**Expected files:**
- docker-compose.yml ✓
- .env ✓
- backend/ ✓
- frontend/ ✓
- README.md ✓

### Step 3: Build and Start
```bash
docker-compose up --build
```

### Step 4: Wait for Services
Watch for these messages:
- ✅ `PostgreSQL is ready!`
- ✅ `Running migrations...`
- ✅ `Starting Django server...`
- ✅ `webpack compiled successfully`

**First run takes 3-5 minutes**

### Step 5: Verify Access
- [ ] Open http://localhost:3000 (Frontend)
- [ ] Open http://localhost:8000/api/ (Backend)
- [ ] Backend shows DRF browsable API

---

## Post-Launch Verification

### Quick Test 1: Frontend Loads
- [ ] Navigate to http://localhost:3000
- [ ] See "Support Ticket System" header
- [ ] See three tabs: Submit Ticket, All Tickets, Statistics

### Quick Test 2: Submit a Ticket
- [ ] Click "Submit Ticket"
- [ ] Fill in title: "Test Ticket"
- [ ] Fill in description: "I cannot login to my account"
- [ ] Watch for AI to auto-fill category (should be "account")
- [ ] Click Submit
- [ ] See success message
- [ ] Automatically switches to "All Tickets"
- [ ] New ticket appears at top

### Quick Test 3: View Statistics
- [ ] Click "Statistics" tab
- [ ] See total tickets count
- [ ] See open tickets count
- [ ] See priority breakdown
- [ ] See category breakdown

### Quick Test 4: Test Filtering
- [ ] Go to "All Tickets"
- [ ] Use search box to search for "login"
- [ ] Filter by category
- [ ] Filter by priority
- [ ] Filter by status
- [ ] Try combined filters

### Quick Test 5: Backend API
Open in browser or use curl:
- [ ] http://localhost:8000/api/tickets/
- [ ] http://localhost:8000/api/tickets/stats/

---

## Common Issues & Solutions

### Issue: Port Already in Use

**Symptoms:**
- Error: "Port 8000 is already in use"
- Error: "Port 3000 is already in use"

**Solution:**
```powershell
# Find process using port
netstat -ano | findstr :8000

# Kill process (replace <PID> with actual process ID)
taskkill /PID <PID> /F
```

### Issue: Docker Not Running

**Symptoms:**
- Error: "Cannot connect to Docker daemon"
- Error: "Docker is not running"

**Solution:**
1. Open Docker Desktop
2. Wait for it to fully start
3. Try again

### Issue: Database Connection Failed

**Symptoms:**
- Backend logs show "could not connect to server"
- Backend keeps restarting

**Solution:**
```bash
# Check if database is healthy
docker-compose ps

# Restart backend service
docker-compose restart backend
```

### Issue: Gemini API Errors

**Symptoms:**
- Classification returns "general/medium" always
- Backend logs show "Gemini API error"

**Solution:**
1. Check `.env` file has correct API key
2. Verify API key at https://aistudio.google.com/app/apikey
3. Check you have credits/billing enabled
4. System still works with fallback values

### Issue: Frontend Shows Blank Page

**Symptoms:**
- Browser shows blank white page
- No errors in console

**Solution:**
```bash
# Check frontend logs
docker-compose logs frontend

# Common fix: restart frontend
docker-compose restart frontend

# If still not working, rebuild
docker-compose down
docker-compose up --build
```

### Issue: Migrations Not Applied

**Symptoms:**
- Error: "no such table: tickets_ticket"
- Backend shows database errors

**Solution:**
```bash
# Run migrations manually
docker-compose exec backend python manage.py migrate

# Or rebuild from scratch
docker-compose down -v
docker-compose up --build
```

---

## Stopping the Application

### Graceful Shutdown
```bash
# Press Ctrl+C in terminal, then:
docker-compose down
```

### Stop and Keep Data
```bash
docker-compose down
```

### Stop and Delete All Data
```bash
docker-compose down -v
```

---

## Restarting

### Quick Restart (No Rebuild)
```bash
docker-compose up
```

### Full Rebuild
```bash
docker-compose up --build
```

### Fresh Start (Delete Everything)
```bash
docker-compose down -v
docker-compose up --build
```

---

## Health Check Commands

### Check All Services
```bash
docker-compose ps
```

**Expected output:**
```
NAME               STATUS          PORTS
ticket_db          running         0.0.0.0:5432->5432/tcp
ticket_backend     running         0.0.0.0:8000->8000/tcp
ticket_frontend    running         0.0.0.0:3000->3000/tcp
```

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# Follow logs (real-time)
docker-compose logs -f backend
```

### Check Database
```bash
# Enter PostgreSQL
docker-compose exec db psql -U ticketuser -d ticketdb

# List tables
\dt

# Count tickets
SELECT COUNT(*) FROM tickets_ticket;

# Exit
\q
```

### Run Django Commands
```bash
# Check migrations
docker-compose exec backend python manage.py showmigrations

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Django shell
docker-compose exec backend python manage.py shell
```

---

## Success Criteria

✅ All services running (green in `docker-compose ps`)  
✅ Frontend accessible at http://localhost:3000  
✅ Backend accessible at http://localhost:8000/api/  
✅ Can create tickets with AI classification  
✅ Can filter and search tickets  
✅ Statistics display correctly  
✅ No errors in logs  

---

## Ready to Launch?

### Quick Pre-Flight Check:
1. [ ] `.env` has Gemini API key
2. [ ] Docker Desktop running
3. [ ] Ports 3000, 8000, 5432 available
4. [ ] In correct directory

### Launch Command:
```bash
docker-compose up --build
```

### Expected Wait Time:
- First run: 3-5 minutes
- Subsequent runs: 30-60 seconds

### Success Indicators:
- See "webpack compiled successfully"
- See "Starting development server"
- Browser opens to http://localhost:3000
- Application loads without errors

---

## Need Help?

1. Check [QUICKSTART.md](QUICKSTART.md) for quick setup
2. Check [TESTING.md](TESTING.md) for test procedures
3. Check [README.md](README.md) for full documentation
4. Check logs: `docker-compose logs backend`

---

**Everything checked? Let's go!** 🚀

```bash
docker-compose up --build
```
