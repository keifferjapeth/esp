# MO AI Backend API Reference

## Base URL

**Development:** `http://localhost:8080`  
**Production:** `https://mo-ai-backend.run.app`

## Authentication

All production endpoints require Bearer token authentication:

```
Authorization: Bearer <JWT_TOKEN>
```

## Endpoints

---

## 1. Health & Status

### GET /health
Health check endpoint.

**Request:**
```bash
curl http://localhost:8080/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-04T10:30:00Z",
  "version": "1.0.0",
  "uptime_seconds": 3600
}
```

**Status Codes:**
- `200 OK` - Service is healthy
- `503 Service Unavailable` - Service is down

---

## 2. Command Execution

### POST /api/execute
Execute a natural language command.

**Request:**
```bash
curl -X POST http://localhost:8080/api/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "command": "analyze leads for property valuation"
  }'
```

**Request Body:**
```json
{
  "command": "string",           # Natural language command (required)
  "context": "object",           # Optional context data
  "parameters": "object"         # Optional parameters
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "data": {},
    "insights": "string"
  },
  "execution_time_ms": 234,
  "timestamp": "2025-11-04T10:30:00Z"
}
```

**Supported Commands:**
- `"check acrobat project status"`
- `"score leads for <property_id>"`
- `"predict property value for <address>"`
- `"cluster leads by market"`
- `"analyze big query data"`
- `"generate content about <topic>"`

**Status Codes:**
- `200 OK` - Command executed successfully
- `400 Bad Request` - Invalid command format
- `401 Unauthorized` - Missing/invalid authentication
- `500 Internal Server Error` - Execution failed

**Example with context:**
```bash
curl -X POST http://localhost:8080/api/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "command": "score leads",
    "context": {
      "property_id": "12345",
      "market": "NYC"
    },
    "parameters": {
      "threshold": 0.7
    }
  }'
```

---

## 3. Acrobat Project Endpoints

### GET /api/acrobat/status
Get Acrobat project status and available models.

**Request:**
```bash
curl http://localhost:8080/api/acrobat/status \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "project_id": "alert-acrobat-477200-g9",
  "status": "active",
  "region": "us-central1",
  "models": [
    {
      "name": "lead_scoring",
      "type": "classification",
      "endpoint": "/api/acrobat/lead_scoring",
      "status": "active"
    },
    {
      "name": "property_valuation",
      "type": "regression",
      "endpoint": "/api/acrobat/property_valuation",
      "status": "active"
    },
    {
      "name": "market_trend",
      "type": "forecasting",
      "endpoint": "/api/acrobat/market_trend",
      "status": "active"
    },
    {
      "name": "lead_clustering",
      "type": "clustering",
      "endpoint": "/api/acrobat/lead_clustering",
      "status": "active"
    }
  ]
}
```

### POST /api/acrobat/lead_scoring
Score leads for conversion probability.

**Request:**
```bash
curl -X POST http://localhost:8080/api/acrobat/lead_scoring \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "lead_id": "L12345",
    "properties": {
      "engagement_score": 0.85,
      "response_time_hours": 24,
      "property_views": 5
    }
  }'
```

**Response:**
```json
{
  "lead_id": "L12345",
  "conversion_probability": 0.78,
  "confidence": 0.92,
  "recommendation": "high_priority",
  "features_influence": {
    "engagement_score": 0.35,
    "response_time": 0.28,
    "property_views": 0.37
  }
}
```

### POST /api/acrobat/property_valuation
Predict property value.

**Request:**
```bash
curl -X POST http://localhost:8080/api/acrobat/property_valuation \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "property_id": "P98765",
    "features": {
      "square_feet": 2500,
      "bedrooms": 4,
      "bathrooms": 2.5,
      "year_built": 2005,
      "zip_code": "10001"
    }
  }'
```

**Response:**
```json
{
  "property_id": "P98765",
  "estimated_value": 750000,
  "confidence_interval": {
    "lower": 720000,
    "upper": 780000
  },
  "market_comparison": 1.05,
  "valuation_date": "2025-11-04"
}
```

### POST /api/acrobat/market_trend
Forecast market trends.

**Request:**
```bash
curl -X POST http://localhost:8080/api/acrobat/market_trend \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "market": "NYC",
    "forecast_months": 6
  }'
```

**Response:**
```json
{
  "market": "NYC",
  "forecast_period": "6 months",
  "trend": "upward",
  "predicted_growth": 0.08,
  "confidence": 0.85,
  "forecast_data": [
    {
      "month": 1,
      "predicted_value": 755000
    },
    {
      "month": 2,
      "predicted_value": 765000
    }
  ]
}
```

### POST /api/acrobat/lead_clustering
Cluster leads into segments.

**Request:**
```bash
curl -X POST http://localhost:8080/api/acrobat/lead_clustering \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "leads": [
      {"id": "L1", "features": [0.8, 0.9, 0.7]},
      {"id": "L2", "features": [0.2, 0.3, 0.25]}
    ],
    "num_clusters": 3
  }'
```

**Response:**
```json
{
  "clusters": [
    {
      "cluster_id": 0,
      "leads": ["L1"],
      "centroid": [0.8, 0.9, 0.7],
      "characteristics": "high_value"
    },
    {
      "cluster_id": 1,
      "leads": ["L2"],
      "centroid": [0.2, 0.3, 0.25],
      "characteristics": "low_value"
    }
  ]
}
```

