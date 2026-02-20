# 🎨 System Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────────┐
│                              USER BROWSER                                  │
│                         http://localhost:3000                              │
└───────────────────────────┬───────────────────────────────────────────────┘
                            │
                            │ HTTP/JSON
                            │
┌───────────────────────────▼───────────────────────────────────────────────┐
│                        REACT FRONTEND (PORT 3000)                          │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐           │
│  │  SubmitTicket   │  │   TicketList    │  │ StatsDashboard  │           │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤           │
│  │ • Form inputs   │  │ • Ticket cards  │  │ • Total count   │           │
│  │ • AI classify   │  │ • Filters       │  │ • Open count    │           │
│  │ • Validation    │  │ • Search        │  │ • Avg per day   │           │
│  │ • Submit        │  │ • Update status │  │ • Breakdowns    │           │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘           │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────┐          │
│  │                     api.js (Axios Client)                    │          │
│  │  • GET /tickets/     • POST /tickets/                       │          │
│  │  • PATCH /tickets/:id/   • GET /tickets/stats/              │          │
│  │  • POST /tickets/classify/                                  │          │
│  └─────────────────────────────────────────────────────────────┘          │
│                                                                             │
└───────────────────────────┬───────────────────────────────────────────────┘
                            │
                            │ REST API (JSON)
                            │
┌───────────────────────────▼───────────────────────────────────────────────┐
│                   DJANGO BACKEND (PORT 8000)                               │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────┐          │
│  │                    tickets/urls.py                           │          │
│  │  /api/tickets/          → TicketViewSet                      │          │
│  │  /api/tickets/stats/    → get_stats()                        │          │
│  │  /api/tickets/classify/ → classify_ticket()                  │          │
│  └─────────────────────────────────────────────────────────────┘          │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────┐          │
│  │                    tickets/views.py                          │          │
│  │  TicketViewSet:                                              │          │
│  │    • list() - GET with filters                               │          │
│  │    • create() - POST                                         │          │
│  │    • partial_update() - PATCH                                │          │
│  │    • get_stats() - ORM aggregations                          │          │
│  │    • classify_ticket() - AI classification                   │          │
│  └─────────────────────────────────────────────────────────────┘          │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────┐          │
│  │                  tickets/serializers.py                      │          │
│  │    • TicketSerializer - CRUD validation                      │          │
│  │    • ClassificationRequestSerializer                         │          │
│  │    • ClassificationResponseSerializer                        │          │
│  └─────────────────────────────────────────────────────────────┘          │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────┐          │
│  │                   tickets/services.py                        │          │
│  │    TicketClassifier:                                         │          │
│  │      • classify() - Main method                              │          │
│  │      • CLASSIFICATION_PROMPT - Full prompt                   │          │
│  │      • OpenAI API call (gpt-3.5-turbo)                       │          │
│  │      • Error handling + fallback                             │          │
│  └─────────────────────────────────────────────────────────────┘          │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────┐          │
│  │                    tickets/models.py                         │          │
│  │    Ticket Model:                                             │          │
│  │      • title (CharField, max=200)                            │          │
│  │      • description (TextField)                               │          │
│  │      • category (CHECK constraint)                           │          │
│  │      • priority (CHECK constraint)                           │          │
│  │      • status (CHECK constraint, default='open')             │          │
│  │      • created_at (auto timestamp)                           │          │
│  └─────────────────────────────────────────────────────────────┘          │
│                                                                             │
└──────────┬────────────────────────────────────────┬───────────────────────┘
           │                                         │
           │ SQL                                     │ HTTPS
           │                                         │
┌──────────▼─────────────────┐         ┌────────────▼──────────────────────┐
│  POSTGRESQL (PORT 5432)    │         │       OPENAI API                   │
├────────────────────────────┤         ├───────────────────────────────────┤
│  Database: ticketdb        │         │  Model: gpt-3.5-turbo              │
│  User: ticketuser          │         │  Temperature: 0.3                  │
│                            │         │                                    │
│  Table: tickets_ticket     │         │  Input: Ticket description         │
│    ├─ id (PK)              │         │  Output: {category, priority}      │
│    ├─ title                │         │                                    │
│    ├─ description          │         │  Fallback on error:                │
│    ├─ category             │         │    category: "general"             │
│    ├─ priority             │         │    priority: "medium"              │
│    ├─ status               │         │                                    │
│    └─ created_at           │         └───────────────────────────────────┘
│                            │
│  Constraints:              │
│    ✓ valid_category        │
│    ✓ valid_priority        │
│    ✓ valid_status          │
│                            │
│  Indexes:                  │
│    ✓ created_at DESC       │
│    ✓ category + status     │
│    ✓ priority + status     │
└────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                          DOCKER COMPOSE ORCHESTRATION
═══════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│                      docker-compose.yml                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  services:                                                                │
│    db:                                                                    │
│      image: postgres:15-alpine                                            │
│      ports: 5432:5432                                                     │
│      healthcheck: pg_isready                                              │
│                                                                           │
│    backend:                                                               │
│      build: ./backend                                                     │
│      ports: 8000:8000                                                     │
│      depends_on: db (with health check)                                   │
│      command: /app/entrypoint.sh                                          │
│        └─ Wait for DB                                                     │
│        └─ Run migrations                                                  │
│        └─ Start Django                                                    │
│                                                                           │
│    frontend:                                                              │
│      build: ./frontend                                                    │
│      ports: 3000:3000                                                     │
│      depends_on: backend                                                  │
│      command: npm start                                                   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                              DATA FLOW EXAMPLE
═══════════════════════════════════════════════════════════════════════════

  USER CREATES TICKET: "I was charged twice for my subscription"
                              │
                              ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. User types description in SubmitTicket.js                │
  └─────────────┬───────────────────────────────────────────────┘
                │
                ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 2. Frontend → POST /api/tickets/classify/                   │
  │    { "description": "I was charged twice..." }              │
  └─────────────┬───────────────────────────────────────────────┘
                │
                ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 3. Django → TicketClassifier.classify()                     │
  └─────────────┬───────────────────────────────────────────────┘
                │
                ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 4. OpenAI API call with CLASSIFICATION_PROMPT               │
  │    Prompt includes: description + category rules            │
  └─────────────┬───────────────────────────────────────────────┘
                │
                ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 5. AI responds: {"category": "billing", "priority": "high"} │
  └─────────────┬───────────────────────────────────────────────┘
                │
                ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 6. Django returns to Frontend                                │
  └─────────────┬───────────────────────────────────────────────┘
                │
                ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 7. Frontend auto-fills dropdowns                            │
  │    Category: Billing ✓                                       │
  │    Priority: High ✓                                          │
  └─────────────┬───────────────────────────────────────────────┘
                │
                ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 8. User reviews (can change) and clicks Submit              │
  └─────────────┬───────────────────────────────────────────────┘
                │
                ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 9. Frontend → POST /api/tickets/                            │
  │    Full ticket data                                          │
  └─────────────┬───────────────────────────────────────────────┘
                │
                ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 10. Django validates via TicketSerializer                   │
  └─────────────┬───────────────────────────────────────────────┘
                │
                ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 11. PostgreSQL enforces CHECK constraints                   │
  └─────────────┬───────────────────────────────────────────────┘
                │
                ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 12. Ticket saved with ID, timestamp                         │
  └─────────────┬───────────────────────────────────────────────┘
                │
                ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 13. Django returns 201 with full ticket object              │
  └─────────────┬───────────────────────────────────────────────┘
                │
                ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 14. Frontend:                                                │
  │     • Clears form                                            │
  │     • Shows success message                                  │
  │     • Switches to "All Tickets" tab                          │
  │     • Adds new ticket to list (no reload)                    │
  │     • Updates statistics                                     │
  └─────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                        STATISTICS CALCULATION FLOW
