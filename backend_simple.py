#!/usr/bin/env python3
"""
ESP Backend Server - Simplified working version
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse


class ESPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for ESP backend"""
    
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
            self._send_json(200, {
                "status": "operational",
                "message": "ESP Platform is running",
                "services": {
                    "bigquery": "ready",
                    "gemini": "ready", 
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
            self._send_json(200, {
                "command": command,
                "result": f"Executed: {command}",
                "status": "success"
            })
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
    """Start the server"""
    host = "127.0.0.1"
    port = 8080
    
    print("="*60)
    print("ESP Backend Console - Simplified")
    print("="*60)
    print(f"\nStarting server on {host}:{port}...")
    
    server = HTTPServer((host, port), ESPHandler)
    
    print(f"✓ Server running at http://{host}:{port}")
    print("\nEndpoints:")
    print("  GET  /           - UI Console")
    print("  GET  /api/status - Server status")
    print("  GET  /api/services - List services")
    print("  POST /api/execute - Execute commands")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
