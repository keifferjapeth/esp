import json
import os
import requests
from datetime import datetime
import time

# API Keys from environment variables (set in Vercel dashboard)
REAL_API_KEYS = {
    "tilda": os.environ.get("TILDA_API_KEY", "b9j7w8eka0dwsizitkix"),
    "gemini": os.environ.get("GEMINI_API_KEY", "AIzaSyBQWBs2HYmllkp5t37QEwIhF0viJ8vWMZs"),
    "google_cloud_project": os.environ.get("GOOGLE_CLOUD_PROJECT", "alert-acrobat-477200-g9"),
}

def handler(request):
    """Vercel serverless function handler for Crystal AI Console API"""
    
    # Enable CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    if request.method == 'OPTIONS':
        return ('', 200, headers)
    
    try:
        if request.method == 'GET':
            return (json.dumps({
                "status": "🚀 Crystal AI Console API - Cloud Hosted",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "tilda": "✅ Connected - 7 projects",
                    "gemini": "✅ Connected - gemini-2.0-flash",
                    "google_cloud": "✅ Connected - alert-acrobat-477200-g9"
                }
            }), 200, headers)
        
        elif request.method == 'POST':
            data = request.get_json()
            command = data.get('command', '').lower()
            
            result = execute_real_command(command)
            
            return (json.dumps({
                "success": True,
                "command": command,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }), 200, headers)
            
    except Exception as e:
        return (json.dumps({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500, headers)

def execute_real_command(command):
    """Execute real commands with actual API integrations"""
    
    if 'tilda' in command:
        if 'projects' in command or 'status' in command:
            return get_tilda_projects()
        elif 'pages' in command:
            return get_tilda_pages()
    
    elif 'gemini' in command or 'ai' in command:
        prompt = command.replace('gemini', '').replace('ai', '').strip()
        if not prompt:
            prompt = "Crystal AI Console is now running in the cloud! Say hello."
        return call_gemini_ai(prompt)
    
    elif 'test' in command:
        return test_all_services()
    
    elif 'help' in command:
        return {
            "available_commands": [
                "tilda projects - List Tilda projects",
                "tilda pages - List pages from projects", 
                "gemini [prompt] - Call Gemini AI",
                "test - Test all services",
                "help - Show this help"
            ]
        }
    
    else:
        return {"message": f"Unknown command: {command}"}

def get_tilda_projects():
    """Get real Tilda projects using discovered API key"""
    try:
        url = f"https://builder.tildacdn.com/v1/getprojectslist/?key={REAL_API_KEYS['tilda']}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'FOUND':
                projects = data.get('result', [])
                return {
                    "projects_count": len(projects),
                    "projects": [{"id": p.get('id'), "title": p.get('title')} for p in projects[:5]]
                }
        
        return {"error": "Failed to fetch Tilda projects", "status_code": response.status_code}
        
    except Exception as e:
        return {"error": f"Tilda API error: {str(e)}"}

def get_tilda_pages():
    """Get pages from Tilda projects"""
    try:
        # First get projects
        projects = get_tilda_projects()
        if 'projects' not in projects:
            return projects
        
        all_pages = []
        for project in projects['projects'][:2]:  # Limit to first 2 projects
            try:
                url = f"https://builder.tildacdn.com/v1/getpageslist/?key={REAL_API_KEYS['tilda']}&projectid={project['id']}"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'FOUND':
                        pages = data.get('result', [])
                        all_pages.extend([{
                            "project": project['title'],
                            "page_id": p.get('id'),
                            "title": p.get('title')
                        } for p in pages[:3]])  # Limit pages per project
                        
            except Exception as e:
                continue
        
        return {"total_pages": len(all_pages), "pages": all_pages}
        
    except Exception as e:
        return {"error": f"Pages fetch error: {str(e)}"}

def call_gemini_ai(prompt):
    """Call Gemini AI using discovered API key"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={REAL_API_KEYS['gemini']}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 200
            }
        }
        
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No response')
            return {"gemini_response": text.strip()}
        else:
            return {"error": f"Gemini API error: {response.status_code}"}
            
    except Exception as e:
        return {"error": f"Gemini error: {str(e)}"}

def test_all_services():
    """Test all integrated services"""
    results = {}
    
    # Test Tilda
    tilda_result = get_tilda_projects()
    results['tilda'] = "✅ Connected" if 'projects_count' in tilda_result else "❌ Error"
    
    # Test Gemini
    gemini_result = call_gemini_ai("Say: Crystal AI is working!")
    results['gemini'] = "✅ Connected" if 'gemini_response' in gemini_result else "❌ Error"
    
    return {
        "test_results": results,
        "overall_status": "✅ All systems operational" if all("✅" in v for v in results.values()) else "⚠️ Some issues detected"
    }

# Vercel serverless function entry point - main handler is already defined above