═══════════════════════════════════════════════════════════════════════════

  USER CLICKS "STATISTICS" TAB
                │
                ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Frontend → GET /api/tickets/stats/                          │
  └─────────────┬───────────────────────────────────────────────┘
                │
                ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Django executes ORM queries (ALL AT DATABASE LEVEL):        │
  │                                                              │
  │ 1. total = Ticket.objects.count()                           │
  │                                                              │
  │ 2. open = Ticket.objects.filter(status='open').count()      │
  │                                                              │
  │ 3. oldest = Ticket.objects.order_by('created_at').first()   │
  │    days = (now - oldest.created_at).days                    │
  │    avg = total / max(days, 1)                               │
  │                                                              │
  │ 4. priority_breakdown = Ticket.objects                      │
  │      .values('priority')                                    │
  │      .annotate(count=Count('id'))                           │
  │      .values_list('priority', 'count')                      │
  │                                                              │
  │ 5. category_breakdown = Ticket.objects                      │
  │      .values('category')                                    │
  │      .annotate(count=Count('id'))                           │
  │      .values_list('category', 'count')                      │
  └─────────────┬───────────────────────────────────────────────┘
                │
                ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ Returns JSON:                                                │
  │ {                                                            │
  │   "total_tickets": 150,                                      │
  │   "open_tickets": 45,                                        │
  │   "avg_tickets_per_day": 12.5,                              │
  │   "priority_breakdown": {                                    │
  │     "low": 30, "medium": 60, "high": 45, "critical": 15     │
  │   },                                                         │
  │   "category_breakdown": {                                    │
  │     "billing": 40, "technical": 50,                          │
  │     "account": 35, "general": 25                             │
  │   }                                                          │
  │ }                                                            │
  └─────────────┬───────────────────────────────────────────────┘
                │
                ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ StatsDashboard.js renders:                                   │
  │  • Stat cards with gradient backgrounds                      │
  │  • Priority breakdown with color coding                      │
  │  • Category breakdown with counts                            │
  └─────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                            KEY COMPONENTS
═══════════════════════════════════════════════════════════════════════════

BACKEND:
  ✓ Django 4.2.7 + DRF 3.14.0
  ✓ 5 API endpoints (CRUD + Stats + Classify)
  ✓ Database-level constraints
  ✓ ORM aggregations (no Python loops)
  ✓ OpenAI integration with fallback
  ✓ Comprehensive validation

FRONTEND:
  ✓ React 18.2.0 (functional components + hooks)
  ✓ 3 main pages (Submit, List, Stats)
  ✓ Real-time AI classification
  ✓ Advanced filtering (4 types, combinable)
  ✓ Auto-refresh without reload
  ✓ Responsive design

DATABASE:
  ✓ PostgreSQL 15
  ✓ CHECK constraints (category, priority, status)
  ✓ Multiple indexes for performance
  ✓ Persistent data in Docker volume

INFRASTRUCTURE:
  ✓ Docker Compose orchestration
  ✓ Automatic migrations on startup
  ✓ Health checks and dependencies
  ✓ Environment-based configuration
  ✓ Single command deployment


═══════════════════════════════════════════════════════════════════════════
                          DEPLOYMENT COMMAND
═══════════════════════════════════════════════════════════════════════════

                        docker-compose up --build

                    Starts everything in correct order:
                         1. PostgreSQL (with health check)
                         2. Django (waits for DB, runs migrations)
                         3. React (waits for backend)

                    Access:
                         Frontend: http://localhost:3000
                         Backend:  http://localhost:8000/api
                         Admin:    http://localhost:8000/admin


═══════════════════════════════════════════════════════════════════════════
