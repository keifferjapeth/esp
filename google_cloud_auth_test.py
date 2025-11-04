#!/usr/bin/env python3
"""
Google Cloud Service Account Authentication Helper
Properly handles OAuth2 authentication for Vertex AI and BigQuery
"""

import json
import tempfile
import os
from google.oauth2 import service_account
from google.cloud import aiplatform
from google.cloud import bigquery
import requests

class GoogleCloudAuthenticator:
    def __init__(self):
        # Service account credentials from masterdata/ai_config.py
        self.service_account_info = {
            "type": "service_account",
            "project_id": "aimo-460701",
            "private_key_id": "c5cc878b8c6eb3839af861e8185e4aa6ca0ecf1f",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDXFvHv4FkQetX0\n7OZu0oLtcEpxJciA6Iy0fbmYcJzxcSDflsFvDK2Pa2L6JWreSIek70XYuVzUY007\nqsrNjyW//52FXEQOydsLi1zikLwKFwc7qqzv2iyYVjpq56tgPgYAZMiLuaNJL5RA\nMX6EA+HdYIqNt79K4SBaAmNNuzEnINdO4Fm/0RRDfAb9ZhXdrTFKl+KCNSIjNU/5\ncHJFknPFE75t8egSsQq0Qcwe+9uqJKLeSWdcwnoynfJvU+mmjdyOxBk8cu/ZuJWn\niOSZ0gPKxANI40fC1rLuNkpY2yNWYRDgSmuTa0geBtZCyjw/En/OYyY5A8iqdKdi\n2LfeLwzLAgMBAAECggEAUUhYBKUdM1egTG9MQ7wlA1LIpwq2w1RefAT5Is0H2kw8\ntpIzpmI9orHb1RlX0gnJzQApPpYKKS8frDlGa7k5dF3GavPrukT5FNtFLk+w6AU8\n1AUTVo72BFmtuOG0x2mY/gQYL4lnVgx3c2zg2UXYUL8fjR/P2B3MiodVfLYNhLG4\nm06EOjIx9eX1R8/DVAjHHPkGz9LbFJm8MslfgSFQebKLFM2GrKMEc4M3Luf0gCYa\nXY8T4VQWvM3jJvhu8LSJm8D4bL2Gns8PaZvfUntVR7JaGqmxuRCHsAzsTFgK2Vui\nkeJA+CCLl5pcvIlXc5yTz748j8/hLMenSdVmxiTtiQKBgQDuboN+nI9FiQ6lVw2w\nk4XoshOkU1lvl7U+AbKaH2Aw/+HaUxCQZTXsVNn4WxjK0D/1qqh5upJomzWGfL/z\nDbrzrpahqabW/bkbeRFRz01b5V8cjnUfnZxCcUKR6lndujKcX80vZYSo2cNSj9LA\n6M7PGqmkD8UrW8lW5t7Ylp286QKBgQDm8CKQDljXRToqzSH6PHYrqUP3oz7103B5\nc6pom4c/LZ/yTcgMmLPW6nTJhoxqYUpjVHPxulBG1gklINKieLlVdUQTkLBpgGoQ\nvzzeIrqISV98q4RJ3Z/akjqJo/pBBY1m81R8Ggn/Ju3YymIjuEEp66kMrOrQ9mhA\nDJ+p/9cbkwKBgQCHTyBAkgicpZMyMZ0LQC0WSTjsYIC425d3gO8il/u20wARLmKQ\nD1/yppSsZMZFErm5aQgDTOYZhztw/wrPnFMkR0gkpmqQR5ztAl/Z1ZNJO3omcpH1\nRzSOYEgvFpe5RRnDtHp1E1+dkzdNe2FXKMd0sOTkvi5e1NAGCS8eKxuJQQKBgCyy\nFT5kSHWBhHx8LzNLOGPC4tCu26SgQ4h+BmEwmMB1iBtRSoKFm2jg/7FxRQPhyI/o\n7HfAY4ESM7rn21xumRAdHgvbWQlSPTT4jkM/3XI7ISvz1iqlpiabXpD9F5Y2COP/\n/D34nC6xzh7DLLNVGeePIKy/WsMOraaXyt8QEQXZAoGBAMJScYyYPW5GZX7Yr17Q\nIQp77GN/U9IFdnQU6Nfj+Kc4+62HwIG7YV+EQ9VA+xYURCIBs2EhCIGKxtI6+vMH\n4h5HVkKPz/t6BH7GRGNz0ZI5oyqfIQxNHYLd/IiHMoXsVGLlDr52L61vsabheKJX\n+Ml/NrOm9ejkjUIx1XtXM5St\n-----END PRIVATE KEY-----\n",
            "client_email": "gpt-automator-gemini@aimo-460701.iam.gserviceaccount.com",
            "client_id": "101279335386719976003",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/gpt-automator-gemini%40aimo-460701.iam.gserviceaccount.com",
            "universe_domain": "googleapis.com"
        }
        
        # Project configurations
        self.service_account_project = "aimo-460701"
        self.vertex_ai_project = "alert-acrobat-477200-g9"
        
        # Initialize credentials
        self.credentials = None
        self._initialize_credentials()
    
    def _initialize_credentials(self):
        """Initialize service account credentials"""
        try:
            self.credentials = service_account.Credentials.from_service_account_info(
                self.service_account_info,
                scopes=[
                    'https://www.googleapis.com/auth/cloud-platform',
                    'https://www.googleapis.com/auth/bigquery',
                    'https://www.googleapis.com/auth/aiplatform'
                ]
            )
            print("✅ Service account credentials initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize credentials: {e}")
            return False
    
    def test_vertex_ai_access(self):
        """Test Vertex AI access with proper OAuth2 authentication"""
        try:
            # Initialize Vertex AI client
            aiplatform.init(
                project=self.vertex_ai_project,
                location="us-central1",
                credentials=self.credentials
            )
            
            # Try to list models (this requires proper authentication)
            from google.cloud.aiplatform_v1 import ModelServiceClient
            client = ModelServiceClient(credentials=self.credentials)
            
            parent = f"projects/{self.vertex_ai_project}/locations/us-central1"
            response = client.list_models(parent=parent)
            
            models = list(response)
            print(f"✅ Vertex AI Access: Found {len(models)} models in {self.vertex_ai_project}")
            
            # List some model names
            if models:
                for i, model in enumerate(models[:3]):  # Show first 3
                    print(f"  📍 Model {i+1}: {model.name}")
            
            return {"success": True, "models_count": len(models), "project": self.vertex_ai_project}
            
        except Exception as e:
            print(f"❌ Vertex AI Access Failed: {e}")
            return {"success": False, "error": str(e)}
    
    def test_bigquery_access(self):
        """Test BigQuery access with proper OAuth2 authentication"""
        try:
            # Initialize BigQuery client
            client = bigquery.Client(
                project=self.service_account_project,
                credentials=self.credentials
            )
            
            # List datasets
            datasets = list(client.list_datasets())
            print(f"✅ BigQuery Access: Found {len(datasets)} datasets in {self.service_account_project}")
            
            # Show dataset names
            if datasets:
                for i, dataset in enumerate(datasets[:3]):  # Show first 3
                    print(f"  📊 Dataset {i+1}: {dataset.dataset_id}")
            
            # Test a simple query
            query = "SELECT 1 as test_value"
            query_job = client.query(query)
            results = list(query_job)
            
            print(f"✅ BigQuery Query Test: Success - Got {len(results)} rows")
            
            return {"success": True, "datasets_count": len(datasets), "project": self.service_account_project}
            
        except Exception as e:
            print(f"❌ BigQuery Access Failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_access_token(self):
        """Get OAuth2 access token for API calls"""
        try:
            # Refresh token if needed
            if not self.credentials.valid:
                self.credentials.refresh(requests.Request())
            
            return self.credentials.token
        except Exception as e:
            print(f"❌ Failed to get access token: {e}")
            return None
    
    def test_gemini_api(self):
        """Test Gemini API with service account"""
        try:
            import google.generativeai as genai
            
            # Configure with service account
            genai.configure(credentials=self.credentials)
            
            # Test with a simple prompt
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Say 'Hello from Gemini API'")
            
            print(f"✅ Gemini API Test: {response.text}")
            return {"success": True, "response": response.text}
            
        except Exception as e:
            print(f"❌ Gemini API Failed: {e}")
            return {"success": False, "error": str(e)}

def main():
    """Test all Google Cloud services with proper authentication"""
    print("🔐 Google Cloud Service Account Authentication Test")
    print("=" * 60)
    
    auth = GoogleCloudAuthenticator()
    
    if not auth.credentials:
        print("❌ Failed to initialize - cannot proceed")
        return
    
    print(f"🏢 Service Account Project: {auth.service_account_project}")
    print(f"🤖 Vertex AI Project: {auth.vertex_ai_project}")
    print(f"📧 Service Account: {auth.service_account_info['client_email']}")
    print("=" * 60)
    
    # Test all services
    vertex_result = auth.test_vertex_ai_access()
    bigquery_result = auth.test_bigquery_access()
    gemini_result = auth.test_gemini_api()
    
    print("=" * 60)
    print("📊 SUMMARY:")
    print(f"Vertex AI: {'✅ SUCCESS' if vertex_result['success'] else '❌ FAILED'}")
    print(f"BigQuery: {'✅ SUCCESS' if bigquery_result['success'] else '❌ FAILED'}")
    print(f"Gemini API: {'✅ SUCCESS' if gemini_result['success'] else '❌ FAILED'}")
    
    # Show access token (first 20 chars for security)
    token = auth.get_access_token()
    if token:
        print(f"🔑 Access Token: {token[:20]}...")

if __name__ == "__main__":
    main()