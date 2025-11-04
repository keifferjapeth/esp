# MO AI Cloud - Troubleshooting & Support Guide

## Common Issues & Solutions

---

## 1. Authentication Issues

### Problem: "Invalid JWT Signature" - BigQuery

**Symptoms:**
```
Error: invalid_grant: Invalid JWT Signature
Status: 400
```

**Root Causes:**
1. API key used instead of service account key
2. Service account key expired
3. System clock out of sync
4. Key corrupted or malformed

**Solutions:**

**Option A: Use Service Account Key (Recommended)**
```bash
# 1. Create service account
gcloud iam service-accounts create mo-ai-backend

# 2. Create and download key
gcloud iam service-accounts keys create key.json \
  --iam-account=mo-ai-backend@PROJECT_ID.iam.gserviceaccount.com

# 3. Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# 4. Grant permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:mo-ai-backend@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"
```

**Option B: Use OAuth2**
```python
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

scopes = ["https://www.googleapis.com/auth/bigquery"]
credentials = Credentials.from_service_account_file(
    "key.json",
    scopes=scopes
)
```

**Option C: Check System Clock**
```bash
# Sync system time
sudo ntpdate -s time.nist.gov
# or
sudo date -s "$(curl -I --silent --show-error --location https://google.com | grep "date:" | awk '{print $2, $3, $4, $5, $6, $7}' | head -1)"
```

---

### Problem: "401 Unauthorized" - Vertex AI

**Symptoms:**
```
Status: 401
Error: Unauthorized
```

**Solutions:**

1. **Verify API Key Format:**
```bash
# Check key exists and is valid
gcloud auth list
gcloud config get-value project
```

2. **Enable Vertex AI API:**
```bash
gcloud services enable aiplatform.googleapis.com
```

3. **Check IAM Roles:**
```bash
gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/aiplatform.user"
```

4. **Use Service Account:**
```bash
# Create key as described in BigQuery section
gcloud iam service-accounts keys create vertex-key.json \
  --iam-account=mo-ai-backend@PROJECT_ID.iam.gserviceaccount.com

# Use in Python
from google.oauth2 import service_account
credentials = service_account.Credentials.from_service_account_file(
    "vertex-key.json"
)
```

---

## 2. Connection Issues

### Problem: "Network timeout" - Cloud Services

**Symptoms:**
```
ConnectionError: HTTPConnectionPool timed out
ConnectTimeout: Connection refused
```

**Solutions:**

1. **Check Network Connectivity:**
```bash
# Test endpoint reachability
curl -I https://bigquery.googleapis.com
curl -I https://aiplatform.googleapis.com
ping 8.8.8.8

# DNS resolution
nslookup bigquery.googleapis.com
dig bigquery.googleapis.com
```

2. **Check Firewall Rules:**
```bash
# Cloud Run firewall
gcloud compute firewall-rules list
gcloud compute firewall-rules create allow-mo-ai --allow=tcp:8080

# Local firewall (macOS)
sudo pfctl -f /etc/pf.conf
```

