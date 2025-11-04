#!/usr/bin/env python3
"""
Natural Language Task Processor - Processes natural language commands
"""

import re
from typing import Dict, Any, Optional
from service_manager import ServiceManager


class NaturalLanguageProcessor:
    """Process natural language commands and route to appropriate services"""
    
    def __init__(self, service_manager: ServiceManager):
        """Initialize NLP processor"""
        self.service_manager = service_manager
        self.commands = {
            "list": self._handle_list,
            "show": self._handle_show,
            "query": self._handle_query,
            "search": self._handle_search,
            "run": self._handle_run,
            "execute": self._handle_execute,
            "analyze": self._handle_analyze,
            "create": self._handle_create,
        }
        
    def process(self, command: str) -> Dict[str, Any]:
        """Process a natural language command"""
        command = command.lower().strip()
        
        # Extract the action verb
        for cmd_verb, handler in self.commands.items():
            if command.startswith(cmd_verb):
                return handler(command)
        
        # If no specific handler, use Gemini for general processing
        return self._handle_general(command)
    
    def _handle_list(self, command: str) -> Dict[str, Any]:
        """Handle list commands"""
        if "project" in command or "tilda" in command:
            return {
                "action": "list_projects",
                "service": "tilda",
                "result": "Listing Tilda projects...",
                "data": ["Project 1", "Project 2", "Project 3"]
            }
        elif "file" in command:
            return {
                "action": "list_files",
                "service": "filesystem",
                "result": "Listing files...",
                "data": self._list_local_files()
            }
        else:
            return {
                "action": "list_unknown",
                "result": "Please specify what you want to list (projects, files, etc.)"
            }
    
    def _handle_show(self, command: str) -> Dict[str, Any]:
        """Handle show commands"""
        if "file" in command:
            return {
                "action": "show_files",
                "service": "filesystem",
                "result": "Showing files...",
                "data": self._list_local_files()
            }
        elif "note" in command or "terminal" in command:
            notes = self.service_manager.read_terminal_notes()
            return {
                "action": "show_notes",
                "service": "terminal_automator",
                "result": "Showing terminal notes...",
                "data": notes
            }
        else:
            return {
                "action": "show_unknown",
                "result": "Please specify what you want to show"
            }
    
    def _handle_query(self, command: str) -> Dict[str, Any]:
        """Handle query commands"""
        if "bigquery" in command:
            # Extract potential SQL query
            query = self._extract_query(command)
            result = self.service_manager.execute_bigquery(query)
            return {
                "action": "query_bigquery",
                "service": "bigquery",
                "result": result,
                "query": query
            }
        else:
            return {
                "action": "query_general",
                "result": "Please specify the data source (BigQuery, etc.)"
            }
    
    def _handle_search(self, command: str) -> Dict[str, Any]:
        """Handle search commands"""
        search_term = command.replace("search", "").strip()
        return {
            "action": "search",
            "service": "gemini",
            "result": f"Searching for: {search_term}",
            "term": search_term
        }
    
    def _handle_run(self, command: str) -> Dict[str, Any]:
        """Handle run commands"""
        task = command.replace("run", "").strip()
        return {
            "action": "run_task",
            "service": "vertex",
            "result": self.service_manager.execute_vertex(task),
            "task": task
        }
    
    def _handle_execute(self, command: str) -> Dict[str, Any]:
        """Handle execute commands"""
        task = command.replace("execute", "").strip()
        return {
            "action": "execute_task",
            "service": "vertex",
            "result": self.service_manager.execute_vertex(task),
            "task": task
        }
    
    def _handle_analyze(self, command: str) -> Dict[str, Any]:
        """Handle analyze commands"""
        subject = command.replace("analyze", "").strip()
        result = self.service_manager.execute_gemini(f"Analyze: {subject}")
        return {
            "action": "analyze",
            "service": "gemini",
            "result": result,
            "subject": subject
        }
    
    def _handle_create(self, command: str) -> Dict[str, Any]:
        """Handle create commands"""
        target = command.replace("create", "").strip()
        return {
            "action": "create",
            "service": "gemini",
            "result": f"Creating: {target}",
            "target": target
        }
    
    def _handle_general(self, command: str) -> Dict[str, Any]:
        """Handle general natural language commands"""
        result = self.service_manager.execute_gemini(command)
        return {
            "action": "general_query",
            "service": "gemini",
            "result": result,
            "command": command
        }
    
    def _extract_query(self, command: str) -> str:
        """Extract SQL query from command"""
        # Simple extraction - in production, this would be more sophisticated
        parts = command.split("bigquery")
        if len(parts) > 1:
            return parts[1].strip()
        return "SELECT * FROM table LIMIT 10"
    
    def _list_local_files(self) -> list:
        """List local files (placeholder)"""
        return [
            "document1.txt",
            "data.csv",
            "notes.md",
            "config.json"
        ]


if __name__ == "__main__":
    # Test NLP processor
    from key_manager import KeyManager
    
    key_manager = KeyManager()
    service_manager = ServiceManager(key_manager)
    service_manager.initialize_services()
    
    nlp = NaturalLanguageProcessor(service_manager)
    
    test_commands = [
        "list my Tilda projects",
        "show me my files",
        "query BigQuery",
        "analyze my data",
        "run optimization task"
    ]
    
    print("Testing Natural Language Processor\n")
    for cmd in test_commands:
        print(f"Command: {cmd}")
        result = nlp.process(cmd)
        print(f"Result: {result}\n")
