#!/usr/bin/env python3
"""
Key Manager - Manages API keys with priority hierarchy
Priority: primary → Tilda env → Google service → Vertex → local backup
"""

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path


class KeyManager:
    """Manages API keys with priority-based fallback system"""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the key manager with configuration"""
        self.config = self._load_config(config_path)
        self.priority_order = self.config["api_keys"]["priority_order"]
        self.sources = self.config["api_keys"]["sources"]
        self._key_cache = {}
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _expand_path(self, path: str) -> str:
        """Expand ~ and environment variables in path"""
        return os.path.expanduser(os.path.expandvars(path))
    
    def _load_key_from_env(self, var_name: str) -> Optional[str]:
        """Load API key from environment variable"""
        return os.environ.get(var_name)
    
    def _load_key_from_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load API key from JSON file"""
        try:
            expanded_path = self._expand_path(file_path)
            path = Path(expanded_path)
            if path.exists():
                with open(path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading key from {file_path}: {e}")
        return None
    
    def get_key(self, service: str = None) -> Optional[Any]:
        """
        Get API key with priority-based fallback
        Returns the first available key based on priority order
        """
        for priority_name in self.priority_order:
            if priority_name in self._key_cache:
                return self._key_cache[priority_name]
            
            source = self.sources.get(priority_name)
            if not source:
                continue
            
            key = None
            if source["type"] == "environment":
                key = self._load_key_from_env(source["var"])
            elif source["type"] == "file":
                key = self._load_key_from_file(source["path"])
            
            if key:
                self._key_cache[priority_name] = key
                print(f"Using API key from: {priority_name}")
                return key
        
        print("Warning: No API keys found in any source")
        return None
    
    def register_key(self, priority_name: str, key: Any) -> bool:
        """Register a new API key manually"""
        if priority_name in self.priority_order:
            self._key_cache[priority_name] = key
            return True
        return False
    
    def validate_keys(self) -> Dict[str, bool]:
        """Validate availability of all configured key sources"""
        validation_results = {}
        for priority_name in self.priority_order:
            source = self.sources.get(priority_name)
            if not source:
                validation_results[priority_name] = False
                continue
            
            if source["type"] == "environment":
                validation_results[priority_name] = bool(
                    self._load_key_from_env(source["var"])
                )
            elif source["type"] == "file":
                key_data = self._load_key_from_file(source["path"])
                validation_results[priority_name] = bool(key_data)
        
        return validation_results
    
    def get_active_key_priority(self) -> Optional[str]:
        """Get the priority name of the currently active key"""
        for priority_name in self.priority_order:
            if priority_name in self._key_cache:
                return priority_name
        return None


if __name__ == "__main__":
    # Test the key manager
    manager = KeyManager()
    print("Key Manager initialized")
    print(f"Priority order: {manager.priority_order}")
    
    # Validate keys
    validation = manager.validate_keys()
    print("\nKey validation results:")
    for name, valid in validation.items():
        status = "✓" if valid else "✗"
        print(f"  {status} {name}")
    
    # Try to get a key
    key = manager.get_key()
    if key:
        print(f"\nActive key priority: {manager.get_active_key_priority()}")
    else:
        print("\nNo keys available")