---

## 4. BigQuery Endpoints

### GET /api/bigquery/status
Get BigQuery connection status.

**Request:**
```bash
curl http://localhost:8080/api/bigquery/status \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "status": "connected",
  "project": "aimo-460701",
  "datasets": ["masterdata_raw", "masterdata_clean", "masterdata_analytics"],
  "last_check": "2025-11-04T10:30:00Z"
}
```

### POST /api/bigquery/query
Execute a BigQuery query.

**Request:**
```bash
curl -X POST http://localhost:8080/api/bigquery/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "SELECT COUNT(*) as lead_count FROM `aimo-460701.masterdata_raw.leads`",
    "limit": 1000
  }'
```

**Response:**
```json
{
  "rows": [
    {
      "lead_count": 244567
    }
  ],
  "total_rows": 1,
  "total_bytes_processed": 5242880,
  "execution_time_ms": 1234
}
```

### POST /api/bigquery/load
Load data into BigQuery.

**Request:**
```bash
curl -X POST http://localhost:8080/api/bigquery/load \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "dataset": "masterdata_raw",
    "table": "leads_new",
    "data": [
      {"lead_id": "L1", "name": "John Doe", "email": "john@example.com"}
    ]
  }'
```

**Response:**
```json
{
  "status": "success",
  "rows_loaded": 1,
  "table": "projects/aimo-460701/datasets/masterdata_raw/tables/leads_new"
}
```

---

## 5. Gemini API Endpoints

### POST /api/gemini/generate
Generate text using Gemini.

**Request:**
```bash
curl -X POST http://localhost:8080/api/gemini/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "prompt": "Write a brief description of a luxury apartment in Manhattan",
    "model": "gemini-2.0-flash-exp"
  }'
```

**Response:**
```json
{
  "text": "This luxurious Manhattan apartment features...",
  "model": "gemini-2.0-flash-exp",
  "finish_reason": "STOP",
  "tokens_used": 145
}
```

### POST /api/gemini/chat
Chat with Gemini.

**Request:**
```bash
curl -X POST http://localhost:8080/api/gemini/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is the best neighborhood for real estate investment in NYC?"}
    ],
    "model": "gemini-2.0-flash-exp"
  }'
```

**Response:**
```json
{
  "reply": "Based on current market trends, areas like...",
  "tokens_used": 256,
  "model": "gemini-2.0-flash-exp"
}
```

---

## 6. Analytics Endpoints

### GET /api/analytics/dashboard
Get dashboard analytics.

**Request:**
```bash
curl http://localhost:8080/api/analytics/dashboard \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "total_leads": 244567,
  "active_agents": 23,
  "properties_listed": 1245,
  "conversion_rate": 0.156,
  "average_deal_value": 750000,
  "ytd_revenue": 2850000000
}
```

### GET /api/analytics/leads
Get lead analytics.

**Request:**
```bash
curl "http://localhost:8080/api/analytics/leads?period=30days&market=NYC" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "period": "30days",
  "market": "NYC",
  "total_leads": 15643,
  "new_leads": 3245,
  "converted_leads": 485,
  "conversion_rate": 0.031,
  "average_lead_value": 125000,
  "top_agents": [
    {"agent_id": "A001", "leads": 234, "conversions": 45}
  ]
}
```

---

## Error Handling

All endpoints return error responses in this format:

```json
{
  "status": "error",
  "error": "Invalid command",
  "details": "The command 'xyz' is not recognized",
  "error_code": "INVALID_COMMAND",
  "timestamp": "2025-11-04T10:30:00Z"
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `INVALID_COMMAND` | 400 | Command format is invalid |
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `FORBIDDEN` | 403 | User lacks required permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Too many requests |
| `SERVER_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

---

## Rate Limiting

- **Gemini API**: 60 requests/minute
- **BigQuery**: 5,000 requests/minute
- **Vertex AI**: 100 requests/minute
- **General**: 1,000 requests/minute per user

Headers returned:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1733318400
```

---

## Code Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8080"
TOKEN = "your_jwt_token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Execute command
response = requests.post(
    f"{BASE_URL}/api/execute",
    headers=headers,
    json={"command": "score leads"}
)
result = response.json()
print(result)
```

### JavaScript

```javascript
const baseUrl = "http://localhost:8080";
const token = "your_jwt_token";

async function executeCommand(command) {
  const response = await fetch(`${baseUrl}/api/execute`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ command })
  });
  return await response.json();
}

executeCommand("score leads").then(console.log);
```

### cURL

```bash
TOKEN="your_jwt_token"

curl -X POST http://localhost:8080/api/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command": "score leads"}'
```

---

## Pagination

Endpoints that return large datasets support pagination:

```bash
curl "http://localhost:8080/api/analytics/leads?page=1&page_size=100" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total_pages": 25,
    "total_items": 2456
  }
}
```

---

## WebSocket Support

For real-time updates (production):

```javascript
const socket = new WebSocket("wss://mo-ai-backend.run.app/ws");

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Update:", data);
};
```

---

## Support

For API issues or questions:
- Check logs: `gcloud logging read ...`
- Review documentation: `CLOUD_DEPLOYMENT_GUIDE.md`
- Contact: support@moai.dev
