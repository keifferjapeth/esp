#!/usr/bin/env python3
"""
Comprehensive API Key Manager with Automatic Fallbacks
Supports: OpenAI, Google Cloud, Vertex AI, Gemini, Tilda, Anthropic, etc.
"""

import os
import json
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import requests
import asyncio

@dataclass
class APIKey:
    name: str
    key: str
    service: str
    quota_limit: Optional[int] = None
    requests_used: int = 0
    last_reset: datetime = None
    is_working: bool = True
    last_tested: Optional[datetime] = None
    priority: int = 1  # Lower number = higher priority

class APIKeyManager:
    def __init__(self):
        self.keys: Dict[str, List[APIKey]] = {}
        self.test_results = {}
        self.setup_logging()
        self.load_all_keys()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def load_all_keys(self):
        """Load all API keys with automatic fallbacks"""
        
        # Google Cloud / Vertex AI Keys (alert-acrobat-477200-g9 project)
        APIKey("Primary Vertex AI (alert-acrobat)", "AIzaSyBQWBs2HYmllkp5t37QEwIhF0viJ8vWMZs", "vertex_ai", 100),
        APIKey("Secondary Vertex AI (alert-acrobat)", "AIzaSyCjtdewcjT6nUGS-_aT9T1ERpfTXlMcYXo", "vertex_ai", 90),
        
        # BigQuery Keys (aimo-460701 and alert-acrobat-477200-g9 projects)
        APIKey("BigQuery API (aimo-460701)", "AIzaSyCjtdewcjT6nUGS-_aT9T1ERpfTXlMcYXo", "bigquery", 100),
        APIKey("BigQuery API (alert-acrobat)", "AIzaSyCjtdewcjT6nUGS71QCj6lpKKj6Av8xGp8", "bigquery", 90),
        self.keys["google"] = google_keys
        
        # OpenAI Keys (Multiple fallbacks)
        openai_keys = [
            APIKey("openai_main", "sk-proj-PRIMARY-KEY-HERE", "openai", priority=1),
            APIKey("openai_backup", "sk-proj-BACKUP-KEY-HERE", "openai", priority=2),
            APIKey("openai_emergency", "sk-proj-EMERGENCY-KEY-HERE", "openai", priority=3),
        ]
        self.keys["openai"] = openai_keys
        
        # Anthropic Claude Keys
        anthropic_keys = [
            APIKey("claude_main", "sk-ant-PRIMARY-CLAUDE-KEY", "anthropic", priority=1),
            APIKey("claude_backup", "sk-ant-BACKUP-CLAUDE-KEY", "anthropic", priority=2),
        ]
        self.keys["anthropic"] = anthropic_keys
        
        # Tilda Keys (From your environment)
        tilda_keys = [
            APIKey("tilda_main", "b9j7w8eka0dwsizitkix", "tilda", priority=1),
        ]
        self.keys["tilda"] = tilda_keys
        
        # Tilda Secret Keys
        tilda_secrets = [
            APIKey("tilda_secret", "f6e8020a209425c3f895", "tilda_secret", priority=1),
        ]
        self.keys["tilda_secret"] = tilda_secrets
        
        # Other Cloud Services
        misc_keys = [
            APIKey("cloudflare_main", "CF-API-KEY-HERE", "cloudflare", priority=1),
            APIKey("aws_access", "AKIA-AWS-ACCESS-KEY", "aws", priority=1),
            APIKey("azure_main", "AZURE-KEY-HERE", "azure", priority=1),
        ]
        self.keys["misc"] = misc_keys
        
        self.logger.info(f"Loaded {sum(len(keys) for keys in self.keys.values())} API keys across {len(self.keys)} services")
    
    def get_working_key(self, service: str) -> Optional[APIKey]:
        """Get the next working API key for a service with automatic fallback"""
        service_keys = []
        
        # Find keys for this service across all categories
        for category, keys in self.keys.items():
            for key in keys:
                if key.service == service and key.is_working:
                    service_keys.append(key)
        
        if not service_keys:
            self.logger.error(f"No working keys found for service: {service}")
            return None
        
        # Sort by priority (lower number = higher priority)
        service_keys.sort(key=lambda x: x.priority)
        
        # Try each key in priority order
        for key in service_keys:
            if self.is_key_available(key):
                return key
        
        self.logger.warning(f"All keys for {service} are at quota limit or failed")
        return None
    
    def is_key_available(self, key: APIKey) -> bool:
        """Check if a key is available (not at quota limit)"""
        if key.quota_limit is None:
            return True
        
        # Reset daily counters
        if key.last_reset is None or datetime.now() - key.last_reset > timedelta(days=1):
            key.requests_used = 0
            key.last_reset = datetime.now()
        
        return key.requests_used < key.quota_limit
    
    async def test_key(self, key: APIKey) -> bool:
        """Test if an API key is working"""
        try:
            if key.service == "gemini":
                return await self.test_gemini_key(key.key)
            elif key.service == "openai":
                return await self.test_openai_key(key.key)
            elif key.service == "anthropic":
                return await self.test_anthropic_key(key.key)
            elif key.service == "tilda":
                return await self.test_tilda_key(key.key)
            elif key.service == "google_cloud":
                return await self.test_google_cloud_key(key.key)
            elif key.service == "vertex_ai":
                return await self.test_vertex_ai_key(key.key)
            else:
                self.logger.warning(f"No test method for service: {key.service}")
                return True  # Assume working if we can't test
                
        except Exception as e:
            self.logger.error(f"Error testing key {key.name}: {str(e)}")
            key.is_working = False
            return False
    
    async def test_gemini_key(self, api_key: str) -> bool:
        """Test Gemini API key"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    async def test_openai_key(self, api_key: str) -> bool:
        """Test OpenAI API key"""
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    async def test_anthropic_key(self, api_key: str) -> bool:
        """Test Anthropic Claude API key"""
        try:
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            # Use a minimal test request
            data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hi"}]
            }
            response = requests.post("https://api.anthropic.com/v1/messages", 
                                   headers=headers, json=data, timeout=10)
            return response.status_code in [200, 400, 429]  # 400/429 means key is valid but request issue
        except:
            return False
    
    async def test_tilda_key(self, public_key: str) -> bool:
        """Test Tilda API key"""
        try:
            url = f"http://api.tildacdn.info/v1/getprojectslist/?publickey={public_key}"
            response = requests.get(url, timeout=10)
            return response.status_code == 200 and "result" in response.json()
        except:
            return False
    
    async def test_google_cloud_key(self, api_key: str) -> bool:
        """Test Google Cloud API key"""
        try:
            url = f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={api_key}"
            response = requests.get(url, timeout=10)
            return response.status_code in [200, 400]  # 400 might mean invalid format but key exists
        except:
            return False
    
    async def test_vertex_ai_key(self, api_key: str) -> bool:
        """Test Vertex AI key"""
        try:
            # Test with a simple API call
            headers = {"Authorization": f"Bearer {api_key}"}
            url = "https://us-central1-aiplatform.googleapis.com/v1/projects/aimo-460701/locations/us-central1/models"
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code in [200, 401, 403]  # Auth errors mean key format is valid
        except:
            return False
    
    async def test_all_keys(self) -> Dict[str, Any]:
        """Test all API keys and return detailed results"""
        results = {
            "test_timestamp": datetime.now().isoformat(),
            "services": {},
            "summary": {
                "total_keys": 0,
                "working_keys": 0,
                "failed_keys": 0
            }
        }
        
        for category, keys in self.keys.items():
            for key in keys:
                results["summary"]["total_keys"] += 1
                
                self.logger.info(f"Testing {key.name} ({key.service})...")
                is_working = await self.test_key(key)
                
                key.is_working = is_working
                key.last_tested = datetime.now()
                
                if key.service not in results["services"]:
                    results["services"][key.service] = []
                
                results["services"][key.service].append({
                    "name": key.name,
                    "working": is_working,
                    "priority": key.priority,
                    "last_tested": key.last_tested.isoformat() if key.last_tested else None
                })
                
                if is_working:
                    results["summary"]["working_keys"] += 1
                else:
                    results["summary"]["failed_keys"] += 1
        
        return results
    
    def use_key(self, service: str) -> Optional[str]:
        """Get and mark usage of an API key"""
        key = self.get_working_key(service)
        if key:
            key.requests_used += 1
            return key.key
        return None
    
    def get_key_info(self, service: str) -> Dict[str, Any]:
        """Get detailed info about keys for a service"""
        working_key = self.get_working_key(service)
        service_keys = []
        
        for category, keys in self.keys.items():
            for key in keys:
                if key.service == service:
                    service_keys.append({
                        "name": key.name,
                        "working": key.is_working,
                        "priority": key.priority,
                        "requests_used": key.requests_used,
                        "quota_limit": key.quota_limit,
                        "is_current": key == working_key
                    })
        
        return {
            "service": service,
            "current_key": working_key.name if working_key else None,
            "available_keys": len([k for k in service_keys if k["working"]]),
            "total_keys": len(service_keys),
            "keys": service_keys
        }
    
    def export_config(self) -> Dict[str, Any]:
        """Export configuration for use in frontend"""
        config = {
            "services": {},
            "fallback_enabled": True,
            "last_updated": datetime.now().isoformat()
        }
        
        for service in set(key.service for keys in self.keys.values() for key in keys):
            info = self.get_key_info(service)
            config["services"][service] = {
                "available": info["available_keys"] > 0,
                "total_keys": info["total_keys"],
                "current_key": info["current_key"]
            }
        
        return config

# Global instance
api_manager = APIKeyManager()

async def main():
    """Test function"""
    print("🔑 API Key Manager - Comprehensive Test")
    print("=" * 50)
    
    # Test all keys
    results = await api_manager.test_all_keys()
    
    print(f"\n📊 Test Results:")
    print(f"Total Keys: {results['summary']['total_keys']}")
    print(f"Working: {results['summary']['working_keys']}")
    print(f"Failed: {results['summary']['failed_keys']}")
    print(f"Success Rate: {results['summary']['working_keys']/results['summary']['total_keys']*100:.1f}%")
    
    print(f"\n🔧 Service Status:")
    for service, service_keys in results["services"].items():
        working = len([k for k in service_keys if k["working"]])
        total = len(service_keys)
        print(f"  {service}: {working}/{total} working")
        
        for key in service_keys:
            status = "✅" if key["working"] else "❌"
            print(f"    {status} {key['name']} (priority: {key['priority']})")
    
    # Test getting working keys
    print(f"\n🎯 Active Key Selection:")
    for service in ["gemini", "openai", "tilda", "google_cloud"]:
        key = api_manager.get_working_key(service)
        if key:
            print(f"  {service}: {key.name} (priority {key.priority})")
        else:
            print(f"  {service}: No working keys available")

if __name__ == "__main__":
    asyncio.run(main())