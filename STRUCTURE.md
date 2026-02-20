# Project Structure

```
support ticket/
│
├── backend/                          # Django Backend
│   ├── config/                       # Django Project Configuration
│   │   ├── __init__.py
│   │   ├── settings.py               # Main settings (DB, CORS, REST Framework)
│   │   ├── urls.py                   # Root URL routing
│   │   ├── wsgi.py                   # WSGI config
│   │   └── asgi.py                   # ASGI config
│   │
│   ├── tickets/                      # Tickets App
│   │   ├── __init__.py
│   │   ├── apps.py                   # App configuration
│   │   ├── models.py                 # Ticket model with DB constraints
│   │   ├── serializers.py            # DRF serializers for validation
│   │   ├── views.py                  # ViewSet with all endpoints
│   │   ├── urls.py                   # App URL routing
│   │   ├── services.py               # OpenAI classification service
│   │   └── admin.py                  # Django admin customization
│   │
│   ├── manage.py                     # Django management script
│   ├── requirements.txt              # Python dependencies
│   └── Dockerfile                    # Backend container definition
│
├── frontend/                         # React Frontend
│   ├── public/
│   │   └── index.html                # HTML template
│   │
│   ├── src/
│   │   ├── components/
│   │   │   ├── SubmitTicket.js       # Ticket creation form + AI
│   │   │   ├── TicketList.js         # Ticket list with filters
│   │   │   └── StatsDashboard.js     # Statistics dashboard
│   │   │
│   │   ├── api.js                    # Axios API client
│   │   ├── App.js                    # Main app component
│   │   ├── App.css                   # Application styles
│   │   ├── index.js                  # React entry point
│   │   └── index.css                 # Global styles
│   │
│   ├── package.json                  # NPM dependencies
│   └── Dockerfile                    # Frontend container definition
│
├── docker-compose.yml                # Docker orchestration
├── .env.example                      # Environment variables template
├── .gitignore                        # Git ignore rules
├── README.md                         # Complete documentation
├── API_REFERENCE.md                  # API quick reference
├── STRUCTURE.md                      # This file
├── start.sh                          # Linux/Mac startup script
└── start.bat                         # Windows startup script
```

## File Descriptions

### Backend Files

**config/settings.py**
- Database configuration (PostgreSQL)
- CORS settings for frontend
- REST Framework configuration
- OpenAI API key from environment
- Security settings

**tickets/models.py**
- Ticket model definition
- Database-level CHECK constraints
- Indexes for performance
- Field choices and defaults

**tickets/serializers.py**
- TicketSerializer for CRUD operations
- ClassificationRequestSerializer for AI endpoint
- ClassificationResponseSerializer for validation
- Field-level validation

**tickets/views.py**
- TicketViewSet with all CRUD operations
- Custom filter logic (category, priority, status, search)
- Stats endpoint with ORM aggregations
- Classification endpoint with error handling

**tickets/services.py**
- TicketClassifier class
- OpenAI API integration
- Classification prompt (included in code)
- Robust error handling and fallbacks

### Frontend Files

**components/SubmitTicket.js**
- Ticket creation form
- Auto-classification on description input
- Loading states for AI processing
- Form validation and error handling
- Success feedback and form reset

**components/TicketList.js**
- Ticket display with newest first
- Category, priority, status filters
- Search functionality (title + description)
- Status update with inline editing
- Color-coded badges and formatting

**components/StatsDashboard.js**
- Total and open ticket counts
- Average tickets per day
- Priority breakdown visualization
- Category breakdown visualization
- Auto-refresh on ticket creation

**api.js**
- Axios instance configuration
- API base URL from environment
- All API methods (getTickets, createTicket, etc.)
- Centralized API logic

**App.js**
- Main component with tab navigation
- State management for active tab
- Refresh trigger mechanism
- Component composition

**App.css**
- Responsive grid layouts
- Color-coded priority/status badges
- Form styling
- Dashboard card styling
- Mobile-responsive breakpoints

### Docker Files

**backend/Dockerfile**
- Python 3.11 slim base image
- Dependencies installation
- Entrypoint script creation
- Automatic migration on startup
- Health check with netcat

**frontend/Dockerfile**
- Node 18 Alpine base image
- NPM dependencies installation
- Development server configuration
- Port 3000 exposure

**docker-compose.yml**
- PostgreSQL service (port 5432)
- Django backend service (port 8000)
- React frontend service (port 3000)
- Service dependencies and health checks
- Volume mounts for development
- Environment variable passing

## Key Features by File

### Database Constraints (models.py)
```python
constraints = [
    CheckConstraint(check=Q(category__in=['billing', 'technical', 'account', 'general'])),
    CheckConstraint(check=Q(priority__in=['low', 'medium', 'high', 'critical'])),
    CheckConstraint(check=Q(status__in=['open', 'in_progress', 'resolved', 'closed']))
]
```

### ORM Aggregation (views.py)
```python
priority_breakdown = dict(
    Ticket.objects
    .values('priority')
    .annotate(count=Count('id'))
    .values_list('priority', 'count')
)
```

### AI Classification (services.py)
```python
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[...],
    temperature=0.3
)
```

### Filtering Logic (views.py)
```python
queryset = queryset.filter(
    Q(title__icontains=search) | Q(description__icontains=search)
)
```

## Environment Variables

Required in `.env`:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - Comma-separated hosts
- `DB_NAME` - PostgreSQL database name
- `DB_USER` - PostgreSQL username
- `DB_PASSWORD` - PostgreSQL password
- `DB_HOST` - Database host (db in Docker)
- `DB_PORT` - Database port (5432)
- `OPENAI_API_KEY` - OpenAI API key (required)

## Running the Application

**Simple:**
```bash
docker-compose up --build
```

**With scripts:**
```bash
# Windows
start.bat

# Linux/Mac
chmod +x start.sh
./start.sh
```

## Development Workflow

1. Edit code in your IDE
2. Changes hot-reload automatically (frontend)
3. Backend changes require container restart
4. Database persists in Docker volume
5. Logs available via `docker-compose logs`

## Production Considerations

Not included (out of scope for assessment):
- Gunicorn/uWSGI for production ASGI
- Nginx reverse proxy
- Static file serving (Whitenoise or S3)
- HTTPS/SSL certificates
- Environment-specific settings
- Database backups
- Monitoring and logging
- Rate limiting
- Authentication/Authorization
- CI/CD pipeline
