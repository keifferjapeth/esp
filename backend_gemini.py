#!/usr/bin/env python3
"""
ESP Backend Server with Gemini Integration
Translates natural language to machine commands and executes them
"""

import json
import os
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import sys

# Try to import google generativeai
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  google-generativeai not installed. Install with: pip3 install google-generativeai")


class GeminiTranslator:
    """Translates natural language to machine language"""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.model_name = "gemini-2.0-flash"  # Updated to latest available model
        self.is_ready = False
        self._initialize()
    
    def _initialize(self):
        """Initialize Gemini API"""
        if not GEMINI_AVAILABLE:
            print("❌ Gemini not available - google-generativeai not installed")
            return False
        
        if not self.api_key:
            print("⚠️  GOOGLE_GEMINI_API_KEY or GEMINI_API_KEY not set")
            return False
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
            self.is_ready = True
            print("✓ Gemini API initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Gemini: {e}")
            return False
    
    def translate_to_command(self, natural_language_input: str) -> dict:
        """Translate natural language to machine command"""
        if not self.is_ready:
            return {
                "success": False,
                "error": "Gemini API not initialized",
                "command": "",
                "explanation": "Please set GOOGLE_GEMINI_API_KEY environment variable"
            }
        
        try:
            prompt = f"""You are a terminal command translator. Convert this natural language request to a machine command that can be executed in a Unix/Linux/macOS terminal.

Rules:
1. ONLY output valid shell commands
2. Make commands safe - NO destructive operations (no rm -rf, no format, no destroy)
3. If the request is dangerous or malicious, return: ERROR_UNSAFE_COMMAND
4. Return JUST the command, no explanations

Natural language request: {natural_language_input}

Machine command:"""

            response = self.model.generate_content(prompt)
            command = response.text.strip()
            
            # Safety check
            if "ERROR_UNSAFE_COMMAND" in command:
                return {
                    "success": False,
                    "error": "Command is unsafe or not allowed",
                    "command": "",
                    "explanation": "This command was rejected for security reasons"
                }
            
            return {
                "success": True,
                "command": command,
                "error": None,
                "explanation": f"Translated: {natural_language_input} → {command}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": "",
                "explanation": f"Translation failed: {e}"
            }
    
    def get_status(self) -> dict:
        """Get Gemini status"""
        return {
            "gemini_available": GEMINI_AVAILABLE,
            "api_configured": bool(self.api_key),
            "ready": self.is_ready,
            "model": self.model_name if self.is_ready else None
        }


class CommandExecutor:
    """Executes shell commands safely"""
    
    # Blacklist dangerous commands
    DANGEROUS_PATTERNS = [
        'rm -rf',
        'dd if=',
        'mkfs',
        'format',
        'shutdown',
        'reboot',
        'halt',
        'poweroff',
        'sudo rm',
        '| sudo',
        'chmod 777',
        'chown root',
    ]
    
    @staticmethod
    def is_safe(command: str) -> bool:
        """Check if command is safe to execute"""
        command_lower = command.lower()
        for pattern in CommandExecutor.DANGEROUS_PATTERNS:
            if pattern.lower() in command_lower:
                return False
        return True
    
    @staticmethod
    def execute(command: str) -> dict:
        """Execute shell command safely"""
        if not CommandExecutor.is_safe(command):
            return {
                "success": False,
                "output": "",
                "error": "Command blocked for security reasons",
                "command": command
            }
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "command": command,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Command timed out after 10 seconds",
                "command": command
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "command": command
            }


class ESPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for ESP backend with Gemini"""
    
    # Shared Gemini translator instance
    gemini = None
    
    @classmethod
    def set_gemini(cls, gemini_instance):
        """Set the Gemini translator instance"""
        cls.gemini = gemini_instance
    
    def do_HEAD(self):
        """Handle HEAD requests"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/' or parsed_path.path == '':
            self._serve_html()
        elif parsed_path.path == '/api/status':
            gemini_status = self.gemini.get_status() if self.gemini else {}
            self._send_json(200, {
                "status": "operational",
                "message": "ESP Platform with Gemini Integration",
                "gemini": gemini_status,
                "services": {
                    "bigquery": "ready",
                    "gemini": "ready" if self.gemini.is_ready else "offline",
                    "vertex": "ready",
                    "terminal_automator": "ready"
                }
            })
        elif parsed_path.path == '/api/services':
            self._send_json(200, {
                "services": [
                    "bigquery",
                    "gemini",
                    "vertex",
                    "terminal_automator"
                ]
            })
        else:
            self._send_json(404, {"error": "Not found"})
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        try:
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
        except:
            self._send_json(400, {"error": "Invalid request"})
            return
        
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/execute':
            command = data.get("command", "")
            
            if not command:
                self._send_json(400, {"error": "No command provided"})
                return
            
            # Step 1: Translate natural language to machine command
            translation = self.gemini.translate_to_command(command)
            
            if not translation["success"]:
                self._send_json(200, {
                    "command": command,
                    "status": "translation_failed",
                    "error": translation["error"],
                    "explanation": translation["explanation"]
                })
                return
            
            machine_command = translation["command"]
            
            # Step 2: Execute the machine command
            execution = CommandExecutor.execute(machine_command)
            
            # Step 3: Return full result
            self._send_json(200, {
                "original_command": command,
                "translated_command": machine_command,
                "translation_explanation": translation["explanation"],
                "execution": execution,
                "status": "success" if execution["success"] else "execution_failed"
            })
        
        elif parsed_path.path == '/api/gemini/translate':
            """Translate without executing"""
            command = data.get("command", "")
            if not command:
                self._send_json(400, {"error": "No command provided"})
                return
            
            translation = self.gemini.translate_to_command(command)
            self._send_json(200, translation)
        
        else:
            self._send_json(404, {"error": "Endpoint not found"})
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_json(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _serve_html(self):
        """Serve the HTML UI"""
        html_file = os.path.join(os.path.dirname(__file__), 'tilda_ai_console.html')
        try:
            with open(html_file, 'r') as f:
                html_content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        except FileNotFoundError:
            self._send_json(404, {"error": "HTML file not found"})
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[ESP] {format % args}")


def main():
    """Start the server with Gemini integration"""
    host = "127.0.0.1"
    port = 8080
    
    print("="*60)
    print("ESP Backend with Gemini Integration")
    print("="*60)
    
    # Initialize Gemini
    gemini = GeminiTranslator()
    ESPHandler.set_gemini(gemini)
    
    gemini_status = gemini.get_status()
    print(f"\n🤖 Gemini Status:")
    print(f"  Available: {gemini_status['gemini_available']}")
    print(f"  Configured: {gemini_status['api_configured']}")
    print(f"  Ready: {gemini_status['ready']}")
    
    print(f"\n🌐 Starting server on {host}:{port}...")
    
    server = HTTPServer((host, port), ESPHandler)
    
    print(f"✓ Server running at http://{host}:{port}")
    print("\nEndpoints:")
    print("  GET  /                    - UI Console")
    print("  GET  /api/status          - Server and Gemini status")
    print("  GET  /api/services        - List services")
    print("  POST /api/execute         - NL→ML translation + execution")
    print("  POST /api/gemini/translate - NL→ML translation only")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
