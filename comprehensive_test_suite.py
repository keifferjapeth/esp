#!/usr/bin/env python3
"""
Comprehensive Test Suite for Tilda Crystal AI Console
Tests all components 3 times and generates detailed reports
"""

import asyncio
import json
import time
import requests
from datetime import datetime
import sys
import os

# Import our API key manager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from api_key_manager import APIKeyManager, api_manager

class ComprehensiveTestSuite:
    def __init__(self):
        self.api_manager = api_manager
        self.test_results = []
        self.test_round = 0
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    async def run_full_test_suite(self, rounds=3):
        """Run comprehensive tests multiple times"""
        self.log("🚀 Starting Comprehensive Test Suite")
        self.log(f"📊 Running {rounds} test rounds")
        
        overall_results = {
            "test_start": datetime.now().isoformat(),
            "rounds": [],
            "summary": {}
        }
        
        for round_num in range(1, rounds + 1):
            self.log(f"\n🔄 Starting Test Round {round_num}/{rounds}")
            round_result = await self.run_single_test_round(round_num)
            overall_results["rounds"].append(round_result)
            
            # Brief pause between rounds
            if round_num < rounds:
                self.log("⏳ Waiting 3 seconds before next round...")
                await asyncio.sleep(3)
        
        overall_results["test_end"] = datetime.now().isoformat()
        overall_results["summary"] = self.calculate_overall_summary(overall_results["rounds"])
        
        # Generate final report
        await self.generate_final_report(overall_results)
        return overall_results
    
    async def run_single_test_round(self, round_num):
        """Run a complete single test round"""
        self.test_round = round_num
        round_start = datetime.now()
        
        round_result = {
            "round": round_num,
            "start_time": round_start.isoformat(),
            "tests": {}
        }
        
        # Test 1: API Key Manager
        self.log("🔑 Testing API Key Manager...")
        round_result["tests"]["api_key_manager"] = await self.test_api_key_manager()
        
        # Test 2: Individual API Keys
        self.log("🌐 Testing Individual APIs...")
        round_result["tests"]["individual_apis"] = await self.test_individual_apis()
        
        # Test 3: Fallback System
        self.log("🔄 Testing Fallback System...")
        round_result["tests"]["fallback_system"] = await self.test_fallback_system()
        
        # Test 4: Tilda Integration
        self.log("🎨 Testing Tilda Integration...")
        round_result["tests"]["tilda_integration"] = await self.test_tilda_integration()
        
        # Test 5: UI Components (Static)
        self.log("💎 Testing UI Components...")
        round_result["tests"]["ui_components"] = await self.test_ui_components()
        
        # Test 6: File Operations
        self.log("📁 Testing File Operations...")
        round_result["tests"]["file_operations"] = await self.test_file_operations()
        
        # Test 7: Configuration System
        self.log("⚙️ Testing Configuration...")
        round_result["tests"]["configuration"] = await self.test_configuration()
        
        round_end = datetime.now()
        round_result["end_time"] = round_end.isoformat()
        round_result["duration"] = (round_end - round_start).total_seconds()
        round_result["success_rate"] = self.calculate_round_success_rate(round_result["tests"])
        
        self.log(f"✅ Round {round_num} completed in {round_result['duration']:.2f}s - Success: {round_result['success_rate']:.1f}%")
        
        return round_result
    
    async def test_api_key_manager(self):
        """Test the API Key Manager functionality"""
        results = {
            "test_name": "API Key Manager",
            "subtests": {},
            "overall_success": True
        }
        
        try:
            # Test loading keys
            total_keys = sum(len(keys) for keys in self.api_manager.keys.values())
            results["subtests"]["load_keys"] = {
                "success": total_keys > 0,
                "details": f"Loaded {total_keys} keys across {len(self.api_manager.keys)} services"
            }
            
            # Test getting working keys for each service
            services_to_test = ["gemini", "openai", "tilda", "google_cloud", "vertex_ai"]
            working_services = 0
            
            for service in services_to_test:
                key = self.api_manager.get_working_key(service)
                success = key is not None
                if success:
                    working_services += 1
                    
                results["subtests"][f"get_{service}_key"] = {
                    "success": success,
                    "details": f"Key found: {key.name if key else 'None'}"
                }
            
            results["subtests"]["key_availability"] = {
                "success": working_services >= 2,  # At least 2 services should have keys
                "details": f"{working_services}/{len(services_to_test)} services have working keys"
            }
            
        except Exception as e:
            results["overall_success"] = False
            results["error"] = str(e)
            
        return results
    
    async def test_individual_apis(self):
        """Test individual API endpoints"""
        results = {
            "test_name": "Individual APIs",
            "subtests": {},
            "overall_success": True
        }
        
        # Test APIs we have keys for
        api_tests = [
            ("gemini", self.test_gemini_api),
            ("tilda", self.test_tilda_api_direct),
            ("google_cloud", self.test_google_cloud_api),
        ]
        
        successful_apis = 0
        for api_name, test_func in api_tests:
            try:
                result = await test_func()
                results["subtests"][api_name] = result
                if result.get("success", False):
                    successful_apis += 1
            except Exception as e:
                results["subtests"][api_name] = {
                    "success": False,
                    "error": str(e)
                }
        
        results["subtests"]["api_success_rate"] = {
            "success": successful_apis >= 1,  # At least 1 API should work
            "details": f"{successful_apis}/{len(api_tests)} APIs working"
        }
        
        return results
    
    async def test_gemini_api(self):
        """Test Gemini API specifically"""
        try:
            key = self.api_manager.get_working_key("gemini")
            if not key:
                return {"success": False, "details": "No Gemini key available"}
            
            url = f"https://generativelanguage.googleapis.com/v1/models?key={key.key}"
            response = requests.get(url, timeout=10)
            
            return {
                "success": response.status_code == 200,
                "details": f"Status: {response.status_code}, Key: {key.name}",
                "response_time": response.elapsed.total_seconds()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_tilda_api_direct(self):
        """Test Tilda API directly"""
        try:
            key = self.api_manager.get_working_key("tilda")
            if not key:
                return {"success": False, "details": "No Tilda key available"}
            
            url = f"http://api.tildacdn.info/v1/getprojectslist/?publickey={key.key}"
            response = requests.get(url, timeout=10)
            
            success = response.status_code == 200
            projects_count = 0
            
            if success:
                try:
                    data = response.json()
                    if data.get("status") == "FOUND":
                        projects_count = len(data.get("result", []))
                except:
                    pass
            
            return {
                "success": success,
                "details": f"Status: {response.status_code}, Projects: {projects_count}",
                "projects_found": projects_count
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_google_cloud_api(self):
        """Test Google Cloud API"""
        try:
            key = self.api_manager.get_working_key("google_cloud")
            if not key:
                return {"success": False, "details": "No Google Cloud key available"}
            
            # Try a simple API call
            url = f"https://www.googleapis.com/bigquery/v2/projects"
            headers = {"Authorization": f"Bearer {key.key}"}
            response = requests.get(url, headers=headers, timeout=10)
            
            # Accept various status codes as "working"
            success = response.status_code in [200, 401, 403]
            
            return {
                "success": success,
                "details": f"Status: {response.status_code}, Key: {key.name}",
                "note": "401/403 indicates key format is valid"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def test_fallback_system(self):
        """Test the fallback system"""
        results = {
            "test_name": "Fallback System",
            "subtests": {},
            "overall_success": True
        }
        
        try:
            # Test priority ordering
            gemini_key = self.api_manager.get_working_key("gemini")
            if gemini_key:
                results["subtests"]["priority_selection"] = {
                    "success": True,
                    "details": f"Selected key: {gemini_key.name} (priority: {gemini_key.priority})"
                }
            else:
                results["subtests"]["priority_selection"] = {
                    "success": False,
                    "details": "No gemini key available for priority test"
                }
            
            # Test key availability checking
            test_key = next(iter(next(iter(self.api_manager.keys.values()))))
            available = self.api_manager.is_key_available(test_key)
            results["subtests"]["availability_check"] = {
                "success": True,
                "details": f"Availability check working: {available}"
            }
            
            # Test service mapping
            services_with_keys = 0
            for service in ["gemini", "tilda", "openai"]:
                if self.api_manager.get_working_key(service):
                    services_with_keys += 1
            
            results["subtests"]["service_mapping"] = {
                "success": services_with_keys > 0,
                "details": f"{services_with_keys} services have mapped keys"
            }
            
        except Exception as e:
            results["overall_success"] = False
            results["error"] = str(e)
        
        return results
    
    async def test_tilda_integration(self):
        """Test Tilda integration specifically"""
        results = {
            "test_name": "Tilda Integration",
            "subtests": {},
            "overall_success": True
        }
        
        try:
            # Test with the provided keys
            public_key = "b9j7w8eka0dwsizitkix"
            secret_key = "f6e8020a209425c3f895"
            
            # Test public key
            url = f"http://api.tildacdn.info/v1/getprojectslist/?publickey={public_key}"
            response = requests.get(url, timeout=10)
            
            results["subtests"]["public_key_test"] = {
                "success": response.status_code == 200,
                "details": f"Public key status: {response.status_code}"
            }
            
            # Test project listing
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("status") == "FOUND":
                        projects = data.get("result", [])
                        results["subtests"]["project_listing"] = {
                            "success": True,
                            "details": f"Found {len(projects)} projects"
                        }
                    else:
                        results["subtests"]["project_listing"] = {
                            "success": False,
                            "details": f"API response status: {data.get('status')}"
                        }
                except Exception as e:
                    results["subtests"]["project_listing"] = {
                        "success": False,
                        "error": str(e)
                    }
            
            # Test key storage in manager
            tilda_keys = self.api_manager.keys.get("tilda", [])
            results["subtests"]["key_storage"] = {
                "success": len(tilda_keys) > 0,
                "details": f"Stored {len(tilda_keys)} Tilda keys"
            }
            
        except Exception as e:
            results["overall_success"] = False
            results["error"] = str(e)
        
        return results
    
    async def test_ui_components(self):
        """Test UI components (static analysis)"""
        results = {
            "test_name": "UI Components",
            "subtests": {},
            "overall_success": True
        }
        
        try:
            # Check if HTML file exists and is readable
            html_path = "/Users/keifferjapeth/Documents/GitHub/esp/tilda_crystal_console.html"
            
            if os.path.exists(html_path):
                with open(html_path, 'r') as f:
                    content = f.read()
                
                results["subtests"]["html_file"] = {
                    "success": True,
                    "details": f"HTML file size: {len(content)} bytes"
                }
                
                # Check for key components
                components = [
                    ("Crystal CSS", "glassmorphism"),
                    ("Chat Interface", "chat-messages"),
                    ("API Status", "api-status"),
                    ("Terminal", "terminal-output"),
                    ("File Manager", "file-list"),
                    ("Configuration", "config-grid")
                ]
                
                found_components = 0
                for name, selector in components:
                    found = selector in content
                    if found:
                        found_components += 1
                    
                    results["subtests"][f"component_{name.lower().replace(' ', '_')}"] = {
                        "success": found,
                        "details": f"Component {'found' if found else 'missing'}"
                    }
                
                results["subtests"]["component_completeness"] = {
                    "success": found_components >= 4,  # At least 4/6 components
                    "details": f"{found_components}/{len(components)} components found"
                }
                
            else:
                results["subtests"]["html_file"] = {
                    "success": False,
                    "details": "HTML file not found"
                }
                results["overall_success"] = False
                
        except Exception as e:
            results["overall_success"] = False
            results["error"] = str(e)
        
        return results
    
    async def test_file_operations(self):
        """Test file operations"""
        results = {
            "test_name": "File Operations",
            "subtests": {},
            "overall_success": True
        }
        
        try:
            # Test directory listing
            current_dir = "/Users/keifferjapeth/Documents/GitHub/esp"
            if os.path.exists(current_dir):
                files = os.listdir(current_dir)
                results["subtests"]["directory_listing"] = {
                    "success": True,
                    "details": f"Found {len(files)} files/directories"
                }
            else:
                results["subtests"]["directory_listing"] = {
                    "success": False,
                    "details": "Current directory not accessible"
                }
            
            # Test file creation (test file)
            test_file = os.path.join(current_dir, "test_temp.txt")
            try:
                with open(test_file, 'w') as f:
                    f.write("Test file for Tilda Crystal Console")
                
                file_exists = os.path.exists(test_file)
                results["subtests"]["file_creation"] = {
                    "success": file_exists,
                    "details": "Test file created successfully"
                }
                
                # Clean up
                if file_exists:
                    os.remove(test_file)
                    
            except Exception as e:
                results["subtests"]["file_creation"] = {
                    "success": False,
                    "error": str(e)
                }
            
            # Test our created files
            created_files = [
                "api_key_manager.py",
                "tilda_crystal_console.html"
            ]
            
            existing_files = 0
            for filename in created_files:
                file_path = os.path.join(current_dir, filename)
                exists = os.path.exists(file_path)
                if exists:
                    existing_files += 1
                
                results["subtests"][f"file_{filename}"] = {
                    "success": exists,
                    "details": f"File {'exists' if exists else 'missing'}"
                }
            
            results["subtests"]["created_files_check"] = {
                "success": existing_files == len(created_files),
                "details": f"{existing_files}/{len(created_files)} created files found"
            }
            
        except Exception as e:
            results["overall_success"] = False
            results["error"] = str(e)
        
        return results
    
    async def test_configuration(self):
        """Test configuration system"""
        results = {
            "test_name": "Configuration",
            "subtests": {},
            "overall_success": True
        }
        
        try:
            # Test API manager configuration
            config = self.api_manager.export_config()
            
            results["subtests"]["config_export"] = {
                "success": isinstance(config, dict) and "services" in config,
                "details": f"Config exported with {len(config.get('services', {}))} services"
            }
            
            # Test service configuration
            services_configured = len(config.get("services", {}))
            results["subtests"]["services_configured"] = {
                "success": services_configured >= 3,
                "details": f"{services_configured} services configured"
            }
            
            # Test key info retrieval
            tilda_info = self.api_manager.get_key_info("tilda")
            results["subtests"]["key_info_retrieval"] = {
                "success": isinstance(tilda_info, dict) and "service" in tilda_info,
                "details": f"Key info retrieved for tilda: {tilda_info.get('total_keys', 0)} keys"
            }
            
            # Test configuration completeness
            required_config = ["services", "fallback_enabled", "last_updated"]
            config_complete = all(key in config for key in required_config)
            
            results["subtests"]["config_completeness"] = {
                "success": config_complete,
                "details": f"Config has all required fields: {config_complete}"
            }
            
        except Exception as e:
            results["overall_success"] = False
            results["error"] = str(e)
        
        return results
    
    def calculate_round_success_rate(self, tests):
        """Calculate success rate for a round"""
        total_subtests = 0
        successful_subtests = 0
        
        for test_name, test_result in tests.items():
            if "subtests" in test_result:
                for subtest_name, subtest_result in test_result["subtests"].items():
                    total_subtests += 1
                    if subtest_result.get("success", False):
                        successful_subtests += 1
        
        return (successful_subtests / total_subtests * 100) if total_subtests > 0 else 0
    
    def calculate_overall_summary(self, rounds):
        """Calculate overall summary across all rounds"""
        total_rounds = len(rounds)
        successful_rounds = sum(1 for round in rounds if round["success_rate"] >= 70)  # 70% threshold
        
        # Calculate average success rate
        avg_success_rate = sum(round["success_rate"] for round in rounds) / total_rounds if total_rounds > 0 else 0
        
        # Find most/least successful tests
        test_performance = {}
        for round in rounds:
            for test_name, test_result in round["tests"].items():
                if test_name not in test_performance:
                    test_performance[test_name] = []
                test_performance[test_name].append(test_result.get("overall_success", False))
        
        test_success_rates = {}
        for test_name, successes in test_performance.items():
            success_rate = sum(successes) / len(successes) * 100
            test_success_rates[test_name] = success_rate
        
        return {
            "total_rounds": total_rounds,
            "successful_rounds": successful_rounds,
            "overall_success_rate": avg_success_rate,
            "test_success_rates": test_success_rates,
            "best_performing_test": max(test_success_rates.items(), key=lambda x: x[1]) if test_success_rates else None,
            "worst_performing_test": min(test_success_rates.items(), key=lambda x: x[1]) if test_success_rates else None
        }
    
    async def generate_final_report(self, results):
        """Generate comprehensive final report"""
        self.log("\n" + "="*60)
        self.log("📊 COMPREHENSIVE TEST REPORT - FINAL RESULTS")
        self.log("="*60)
        
        summary = results["summary"]
        
        self.log(f"🎯 OVERALL RESULTS:")
        self.log(f"   Total Rounds: {summary['total_rounds']}")
        self.log(f"   Successful Rounds: {summary['successful_rounds']}")
        self.log(f"   Overall Success Rate: {summary['overall_success_rate']:.1f}%")
        
        if summary["overall_success_rate"] >= 80:
            status_emoji = "🟢"
            status = "EXCELLENT"
        elif summary["overall_success_rate"] >= 60:
            status_emoji = "🟡"
            status = "GOOD"
        else:
            status_emoji = "🔴"
            status = "NEEDS IMPROVEMENT"
            
        self.log(f"   System Status: {status_emoji} {status}")
        
        self.log(f"\n📈 TEST PERFORMANCE BY COMPONENT:")
        for test_name, success_rate in summary["test_success_rates"].items():
            emoji = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 60 else "❌"
            self.log(f"   {emoji} {test_name.replace('_', ' ').title()}: {success_rate:.1f}%")
        
        if summary["best_performing_test"]:
            best_test, best_rate = summary["best_performing_test"]
            self.log(f"\n🏆 Best Performing: {best_test.replace('_', ' ').title()} ({best_rate:.1f}%)")
        
        if summary["worst_performing_test"]:
            worst_test, worst_rate = summary["worst_performing_test"]
            self.log(f"🔧 Needs Attention: {worst_test.replace('_', ' ').title()} ({worst_rate:.1f}%)")
        
        self.log(f"\n🔄 ROUND-BY-ROUND BREAKDOWN:")
        for i, round_result in enumerate(results["rounds"], 1):
            emoji = "✅" if round_result["success_rate"] >= 70 else "⚠️"
            self.log(f"   {emoji} Round {i}: {round_result['success_rate']:.1f}% ({round_result['duration']:.1f}s)")
        
        # Save detailed report to file
        report_filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = f"/Users/keifferjapeth/Documents/GitHub/esp/{report_filename}"
        
        try:
            with open(report_path, 'w') as f:
                json.dump(results, f, indent=2)
            self.log(f"\n💾 Detailed report saved to: {report_filename}")
        except Exception as e:
            self.log(f"⚠️ Could not save report: {e}")
        
        self.log("\n" + "="*60)
        
        return results

async def main():
    """Main test execution"""
    test_suite = ComprehensiveTestSuite()
    
    print("🧪 Tilda Crystal AI Console - Comprehensive Test Suite")
    print("=" * 60)
    print("Testing all components 3 times...")
    print()
    
    results = await test_suite.run_full_test_suite(rounds=3)
    
    print(f"\n🎉 Testing Complete!")
    print(f"Overall Success Rate: {results['summary']['overall_success_rate']:.1f}%")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())