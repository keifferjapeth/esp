#!/usr/bin/env python3
"""
Integration test for ESP platform
Tests all components end-to-end
"""

import sys
import json
from key_manager import KeyManager
from service_manager import ServiceManager
from validation_system import ValidationSystem
from nlp_processor import NaturalLanguageProcessor


def test_key_manager():
    """Test key manager"""
    print("Testing Key Manager...")
    manager = KeyManager()
    assert manager.priority_order is not None
    assert len(manager.priority_order) == 5
    validation = manager.validate_keys()
    assert isinstance(validation, dict)
    print("  ✓ Key Manager test passed")
    return manager


def test_service_manager(key_manager):
    """Test service manager"""
    print("Testing Service Manager...")
    manager = ServiceManager(key_manager)
    results = manager.initialize_services()
    assert isinstance(results, dict)
    assert all(results.values()), "All services should initialize"
    
    # Test service methods
    result = manager.execute_bigquery("SELECT 1")
    assert result["status"] == "success"
    
    result = manager.execute_gemini("test prompt")
    assert result["status"] == "success"
    
    result = manager.execute_vertex("test task")
    assert result["status"] == "success"
    
    print("  ✓ Service Manager test passed")
    return manager


def test_validation_system(key_manager, service_manager):
    """Test validation system"""
    print("Testing Validation System...")
    validator = ValidationSystem(key_manager, service_manager)
    passed, results = validator.validate_all()
    assert isinstance(results, dict)
    assert len(results) == 7  # 7 validation passes
    print("  ✓ Validation System test passed")
    return validator


def test_nlp_processor(service_manager):
    """Test NLP processor"""
    print("Testing NLP Processor...")
    nlp = NaturalLanguageProcessor(service_manager)
    
    # Test various commands
    test_commands = [
        ("list my Tilda projects", "list_projects"),
        ("show me my files", "show_files"),
        ("query BigQuery", "query_bigquery"),
        ("analyze my data", "analyze"),
    ]
    
    for command, expected_action in test_commands:
        result = nlp.process(command)
        assert result["action"] == expected_action, f"Failed for command: {command}"
    
    print("  ✓ NLP Processor test passed")
    return nlp


def test_integration():
    """Run full integration test"""
    print("=" * 60)
    print("ESP Integration Test")
    print("=" * 60)
    print()
    
    try:
        # Test each component
        key_manager = test_key_manager()
        service_manager = test_service_manager(key_manager)
        validator = test_validation_system(key_manager, service_manager)
        nlp = test_nlp_processor(service_manager)
        
        print()
        print("=" * 60)
        print("✓ All Integration Tests Passed!")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)
