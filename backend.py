#!/usr/bin/env python3
"""
ESP Backend Server - Main backend console server
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from key_manager import KeyManager
from service_manager import ServiceManager
from validation_system import ValidationSystem
from nlp_processor import NaturalLanguageProcessor


class ESPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for ESP backend"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/' or parsed_path.path == '':
            self._serve_html()
        elif parsed_path.path == '/status':
            self._handle_status()
        elif parsed_path.path == '/validate':
            self._handle_validate()
        elif parsed_path.path == '/services':
            self._handle_services()
        elif parsed_path.path == '/api/status':
            self._handle_status()
        elif parsed_path.path == '/api/services':
            self._handle_services()
        else:
            self._send_response(404, {"error": "Not found"})
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_response(400, {"error": "Invalid JSON"})
            return
        
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/execute':
            self._handle_execute(data)
        elif parsed_path.path == '/query':
            self._handle_query(data)
        else:
            self._send_response(404, {"error": "Not found"})
    
    def do_HEAD(self):
        """Handle HEAD requests (preflight checks)"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_response(self, status_code, data):
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
            self._send_response(404, {"error": "HTML file not found"})
    
    
    def _handle_status(self):
        """Handle /status endpoint"""
        status = {
            "status": "running",
            "services": self.server.service_manager.get_service_status(),
            "active_key": self.server.key_manager.get_active_key_priority()
        }
        self._send_response(200, status)
    
    def _handle_validate(self):
        """Handle /validate endpoint"""
        passed, results = self.server.validator.validate_all()
        response = {
            "passed": passed,
            "results": results
        }
        self._send_response(200, response)
    
    def _handle_services(self):
        """Handle /services endpoint"""
        services = self.server.service_manager.get_service_status()
        self._send_response(200, {"services": services})
    
    def _handle_execute(self, data):
        """Handle /execute endpoint"""
        command = data.get("command", "")
        if not command:
            self._send_response(400, {"error": "No command provided"})
            return
        
        result = self.server.nlp.process(command)
        self._send_response(200, result)
    
    def _handle_query(self, data):
        """Handle /query endpoint"""
        service = data.get("service", "")
        query = data.get("query", "")
        
        if service == "bigquery":
            result = self.server.service_manager.execute_bigquery(query)
        elif service == "gemini":
            result = self.server.service_manager.execute_gemini(query)
        elif service == "vertex":
            result = self.server.service_manager.execute_vertex(query)
        else:
            result = {"error": f"Unknown service: {service}"}
        
        self._send_response(200, result)
    
    def log_message(self, format, *args):
        """Custom log message format"""
        print(f"[ESP] {format % args}")


class ESPServer(HTTPServer):
    """ESP HTTP Server with initialized components"""
    
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        
        # Initialize all components
        print("Initializing ESP Backend...")
        self.key_manager = KeyManager()
        self.service_manager = ServiceManager(self.key_manager)
        self.validator = ValidationSystem(self.key_manager, self.service_manager)
        self.nlp = NaturalLanguageProcessor(self.service_manager)
        
        # Initialize services
        print("\nInitializing services...")
        init_results = self.service_manager.initialize_services()
        for service, success in init_results.items():
            status = "✓" if success else "✗"
            print(f"  {status} {service}")
        
        print("\nESP Backend ready!")


def main():
    """Start the ESP backend server"""
    host = "127.0.0.1"
    port = 8080
    
    print("="*60)
    print("ESP Backend Console")
    print("="*60)
    
    server = ESPServer((host, port), ESPHandler)
    
    print(f"\nServer running at http://{host}:{port}")
    print("\nAvailable endpoints:")
    print("  GET  /status    - Get server status")
    print("  GET  /validate  - Run validation")
    print("  GET  /services  - Get service status")
    print("  POST /execute   - Execute natural language command")
    print("  POST /query     - Execute service query")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down ESP Backend...")
        server.shutdown()


if __name__ == "__main__":
    main()
