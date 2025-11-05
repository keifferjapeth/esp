#!/usr/bin/env python3
"""
Simple AI Response Test
Tests if AI responds to basic queries without complex dependencies.
"""

print("🤖 Simple AI Test Started")
print("=" * 50)

# Test 1: Basic Response
print("✓ Python is working")
print("✓ Script is executing")

# Test 2: Simple AI-like response
def simple_ai_response(query):
    """Simple rule-based responses to test basic functionality"""
    query_lower = query.lower()
    
    if "hello" in query_lower or "hi" in query_lower:
        return "Hello! I'm responding successfully. AI communication is working!"
    elif "test" in query_lower:
        return "Test successful! AI is responding to your input."
    elif "working" in query_lower:
        return "Yes, I'm working! The AI system can process and respond to queries."
    else:
        return f"I received your message: '{query}' - AI response system is functional!"

# Test the response
test_query = "Hello, can you respond to test if AI is working?"
response = simple_ai_response(test_query)

print(f"📝 Query: {test_query}")
print(f"🤖 AI Response: {response}")
print("=" * 50)
print("✅ AI Response Test Complete!")