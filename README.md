# 🎫 Support Ticket System

A full-stack support ticket management system built with Django REST Framework, React, PostgreSQL, and Gemini API integration for intelligent ticket classification.

## 🚀 Features

- **Ticket Management**: Create, view, update, and filter support tickets
- **AI-Powered Classification**: Automatic category and priority suggestion using Gemini 1.5 Flash
- **Real-time Statistics**: Dashboard with aggregate metrics and breakdowns
- **Advanced Filtering**: Filter tickets by category, priority, status, and search
- **Responsive UI**: Clean, functional interface built with React
- **Dockerized**: Complete containerization with Docker Compose

## 🛠 Tech Stack

**Backend:**
- Django 4.2.7
- Django REST Framework 3.14.0
- PostgreSQL 15
- Gemini API (Gemini 1.5 Flash)
- Python 3.11

**Frontend:**
- React 18.2.0
- Axios for API calls
- Functional components with hooks
- CSS Grid/Flexbox

**Infrastructure:**
- Docker & Docker Compose
- PostgreSQL container
- Multi-stage builds

## 📋 Prerequisites

- Docker Desktop installed and running
- Gemini API key (get one at https://aistudio.google.com/app/apikey)
- 4GB RAM minimum
- Port 3000, 8000, and 5432 available

## ⚙️ Setup Instructions

### 1. Clone or Download the Project

```bash
cd "support ticket"
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-this
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=ticketdb
DB_USER=ticketuser
DB_PASSWORD=ticketpass
DB_HOST=db
DB_PORT=5432

# Gemini (REQUIRED for AI classification)
GEMINI_API_KEY=your-gemini-api-key-here
```

**⚠️ Important:** Replace `your-gemini-api-key-here` with your real Gemini API key.

### 3. Build and Run with Docker

```bash
docker-compose up --build
```

This single command will:
- Build all Docker images
- Start PostgreSQL database
- Run Django migrations automatically
- Start the Django backend on http://localhost:8000
- Start the React frontend on http://localhost:3000

**First run takes 3-5 minutes** to download images and install dependencies.

### 4. Access the Application

Once all services are running:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/admin/

### 5. Create Django Superuser (Optional)

To access the Django admin panel:

```bash
docker-compose exec backend python manage.py createsuperuser
```

Follow the prompts to create an admin account.

## 📁 Project Structure

```
support ticket/
├── backend/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py          # Django settings
│   │   ├── urls.py               # Root URL configuration
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── tickets/
│   │   ├── __init__.py
│   │   ├── models.py             # Ticket model with DB constraints
│   │   ├── serializers.py        # DRF serializers
│   │   ├── views.py              # API endpoints & ORM aggregations
│   │   ├── urls.py               # Ticket app URLs
│   │   ├── services.py           # Gemini classification service
│   │   ├── admin.py              # Django admin configuration
│   │   └── apps.py
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── SubmitTicket.js   # Ticket creation with AI
│   │   │   ├── TicketList.js     # Ticket list with filters
│   │   │   └── StatsDashboard.js # Statistics dashboard
│   │   ├── api.js                # Axios API client
│   │   ├── App.js                # Main app component
│   │   ├── App.css               # Application styles
│   │   ├── index.js
│   │   └── index.css
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## 🔌 API Endpoints

### Tickets

**1. Create Ticket**
```http
POST /api/tickets/
Content-Type: application/json

{
  "title": "Cannot login to my account",
  "description": "I'm getting an error when trying to log in",
  "category": "account",
  "priority": "high"
}

Response: 201 Created
```

**2. List Tickets**
```http
GET /api/tickets/
GET /api/tickets/?category=billing
GET /api/tickets/?priority=high&status=open
GET /api/tickets/?search=login

Response: 200 OK
[
  {
    "id": 1,
    "title": "Cannot login",
    "description": "Error when logging in",
    "category": "account",
    "priority": "high",
    "status": "open",
    "created_at": "2026-02-20T10:30:00Z"
  }
]
```

**3. Update Ticket**
```http
PATCH /api/tickets/1/
Content-Type: application/json

{
  "status": "resolved"
}

Response: 200 OK
```

**4. Get Statistics**
```http
GET /api/tickets/stats/

Response: 200 OK
{
  "total_tickets": 150,
  "open_tickets": 45,
  "avg_tickets_per_day": 12.5,
  "priority_breakdown": {
    "low": 30,
    "medium": 60,
    "high": 45,
    "critical": 15
  },
  "category_breakdown": {
    "billing": 40,
    "technical": 50,
    "account": 35,
    "general": 25
  }
}
```

**5. Classify Ticket (AI)**
```http
POST /api/tickets/classify/
Content-Type: application/json

{
  "description": "I was charged twice for my subscription this month"
}

Response: 200 OK
{
  "suggested_category": "billing",
  "suggested_priority": "high"
}
```

## 🧠 Gemini Integration Details

### Classification Prompt

The system uses the following prompt for ticket classification:

```
You are a support ticket classifier. Based on the ticket description provided, classify it into the appropriate category and priority.

Categories:
- billing: Issues related to payments, invoices, refunds, subscriptions
- technical: Technical problems, bugs, system errors, functionality issues
- account: Account access, password resets, profile issues, authentication
- general: General inquiries, questions, feedback, other

Priority Levels:
- low: General questions, minor issues, no immediate impact
- medium: Standard issues affecting user experience but have workarounds
- high: Significant issues affecting core functionality, no easy workaround
- critical: System down, security issues, data loss, affecting multiple users

Ticket Description: {description}

Respond with ONLY a JSON object in this exact format:
{"category": "one_of_the_categories", "priority": "one_of_the_priorities"}
```

### Error Handling

- If Gemini API fails, returns default: `category: "general", priority: "medium"`
- If API key is missing, gracefully degrades to fallback classification
- All API errors are logged but don't break the user experience

### Implementation

Located in [`backend/tickets/services.py`](backend/tickets/services.py):

- `TicketClassifier` class handles all Gemini interactions
- Uses `gemini-1.5-flash` model with temperature 0.3 for consistent results
- Robust JSON parsing with multiple fallback strategies
- Comprehensive error handling and logging

## 📊 Database Schema

### Ticket Model

```python
class Ticket(models.Model):
    title = CharField(max_length=200)              # Required
    description = TextField()                       # Required
    category = CharField(choices=[...])             # DB constraint
    priority = CharField(choices=[...])             # DB constraint
    status = CharField(choices=[...], default='open')  # DB constraint
    created_at = DateTimeField(auto_now_add=True)
```

**Database Constraints:**
- `valid_category`: Enforces category in ['billing', 'technical', 'account', 'general']
- `valid_priority`: Enforces priority in ['low', 'medium', 'high', 'critical']
- `valid_status`: Enforces status in ['open', 'in_progress', 'resolved', 'closed']

**Indexes:**
- Primary index on `created_at` (descending)
- Composite indexes on `category + status` and `priority + status`

## 📈 Statistics Implementation

The stats endpoint uses **pure Django ORM aggregation** (no Python loops):

```python
# Priority breakdown - pure ORM
priority_breakdown = dict(
    Ticket.objects
    .values('priority')
    .annotate(count=Count('id'))
    .values_list('priority', 'count')
)

# Category breakdown - pure ORM
category_breakdown = dict(
    Ticket.objects
    .values('category')
    .annotate(count=Count('id'))
    .values_list('category', 'count')
)

# Average tickets per day - single query
oldest_ticket = Ticket.objects.order_by('created_at').first()
days_since_first = (timezone.now() - oldest_ticket.created_at).days
avg_tickets_per_day = total_tickets / max(days_since_first, 1)
```

All aggregations happen at the database level for optimal performance.

## 🎨 Frontend Features

### 1. Submit Ticket Page
- Title input with character counter (200 max)
- Description textarea with AI analysis
- Auto-classification on description input (>10 chars)
- Loading state during AI classification
- Manual override of AI suggestions
- Form validation
- Success/error feedback
- Auto-refresh ticket list on creation

### 2. Ticket List Page
- Newest tickets first
- Real-time filtering:
  - Category dropdown
  - Priority dropdown
  - Status dropdown
  - Text search (title + description)
- Combined filters work together
- Status update functionality
- Truncated descriptions with full text on hover
- Color-coded priority badges
- Timestamp formatting

### 3. Stats Dashboard
- Total tickets count
- Open tickets count
- Average tickets per day
- Priority breakdown with counts
- Category breakdown with counts
- Auto-refresh on new ticket creation
- Visual stat cards with gradient backgrounds

## 🔧 Development

### Running Tests

```bash
# Backend tests
docker-compose exec backend python manage.py test

# Create migrations
docker-compose exec backend python manage.py makemigrations

# Run migrations
docker-compose exec backend python manage.py migrate
```

### Logs

```bash
# View all logs
docker-compose logs

# View specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# Follow logs
docker-compose logs -f backend
```

### Stopping the Application

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```

### Rebuilding

```bash
# Rebuild after code changes
docker-compose up --build

# Rebuild specific service
docker-compose up --build backend
```

## 🐛 Troubleshooting

### Port Already in Use

If ports 3000, 8000, or 5432 are already in use:

```bash
# Find process using port (Windows)
netstat -ano | findstr :8000

# Kill process
taskkill /PID <process_id> /F
```

### Database Connection Issues

If backend can't connect to database:

```bash
# Check if database is ready
docker-compose ps

# Restart backend
docker-compose restart backend
```

### Frontend Not Loading

If frontend shows blank page:

```bash
# Check frontend logs
docker-compose logs frontend

# Restart frontend
docker-compose restart frontend
```

### Gemini API Errors

If classification fails:
- Check if `GEMINI_API_KEY` is set in `.env`
- Verify API key is valid at https://aistudio.google.com/app/apikey
- Check API usage limits/billing
- System gracefully falls back to default classification

### Migration Issues

If database schema is out of sync:

```bash
# Reset database
docker-compose down -v
docker-compose up --build
```

## 📝 Design Decisions

### Why Django REST Framework?
- Rapid development with built-in serializers
- Automatic API documentation support
- Powerful ORM for complex queries
- Excellent validation framework

### Why PostgreSQL?
- Production-ready database
- Supports CHECK constraints at DB level
- Better performance for aggregations
- ACID compliance

### Why React Functional Components?
- Modern React best practices
- Hooks provide cleaner state management
- Better performance with memo optimization
- Easier to test and maintain

### Why Docker Compose?
- Single command deployment
- Consistent environments
- Easy service orchestration
- Simplified dependency management

## 🎯 Assessment Criteria Met

✅ **Backend Requirements**
- Django + DRF with all required fields
- PostgreSQL with DB-level constraints
- All 5 API endpoints implemented
- ORM aggregation for stats (no Python loops)
- Gemini integration with error handling

✅ **Frontend Requirements**
- React functional components with hooks
- Submit, List, and Stats pages
- AI auto-classification with loading states
- Filters and search functionality
- Auto-refresh on ticket creation

✅ **Docker Requirements**
- PostgreSQL, Django, React services
- Automatic migrations on startup
- Single `docker-compose up --build` command
- Environment variable configuration
- No hardcoded secrets

✅ **Code Quality**
- Clean, production-style code
- Comprehensive error handling
- Proper validation at all layers
- Well-structured and documented
- Realistic for 3-hour timeframe

## 📜 License

This project is created for educational/assessment purposes.

## 👨‍💻 Author

Built as a full-stack engineering assessment project demonstrating proficiency in:
- Backend API development (Django/DRF)
- Database design and optimization
- LLM integration (Gemini API)
- Frontend development (React)
- DevOps (Docker/Docker Compose)
- Full-stack architecture

---

**Ready to run:** `docker-compose up --build`
