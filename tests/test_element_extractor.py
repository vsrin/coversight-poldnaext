"""
Tests for the element extractor module.
"""

import pytest
from unittest.mock import MagicMock
from src.element_extractor import ElementExtractor

class MockLLMClient:
    """Mock LLM client for testing."""
    
    def __init__(self, responses=None):
        """Initialize the mock client with predefined responses."""
        self.responses = responses or {}
        self.prompts = []
    
    def generate(self, prompt):
        """Return a mock response based on prompt content."""
        self.prompts.append(prompt)
        
        # Return mock response based on prompt content
        if "Extract elements" in prompt or "Element Extraction" in prompt:
            return self.responses.get("extraction", """
            [
              {
                "text": "We will pay those sums that the insured becomes legally obligated to pay as damages because of 'bodily injury' or 'property damage' to which this insurance applies.",
                "type": "COVERAGE_GRANT",
                "subtype": "Liability Coverage",
                "metadata": {
                  "has_monetary_value": false,
                  "monetary_values": [],
                  "contains_reference": true,
                  "references": ["bodily injury", "property damage"],
                  "contains_condition": false,
                  "conditions": []
                }
              },
              {
                "text": "This insurance does not apply to 'bodily injury' or 'property damage' expected or intended from the standpoint of the insured.",
                "type": "EXCLUSION",
                "subtype": "Expected or Intended Injury",
                "metadata": {
                  "has_monetary_value": false,
                  "monetary_values": [],
                  "contains_reference": true,
                  "references": ["bodily injury", "property damage"],
                  "contains_condition": false,
                  "conditions": []
                }
              }
            ]
            """)
        
        # Default response
        return "[]"

def test_element_extractor_initialization():
    """Test element extractor initialization."""
    # Create mock LLM client
    mock_client = MockLLMClient()
    
    # Initialize extractor
    extractor = ElementExtractor(mock_client)
    
    # Verify initialization
    assert extractor.llm_client is not None
    assert extractor.prompts is not None

def test_extract_elements_from_section():
    """Test extracting elements from a section."""
    # Create mock LLM client
    mock_client = MockLLMClient()
    
    # Initialize extractor
    extractor = ElementExtractor(mock_client)
    
    # Create test section
    test_section = {
        'id': 'section_123',
        'title': 'INSURING AGREEMENT',
        'text': """
        We will pay those sums that the insured becomes legally obligated to pay as damages because of 'bodily injury' or 'property damage' to which this insurance applies.
        This insurance does not apply to 'bodily injury' or 'property damage' expected or intended from the standpoint of the insured.
        """,
        'classification': {
            'classification': 'INSURING_AGREEMENT'
        }
    }
    
    # Extract elements
    elements = extractor.extract_elements(test_section)
    
    # Verify results
    assert len(elements) == 2
    assert elements[0]['type'] == 'COVERAGE_GRANT'
    assert elements[1]['type'] == 'EXCLUSION'
    assert elements[0]['section_id'] == 'section_123'
    assert elements[1]['section_id'] == 'section_123'
    
    # Verify IDs were assigned
    assert 'id' in elements[0]
    assert 'id' in elements[1]
    
    # Verify relationship fields were initialized
    assert elements[0]['parent_element_id'] is None
    assert elements[0]['child_element_ids'] == []

def test_extract_elements_empty_section():
    """Test extracting elements from an empty section."""
    # Create mock LLM client
    mock_client = MockLLMClient()
    
    # Initialize extractor
    extractor = ElementExtractor(mock_client)
    
    # Create empty test section
    empty_section = {
        'id': 'empty_section',
        'title': 'Empty Section',
        'text': '',
        'classification': {
            'classification': 'OTHER'
        }
    }
    
    # Extract elements
    elements = extractor.extract_elements(empty_section)
    
    # Verify results
    assert len(elements) == 0

def test_clean_json_response():
    """Test cleaning JSON responses."""
    # Create mock LLM client
    mock_client = MockLLMClient()
    
    # Initialize extractor
    extractor = ElementExtractor(mock_client)
    
    # Test with JSON code block
    json_with_block = """```json
    [{"key": "value"}]
    ```"""
    cleaned = extractor._clean_json_response(json_with_block)
    assert cleaned == '[{"key": "value"}]'
    
    # Test with generic code block
    json_with_generic_block = "```\n[1, 2, 3]\n```"
    cleaned = extractor._clean_json_response(json_with_generic_block)
    assert cleaned == "[1, 2, 3]"
    
    # Test with plain JSON
    plain_json = '{"a": 1, "b": 2}'
    cleaned = extractor._clean_json_response(plain_json)
    assert cleaned == '{"a": 1, "b": 2}'

def test_parse_invalid_json():
    """Test handling of invalid JSON responses."""
    # Create mock client with invalid response
    mock_client = MockLLMClient(responses={
        "extraction": "This is not valid JSON"
    })
    
    # Initialize extractor
    extractor = ElementExtractor(mock_client)
    
    # Create test section
    test_section = {
        'id': 'section_123',
        'title': 'Test Section',
        'text': 'Some test content',
        'classification': {
            'classification': 'OTHER'
        }
    }
    
    # Extract elements
    elements = extractor.extract_elements(test_section)
    
    # Verify results
    assert len(elements) == 0  # Should return empty list on parse error