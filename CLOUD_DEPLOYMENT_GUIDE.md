# Cloud Deployment Configuration

This file contains templates for deploying MO AI to the cloud.

## Deployment Platforms

### 1. Vercel (Frontend + Serverless Functions)
### 2. Google Cloud Run (Backend API)
### 3. Firebase Hosting (Static Assets)

---

## Setup Instructions

### Google Cloud Project Setup

1. **Enable Required APIs:**
```bash
gcloud services enable \
  bigquery.googleapis.com \
  aiplatform.googleapis.com \
  run.googleapis.com \
  cloudfunctions.googleapis.com \
  storage.googleapis.com
```

2. **Create Service Account:**
```bash
gcloud iam service-accounts create mo-ai-backend \
  --display-name="MO AI Backend Service"
  
gcloud iam service-accounts keys create \
  mo-ai-backend-key.json \
  --iam-account=mo-ai-backend@$(gcloud config get-value project).iam.gserviceaccount.com
```

3. **Grant Permissions:**
```bash
PROJECT_ID=$(gcloud config get-value project)
SA_EMAIL="mo-ai-backend@${PROJECT_ID}.iam.gserviceaccount.com"

# BigQuery permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/bigquery.dataEditor"

# Vertex AI permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/aiplatform.user"

# Cloud Storage permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/storage.admin"
```

### Vercel Deployment

1. **Install Vercel CLI:**
```bash
npm install -g vercel
```

2. **Configure Environment Variables:**
```bash
vercel env add GEMINI_API_KEY
vercel env add GOOGLE_APPLICATION_CREDENTIALS
vercel env add BIGQUERY_PROJECT
vercel env add ACROBAT_PROJECT_ID
```

3. **Deploy:**
```bash
vercel --prod
```

### Firebase Deployment

1. **Install Firebase CLI:**
```bash
npm install -g firebase-tools
```

2. **Initialize Firebase:**
```bash
firebase init hosting
firebase init functions
```

3. **Deploy:**
```bash
firebase deploy
```

---

## Environment Variables Template

Create a `.env.production` file:

```
# Google Cloud
GOOGLE_CLOUD_PROJECT=alert-acrobat-477200-g9
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# API Keys
GEMINI_API_KEY=AIzaSyBQWBs2HYmllkp5t37QEwIhF0viJ8vWMZs
VERTEX_AI_KEY=AIzaSyBQWBs2HYmllkp5t37QEwIhF0viJ8vWMZs

# BigQuery
BIGQUERY_PROJECT=aimo-460701
BIGQUERY_DATASET=masterdata_leads
BIGQUERY_TABLE=leads_data

# Vertex AI
VERTEX_AI_REGION=us-central1
VERTEX_AI_ENDPOINT=projects/alert-acrobat-477200-g9/locations/us-central1

# Acrobat Project
ACROBAT_PROJECT_ID=alert-acrobat-477200-g9
ACROBAT_REGION=us-central1

# Tilda Integration
TILDA_PUBLIC_KEY=b9j7w8eka0dwsizitkix
TILDA_SECRET_KEY=f6e8020a209425c3f895

# Application
NODE_ENV=production
PORT=8080
LOG_LEVEL=info
```

---

## Docker Deployment (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD ["python", "real_ai_backend.py"]
```

Build and push:

```bash
docker build -t mo-ai-backend:latest .
docker tag mo-ai-backend:latest gcr.io/$PROJECT_ID/mo-ai-backend:latest
docker push gcr.io/$PROJECT_ID/mo-ai-backend:latest

# Deploy to Cloud Run
gcloud run deploy mo-ai-backend \
  --image gcr.io/$PROJECT_ID/mo-ai-backend:latest \
  --platform managed \
  --region us-central1
```

---

## Monitoring & Logging

### Cloud Logging

```bash
# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=mo-ai-backend" \
  --limit 100 \
  --format json

# Create alert
gcloud alpha monitoring policies create \
  --notification-channels=<CHANNEL_ID> \
  --display-name="MO AI Backend Error Alert" \
  --condition-display-name="High Error Rate"
```

### Cloud Monitoring

```bash
# Create dashboard
gcloud monitoring dashboards create --config-from-file=dashboard.json
```

---

## Deployment Validation

After deployment, test:

```bash
# Test health endpoint
curl https://mo-ai-backend.run.app/health

# Test API endpoint
curl -X POST https://mo-ai-backend.run.app/api/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "check acrobat project status"}'

# Test BigQuery access
curl https://mo-ai-backend.run.app/api/bigquery/status

# Test Gemini API
curl https://mo-ai-backend.run.app/api/gemini/test
```

---

## Production Checklist

- [ ] Service account created and key stored securely
- [ ] All APIs enabled in GCP
- [ ] IAM roles assigned
- [ ] Environment variables configured in deployment platform
- [ ] API keys rotated
- [ ] CORS configured properly
- [ ] Rate limiting enabled
- [ ] Monitoring and alerts set up
- [ ] Error logging configured
- [ ] Health checks passing
- [ ] Load testing completed
- [ ] Security audit passed

---

## Rollback Procedure

If deployment fails:

```bash
# Check deployment status
vercel deployments

# Revert to previous version
vercel rollback

# Or manually redeploy:
vercel --prod --force
```

---

## Support & Documentation

- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