3. **Increase Timeout:**
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(connect=5, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

response = session.get(url, timeout=30)
```

### Problem: "Tilda API unreachable"

**Symptoms:**
```
HTTPSConnectionPool(host='api.tildacdn.com', port=443): 
Connection refused
```

**Solutions:**

1. **Verify API Endpoint:**
```bash
# Check if API is up
curl -I https://api.tildacdn.com/v1/getprojectslist

# Check DNS
nslookup api.tildacdn.com

# Get IP
dig api.tildacdn.com
```

2. **Update Tilda Configuration:**
```python
# In acrobat_project_config.py
TILDA_API_ENDPOINT = "https://api.tildacdn.com/v1"
TILDA_PUBLIC_KEY = "your_key"
TILDA_SECRET_KEY = "your_secret"

# Test connection
response = requests.get(
    f"{TILDA_API_ENDPOINT}/getprojectslist",
    params={
        "publickey": TILDA_PUBLIC_KEY,
        "secretkey": TILDA_SECRET_KEY
    },
    timeout=10
)
```

3. **Use Proxy (if needed):**
```python
proxies = {
    "https": "https://proxy.example.com:8080"
}
response = requests.get(url, proxies=proxies)
```

---

## 3. Performance Issues

### Problem: "Slow response times"

**Symptoms:**
```
Response time: 5000ms+
API timeout after 30s
```

**Solutions:**

1. **Enable Caching:**
```python
from functools import lru_cache
import redis

# In-memory cache
@lru_cache(maxsize=128)
def get_lead_score(lead_id):
    return calculate_score(lead_id)

# Redis cache
redis_client = redis.Redis(host='localhost', port=6379)

def get_cached_result(key):
    result = redis_client.get(key)
    if result:
        return json.loads(result)
    return None
```

2. **Add Pagination:**
```bash
# Bad: Loading all data
curl "http://localhost:8080/api/analytics/leads"

# Good: Paginate results
curl "http://localhost:8080/api/analytics/leads?page=1&page_size=100"
```

3. **Optimize Queries:**
```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_lead_status ON leads(status);
CREATE INDEX idx_agent_id ON leads(agent_id);

-- Use LIMIT clause
SELECT * FROM leads LIMIT 1000;

-- Partition large tables
CREATE TABLE leads_2025
PARTITION BY DATE(created_date)
AS SELECT * FROM leads WHERE YEAR(created_date) = 2025;
```

4. **Monitor Performance:**
```bash
# Cloud Trace
gcloud trace create --display-name="MO AI Backend"

# Cloud Profiler
gcloud profiler create --display-name="mo-ai-profiler"

# View metrics
gcloud monitoring metrics list
```

---

## 4. Deployment Issues

### Problem: "Deployment fails on Vercel"

**Symptoms:**
```
Build failed
Function error: Cannot find module
```

**Solutions:**

1. **Check dependencies:**
```bash
# Verify package.json
cat package.json

# Check node_modules
npm install

# Verify all packages installed
npm ls
```

2. **Check environment variables:**
```bash
# List env vars
vercel env ls

# Add missing vars
vercel env add GEMINI_API_KEY
vercel env add GOOGLE_APPLICATION_CREDENTIALS
```

3. **Check buildpack:**
```bash
# Verify correct buildpack for your stack
vercel projects inspect

# Switch Python runtime
vercel env add PYTHON_VERSION 3.11
```

4. **View build logs:**
```bash
vercel logs --scope=your-scope
```

### Problem: "Cloud Run deployment fails"

**Symptoms:**
```
Error: failed to build image
docker: permission denied
```

**Solutions:**

1. **Enable Cloud Build:**
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Grant permissions
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:cloud-build@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"
```

2. **Check Dockerfile:**
```bash
# Validate Dockerfile
docker build . --dry-run

# Build locally first
docker build -t mo-ai-backend:test .

# Run locally
docker run -p 8080:8080 mo-ai-backend:test
```

3. **Use gcloud to deploy:**
```bash
gcloud run deploy mo-ai-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## 5. Data Issues

### Problem: "BigQuery data not syncing"

**Symptoms:**
```
No data returned from query
Table not found error
```

**Solutions:**

1. **Verify table exists:**
```bash
# List datasets
bq ls

# List tables
bq ls -t dataset_id

# Check table schema
bq show --schema dataset_id.table_id
```

2. **Check permissions:**
```bash
bq query --use_legacy_sql=false '
SELECT
  project_id,
  dataset_id,
  table_id
FROM `region-us`.INFORMATION_SCHEMA.TABLES
WHERE project_id = "aimo-460701"
'
```

3. **Verify data pipeline:**
```python
# Test data import
from google.cloud import bigquery

client = bigquery.Client()
query_job = client.query(
    "SELECT COUNT(*) FROM `aimo-460701.masterdata_raw.leads`"
)
print(query_job.result().to_dataframe())
```

4. **Monitor data freshness:**
```bash
# Check last update time
bq show -j dataset_id.table_id | grep LAST_MODIFIED
```

---

## 6. Model Issues

### Problem: "Acrobat ML models not responding"

**Symptoms:**
```
Model endpoint returns 500 error
Predictions have low confidence
```

**Solutions:**

1. **Check model status:**
```bash
# List deployed models
gcloud ai models list --region=us-central1

# Check model details
gcloud ai models describe MODEL_ID --region=us-central1
```

2. **Verify model endpoint:**
```python
from google.cloud import aiplatform

aiplatform.init(project="alert-acrobat-477200-g9", location="us-central1")

endpoint = aiplatform.Endpoint("projects/PROJ/locations/us-central1/endpoints/ENDPOINT_ID")

# Test prediction
prediction = endpoint.predict(instances=[{"property_value": 750000}])
print(prediction)
```

3. **Check input format:**
```python
# Verify input matches training data format
# Training data shape vs prediction input shape must match

import json

test_data = {
    "instances": [
        {
            "square_feet": 2500,
            "bedrooms": 4,
            "bathrooms": 2,
            "year_built": 2005,
            "zip_code": "10001"
        }
    ]
}

print(json.dumps(test_data, indent=2))
```

4. **Retrain model if needed:**
```bash
# Create training pipeline
gcloud ai custom-jobs create \
  --display-name="mo-ai-retrain" \
  --config=training-config.yaml
```

---

## 7. Security Issues

### Problem: "Suspicious activity detected"

**Symptoms:**
```
Multiple failed authentication attempts
Unusual API usage patterns
Rate limit exceeded
```

**Solutions:**

1. **Check audit logs:**
```bash
# View admin logs
gcloud logging read "protoPayload.methodName=google.iam.admin.v1.CreateServiceAccountKey" \
  --limit 10 \
  --format json
```

2. **Rotate compromised keys:**
```bash
# List keys
gcloud iam service-accounts keys list \
  --iam-account=mo-ai-backend@PROJECT_ID.iam.gserviceaccount.com

# Delete compromised key
gcloud iam service-accounts keys delete KEY_ID \
  --iam-account=mo-ai-backend@PROJECT_ID.iam.gserviceaccount.com

# Create new key
gcloud iam service-accounts keys create new-key.json \
  --iam-account=mo-ai-backend@PROJECT_ID.iam.gserviceaccount.com
```

3. **Enable monitoring:**
```bash
# Enable Cloud Security Command Center
gcloud scc activate

# Create alert policy
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Security Alert"
```

---

## Health Check Commands

Run these to verify system health:

```bash
#!/bin/bash

echo "🏥 MO AI System Health Check"
echo "=============================="

# 1. Check API health
echo ""
echo "1️⃣ API Health:"
curl -s http://localhost:8080/health | json_pp

# 2. Check Gemini API
echo ""
echo "2️⃣ Gemini API:"
curl -s -X POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key=$GEMINI_API_KEY \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"hello"}]}]}' | json_pp

