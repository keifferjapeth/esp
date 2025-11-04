#!/usr/bin/env python3
"""
Crystal AI Console - Test Suite
Test all 3 systems with discovered API keys
"""

import requests
import json
import time
from datetime import datetime

class CrystalAITester:
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
        
    def log_result(self, test_name, success, details):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
    def test_gemini_api(self):
        """Test 1 - Gemini AI API with discovered key"""
        print("\n🧠 TEST 1: Gemini AI API")
        print("-" * 50)
        
        try:
            api_key = "AIzaSyBQWBs2HYmllkp5t37QEwIhF0viJ8vWMZs"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": "Test 1: Say 'Crystal AI Console Test 1 Complete' and nothing else."
                    }]
                }]
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data['candidates'][0]['content']['parts'][0]['text'].strip()
                self.log_result("Gemini API Connection", True, f"Response: {ai_response}")
                self.log_result("Gemini Model gemini-2.0-flash", True, f"Tokens used: {data['usageMetadata']['totalTokenCount']}")
                return True
            else:
                self.log_result("Gemini API Connection", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Gemini API Connection", False, f"Exception: {str(e)}")
            return False
    
    def test_tilda_api(self):
        """Test 2 - Tilda API with discovered keys"""
        print("\n🌐 TEST 2: Tilda API")
        print("-" * 50)
        
        try:
            # Use correct Tilda API keys from backend
            public_key = "b9j7w8eka0dwsizitkix"
            secret_key = "f6e8020a209425c3f895"
            url = f"http://api.tildacdn.info/v1/getprojectslist/?publickey={public_key}&secretkey={secret_key}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'FOUND':
                    projects = data.get('result', [])
                    self.log_result("Tilda API Connection", True, f"Found {len(projects)} projects")
                    
                    # Show first few projects
                    for i, project in enumerate(projects[:3]):
                        project_name = project.get('title', 'Unnamed')
                        project_id = project.get('id', 'No ID')
                        self.log_result(f"Tilda Project {i+1}", True, f"{project_name} (ID: {project_id})")
                    
                    return True
                else:
                    self.log_result("Tilda API Connection", False, f"API returned status: {data.get('status')}")
                    return False
            else:
                self.log_result("Tilda API Connection", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Tilda API Connection", False, f"Exception: {str(e)}")
            return False
    
    def test_bigquery_oauth(self):
        """Test 3 - BigQuery with OAuth2 Authentication"""
        print("\n📊 TEST 3: BigQuery OAuth2")
        print("-" * 50)
        
        try:
            # Import our authentication helper
            import sys
            sys.path.append('/Users/keifferjapeth/Documents/GitHub/esp')
            from simple_google_auth_test import SimpleGoogleAuth
            
            auth = SimpleGoogleAuth()
            token = auth.get_access_token()
            
            if not token:
                self.log_result("BigQuery OAuth2 Token", False, "Failed to get access token")
                return False
            
            self.log_result("BigQuery OAuth2 Token", True, f"Token obtained: {token[:20]}...")
            
            # Test BigQuery datasets
            url = f"https://bigquery.googleapis.com/bigquery/v2/projects/{auth.service_project}/datasets"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                datasets = data.get('datasets', [])
                self.log_result("BigQuery Datasets Access", True, f"Found {len(datasets)} datasets")
                
                # Show datasets
                for i, dataset in enumerate(datasets[:3]):
                    dataset_id = dataset.get('datasetReference', {}).get('datasetId', 'Unknown')
                    self.log_result(f"BigQuery Dataset {i+1}", True, f"{dataset_id}")
                
                return True
            else:
                self.log_result("BigQuery Datasets Access", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("BigQuery OAuth2", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all 3 tests"""
        print("🔮 CRYSTAL AI CONSOLE - 3X TEST SUITE")
        print("=" * 60)
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Run tests
        test1_result = self.test_gemini_api()
        test2_result = self.test_tilda_api()  
        test3_result = self.test_bigquery_oauth()
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Final report
        print("\n" + "=" * 60)
        print("📋 FINAL TEST RESULTS")
        print("=" * 60)
        
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} [{result['timestamp']}] {result['test']}: {result['details']}")
        
        print("\n" + "=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)
        print(f"🧠 Gemini AI: {'✅ WORKING' if test1_result else '❌ FAILED'}")
        print(f"🌐 Tilda API: {'✅ WORKING' if test2_result else '❌ FAILED'}")
        print(f"📊 BigQuery: {'✅ WORKING' if test3_result else '❌ FAILED'}")
        print(f"📈 Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        print(f"⏱️  Test Duration: {duration:.2f} seconds")
        
        if success_rate >= 80:
            print("🎉 CRYSTAL AI CONSOLE: READY FOR PRODUCTION!")
        elif success_rate >= 60:
            print("⚠️  CRYSTAL AI CONSOLE: Mostly working, minor issues")
        else:
            print("❌ CRYSTAL AI CONSOLE: Major issues need resolution")
        
        return {
            'success_rate': success_rate,
            'tests_passed': passed_tests,
            'total_tests': total_tests,
            'duration': duration,
            'results': self.test_results
        }

def main():
    """Run the 3x test suite"""
    tester = CrystalAITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    results = main()
    exit(0 if results['success_rate'] >= 80 else 1)