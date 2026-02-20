# API Quick Reference

Base URL: `http://localhost:8000/api`

## Endpoints

### 1. List Tickets
```http
GET /tickets/
GET /tickets/?category=billing
GET /tickets/?priority=high
GET /tickets/?status=open
GET /tickets/?search=login
GET /tickets/?category=technical&priority=critical&status=open
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "Cannot login to account",
    "description": "Getting authentication error",
    "category": "account",
    "priority": "high",
    "status": "open",
    "created_at": "2026-02-20T10:30:00Z"
  }
]
```

### 2. Create Ticket
```http
POST /tickets/
Content-Type: application/json

{
  "title": "Billing issue",
  "description": "I was charged twice",
  "category": "billing",
  "priority": "high"
}
```

**Response:** `201 Created`

### 3. Update Ticket
```http
PATCH /tickets/{id}/
Content-Type: application/json

{
  "status": "resolved"
}
```

**Response:** `200 OK`

### 4. Get Statistics
```http
GET /tickets/stats/
```

**Response:**
```json
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

### 5. Classify Ticket (AI)
```http
POST /tickets/classify/
Content-Type: application/json

{
  "description": "I was charged twice for my subscription"
}
```

**Response:**
```json
{
  "suggested_category": "billing",
  "suggested_priority": "high"
}
```

## Field Constraints

### Category (required)
- `billing` - Payment, invoice, refund issues
- `technical` - Bugs, errors, functionality issues
- `account` - Access, password, profile issues
- `general` - General inquiries, feedback

### Priority (required)
- `low` - Minor issues, no immediate impact
- `medium` - Standard issues with workarounds
- `high` - Significant issues, no workaround
- `critical` - System down, data loss, security

### Status
- `open` (default) - New ticket
- `in_progress` - Being worked on
- `resolved` - Issue fixed
- `closed` - Ticket closed

## Testing with curl

```bash
# Create a ticket
curl -X POST http://localhost:8000/api/tickets/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test ticket",
    "description": "This is a test",
    "category": "general",
    "priority": "low"
  }'

# Get all tickets
curl http://localhost:8000/api/tickets/

# Filter tickets
curl "http://localhost:8000/api/tickets/?category=billing&priority=high"

# Search tickets
curl "http://localhost:8000/api/tickets/?search=login"

# Get stats
curl http://localhost:8000/api/tickets/stats/

# Classify description
curl -X POST http://localhost:8000/api/tickets/classify/ \
  -H "Content-Type: application/json" \
  -d '{"description": "Cannot access my account"}'

# Update ticket status
curl -X PATCH http://localhost:8000/api/tickets/1/ \
  -H "Content-Type: application/json" \
  -d '{"status": "resolved"}'
```

## Error Responses

### 400 Bad Request
```json
{
  "title": ["This field is required."],
  "category": ["\"invalid\" is not a valid choice."]
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```