# 3. Check BigQuery
echo ""
echo "3️⃣ BigQuery:"
bq query --use_legacy_sql=false 'SELECT COUNT(*) FROM `aimo-460701.masterdata_raw.leads`'

# 4. Check Vertex AI
echo ""
echo "4️⃣ Vertex AI:"
gcloud ai models list --region=us-central1

# 5. Check Cloud Run
echo ""
echo "5️⃣ Cloud Run:"
gcloud run services describe mo-ai-backend --region=us-central1

# 6. Check Service Account
echo ""
echo "6️⃣ Service Account:"
gcloud iam service-accounts list

echo ""
echo "✅ Health check complete!"
```

---

## Debug Mode

Enable verbose logging:

```python
# In real_ai_backend.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Use throughout code
logger.debug(f"Command: {command}")
logger.info(f"Executing: {function_name}")
logger.error(f"Error: {error}")
```

---

## Getting Help

### Resources
1. 📖 API Reference: `API_REFERENCE.md`
2. 🚀 Deployment Guide: `CLOUD_DEPLOYMENT_GUIDE.md`
3. 📊 Test Report: `CLOUD_API_TEST_REPORT.md`
4. 🔧 Integration Guide: `ACROBAT_INTEGRATION.md`

### Support Channels
- **Email**: support@moai.dev
- **Slack**: #mo-ai-support
- **GitHub Issues**: mo-ai/issues
- **Documentation**: https://moai.dev/docs

### Escalation Path
1. Check this guide
2. Check logs and monitoring
3. Contact support team
4. Open GitHub issue with logs/details

---

## Emergency Contacts

**On-Call Support:**
- Production Issues: +1 (555) 123-4567
- Security Issues: security@moai.dev
- Infrastructure: infrastructure@moai.dev

**SLA Response Times:**
- Critical: 15 minutes
- High: 1 hour
- Medium: 4 hours
- Low: 24 hours

---

**Last Updated:** November 4, 2025  
**Version:** 1.0.0  
**Status:** Active
