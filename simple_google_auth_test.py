#!/usr/bin/env python3
"""
Simple Google Cloud API Test using Service Account
Tests authentication without requiring additional libraries
"""

import json
import time
import jwt
import requests
from typing import Dict, Any

class SimpleGoogleAuth:
    def __init__(self):
        # Service account info from masterdata/ai_config.py
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
        
        self.service_project = "aimo-460701"
        self.vertex_project = "alert-acrobat-477200-g9"
        self.access_token = None
    
    def create_jwt_assertion(self) -> str:
        """Create JWT assertion for OAuth2 flow"""
        now = int(time.time())
        
        payload = {
            'iss': self.service_account_info['client_email'],
            'scope': 'https://www.googleapis.com/auth/cloud-platform',
            'aud': self.service_account_info['token_uri'],
            'exp': now + 3600,  # 1 hour
            'iat': now
        }
        
        # Create JWT
        assertion = jwt.encode(
            payload,
            self.service_account_info['private_key'],
            algorithm='RS256'
        )
        
        return assertion
    
    def get_access_token(self) -> str:
        """Get OAuth2 access token using service account"""
        try:
            assertion = self.create_jwt_assertion()
            
            data = {
                'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                'assertion': assertion
            }
            
            response = requests.post(
                self.service_account_info['token_uri'],
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                print(f"✅ Access Token obtained: {self.access_token[:20]}...")
                return self.access_token
            else:
                print(f"❌ Failed to get access token: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Access token error: {e}")
            return None
    
    def test_vertex_ai_with_auth(self):
        """Test Vertex AI with OAuth2 token"""
        if not self.access_token:
            return {"success": False, "error": "No access token"}
        
        try:
            url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.vertex_project}/locations/us-central1/models"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                print(f"✅ Vertex AI Success: Found {len(models)} models in {self.vertex_project}")
                
                # Show first few models
                for i, model in enumerate(models[:3]):
                    model_name = model.get('name', 'Unknown')
                    print(f"  📍 Model {i+1}: {model_name.split('/')[-1]}")
                
                return {"success": True, "models_count": len(models), "project": self.vertex_project}
            else:
                print(f"❌ Vertex AI Failed: {response.status_code} - {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Vertex AI Exception: {e}")
            return {"success": False, "error": str(e)}
    
    def test_bigquery_with_auth(self):
        """Test BigQuery with OAuth2 token"""
        if not self.access_token:
            return {"success": False, "error": "No access token"}
        
        try:
            # Test datasets endpoint
            url = f"https://bigquery.googleapis.com/bigquery/v2/projects/{self.service_project}/datasets"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                datasets = data.get('datasets', [])
                print(f"✅ BigQuery Success: Found {len(datasets)} datasets in {self.service_project}")
                
                # Show first few datasets
                for i, dataset in enumerate(datasets[:3]):
                    dataset_id = dataset.get('datasetReference', {}).get('datasetId', 'Unknown')
                    print(f"  📊 Dataset {i+1}: {dataset_id}")
                
                return {"success": True, "datasets_count": len(datasets), "project": self.service_project}
            else:
                print(f"❌ BigQuery Failed: {response.status_code} - {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ BigQuery Exception: {e}")
            return {"success": False, "error": str(e)}
    
    def test_gemini_with_api_key(self):
        """Test Gemini AI with API key (doesn't need OAuth2)"""
        try:
            # Gemini AI supports API keys
            api_key = "AIzaSyBQWBs2HYmllkp5t37QEwIhF0viJ8vWMZs"
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": "Say 'Hello from Gemini API test'"
                    }]
                }]
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No response')
                print(f"✅ Gemini API Success: {text.strip()}")
                return {"success": True, "response": text.strip()}
            else:
                print(f"❌ Gemini API Failed: {response.status_code} - {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"❌ Gemini API Exception: {e}")
            return {"success": False, "error": str(e)}

def main():
    """Test all Google Cloud services"""
    print("🔐 Google Cloud API Authentication Test")
    print("=" * 60)
    
    auth = SimpleGoogleAuth()
    
    print(f"🏢 Service Account Project: {auth.service_project}")
    print(f"🤖 Vertex AI Project: {auth.vertex_project}")
    print(f"📧 Service Account: {auth.service_account_info['client_email']}")
    print("=" * 60)
    
    # Get access token
    token = auth.get_access_token()
    
    if token:
        # Test OAuth2-based services
        vertex_result = auth.test_vertex_ai_with_auth()
        bigquery_result = auth.test_bigquery_with_auth()
    else:
        vertex_result = {"success": False, "error": "No token"}
        bigquery_result = {"success": False, "error": "No token"}
    
    # Test API key-based service
    gemini_result = auth.test_gemini_with_api_key()
    
    print("=" * 60)
    print("📊 FINAL RESULTS:")
    print(f"🔑 Access Token: {'✅ SUCCESS' if token else '❌ FAILED'}")
    print(f"🤖 Vertex AI: {'✅ SUCCESS' if vertex_result['success'] else '❌ FAILED'}")
    print(f"📊 BigQuery: {'✅ SUCCESS' if bigquery_result['success'] else '❌ FAILED'}")
    print(f"🧠 Gemini API: {'✅ SUCCESS' if gemini_result['success'] else '❌ FAILED'}")
    
    # Summary for API integration
    working_services = []
    if token: working_services.append("OAuth2 Authentication")
    if vertex_result['success']: working_services.append("Vertex AI")
    if bigquery_result['success']: working_services.append("BigQuery") 
    if gemini_result['success']: working_services.append("Gemini API")
    
    print("=" * 60)
    print(f"🎯 WORKING SERVICES ({len(working_services)}/4):")
    for service in working_services:
        print(f"  ✅ {service}")
    
    if len(working_services) >= 3:
        print("🚀 READY FOR INTEGRATION: Most services are working!")
    else:
        print("⚠️  PARTIAL SUCCESS: Some services need attention")

if __name__ == "__main__":
    main()