#!/bin/bash

# MO AI Cloud Deployment Script
# This script automates the cloud deployment process

set -e

echo "🚀 MO AI Cloud Deployment Script"
echo "================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCLOUD_PROJECT:-alert-acrobat-477200-g9}"
SERVICE_NAME="mo-ai-backend"
REGION="us-central1"
RUNTIME="python39"

# Functions
print_step() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    echo ""
    echo "Checking prerequisites..."
    
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI not found. Please install Google Cloud SDK."
        exit 1
    fi
    print_step "gcloud CLI found"
    
    if ! command -v git &> /dev/null; then
        print_error "git not found. Please install git."
        exit 1
    fi
    print_step "git found"
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3.9 or higher."
        exit 1
    fi
    print_step "Python 3 found"
    
    # Check gcloud auth
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
        print_error "Not authenticated with gcloud. Run: gcloud auth login"
        exit 1
    fi
    print_step "gcloud authentication verified"
}

# Create service account
create_service_account() {
    echo ""
    echo "Setting up Google Cloud service account..."
    
    SA_NAME="mo-ai-backend"
    SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
    
    # Check if service account already exists
    if gcloud iam service-accounts describe $SA_EMAIL --project=$PROJECT_ID &> /dev/null; then
        print_step "Service account already exists: $SA_EMAIL"
    else
        print_step "Creating service account: $SA_NAME"
        gcloud iam service-accounts create $SA_NAME \
            --display-name="MO AI Backend Service" \
            --project=$PROJECT_ID
        print_step "Service account created"
    fi
    
    # Create and download key
    print_step "Creating service account key..."
    gcloud iam service-accounts keys create mo-ai-backend-key.json \
        --iam-account=$SA_EMAIL \
        --project=$PROJECT_ID
    print_step "Key created and saved to mo-ai-backend-key.json"
    
    # Grant roles
    echo ""
    echo "Granting IAM roles..."
    
    ROLES=(
        "roles/bigquery.dataEditor"
        "roles/aiplatform.user"
        "roles/storage.admin"
        "roles/cloudfunctions.developer"
    )
    
    for ROLE in "${ROLES[@]}"; do
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="serviceAccount:$SA_EMAIL" \
            --role="$ROLE" \
            --project=$PROJECT_ID \
            --quiet
        print_step "Assigned role: $ROLE"
    done
}

# Enable required APIs
enable_apis() {
    echo ""
    echo "Enabling required APIs..."
    
    APIs=(
        "bigquery.googleapis.com"
        "aiplatform.googleapis.com"
        "run.googleapis.com"
        "cloudfunctions.googleapis.com"
        "storage.googleapis.com"
        "cloudbuild.googleapis.com"
    )
    
    for API in "${APIs[@]}"; do
        print_step "Enabling $API"
        gcloud services enable $API --project=$PROJECT_ID
    done
}

# Deploy to Cloud Run
deploy_cloud_run() {
    echo ""
    echo "Deploying to Cloud Run..."
    
    # Build image
    print_step "Building Docker image..."
    gcloud builds submit \
        --tag gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
        --project=$PROJECT_ID
    
    # Deploy
    print_step "Deploying to Cloud Run..."
    gcloud run deploy $SERVICE_NAME \
        --image gcr.io/$PROJECT_ID/$SERVICE_NAME:latest \
        --platform managed \
        --region $REGION \
        --no-allow-unauthenticated \
        --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
        --service-account "mo-ai-backend@${PROJECT_ID}.iam.gserviceaccount.com" \
        --project=$PROJECT_ID \
        --memory 2Gi \
        --cpu 2 \
        --timeout 3600
    
    print_step "Deployment complete!"
    
    # Get service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
        --platform managed \
        --region $REGION \
        --format 'value(status.url)' \
        --project=$PROJECT_ID)
    
    echo ""
    echo "Service URL: $SERVICE_URL"
}

# Deploy Cloud Functions (alternative)
deploy_cloud_functions() {
    echo ""
    echo "Deploying to Cloud Functions..."
    
    gcloud functions deploy mo_ai_function \
        --runtime $RUNTIME \
        --trigger-http \
        --allow-unauthenticated \
        --region $REGION \
        --entry-point=execute_command \
        --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
        --service-account "mo-ai-backend@${PROJECT_ID}.iam.gserviceaccount.com" \
        --project=$PROJECT_ID
    
    print_step "Cloud Function deployed"
}

# Test deployment
test_deployment() {
    echo ""
    echo "Testing deployment..."
    
    # Get service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
        --platform managed \
        --region $REGION \
        --format 'value(status.url)' \
        --project=$PROJECT_ID)
    
    # Generate auth token
    AUTH_TOKEN=$(gcloud auth print-access-token)
    
    # Test health endpoint
    print_step "Testing health endpoint..."
    HEALTH_TEST=$(curl -s -H "Authorization: Bearer $AUTH_TOKEN" \
        "$SERVICE_URL/health" | python3 -m json.tool)
    
    if echo "$HEALTH_TEST" | grep -q "healthy"; then
        print_step "Health check passed ✓"
    else
        print_warning "Health check may have issues"
    fi
    
    # Test API endpoint
    print_step "Testing API endpoint..."
    API_TEST=$(curl -s -X POST -H "Authorization: Bearer $AUTH_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"command": "check acrobat project status"}' \
        "$SERVICE_URL/api/execute" | python3 -m json.tool)
    
    echo ""
    echo "API Response:"
    echo "$API_TEST"
}

# Setup Vercel (frontend)
setup_vercel() {
    echo ""
    echo "Setting up Vercel for frontend..."
    
    if command -v vercel &> /dev/null; then
        print_step "Vercel CLI found"
        
        echo ""
        echo "Adding environment variables to Vercel..."
        echo "Please add these in the Vercel dashboard or via: vercel env add"
        echo ""
        echo "GEMINI_API_KEY=AIzaSyBQWBs2HYmllkp5t37QEwIhF0viJ8vWMZs"
        echo "GOOGLE_APPLICATION_CREDENTIALS=/path/to/key"
        echo "BIGQUERY_PROJECT=aimo-460701"
        echo "ACROBAT_PROJECT_ID=alert-acrobat-477200-g9"
        echo ""
        
        read -p "Deploy to Vercel now? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            vercel --prod
            print_step "Vercel deployment complete"
        fi
    else
        print_warning "Vercel CLI not installed. Install with: npm install -g vercel"
    fi
}

# Main deployment flow
main() {
    echo ""
    echo "Starting MO AI Cloud Deployment"
    echo "Project: $PROJECT_ID"
    echo "Region: $REGION"
    echo ""
    
    # Step 1: Check prerequisites
    check_prerequisites
    
    # Step 2: Create service account
    create_service_account
    
    # Step 3: Enable APIs
    enable_apis
    
    # Step 4: Deploy to Cloud Run
    deploy_cloud_run
    
    # Step 5: Test deployment
    test_deployment
    
    # Step 6: Setup Vercel (optional)
    setup_vercel
    
    echo ""
    echo "✅ Deployment complete!"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Store mo-ai-backend-key.json securely"
    echo "   2. Set GOOGLE_APPLICATION_CREDENTIALS environment variable"
    echo "   3. Configure API keys in Vercel dashboard"
    echo "   4. Set up monitoring and alerts"
    echo "   5. Test end-to-end workflow"
    echo ""
}

# Run main function
main "$@"
