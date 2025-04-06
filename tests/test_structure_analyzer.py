"""
Tests for the structure analyzer module.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.structure_analyzer import StructureAnalyzer, LLMClient

class MockLLMClient:
    """Mock LLM client for testing."""
    
    def generate(self, prompt):
        """Return a simple mock response."""
        return '''
        {
          "sections": [
            {
              "id": "section_1",
              "title": "INSURING AGREEMENT",
              "level": 1,
              "text": "The Company will pay on behalf of the Insured...",
              "parent_id": null,
              "formatting_cues": ["uppercase_title", "numbering"],
              "cross_references": ["Section IV - Exclusions"]
            },
            {
              "id": "section_2",
              "title": "EXCLUSIONS",
              "level": 1,
              "text": "This policy does not apply to...",
              "parent_id": null,
              "formatting_cues": ["uppercase_title", "numbering"],
              "cross_references": []
            }
          ]
        }
        '''

def test_structure_analyzer_initialization():
    """Test structure analyzer initialization."""
    # With mock client
    mock_client = MockLLMClient()
    analyzer = StructureAnalyzer(mock_client)
    assert analyzer.llm_client is not None

def test_analyze_structure():
    """Test document structure analysis."""
    # Setup
    mock_client = MockLLMClient()
    analyzer = StructureAnalyzer(mock_client)
    
    # Test with simple document info
    document_info = {
        'full_text': 'Sample policy text with some content about insurance.'
    }
    
    # Analyze structure
    structure = analyzer.analyze_structure(document_info)
    
    # Verify structure
    assert 'sections' in structure
    assert len(structure['sections']) == 2
    
    # Check section details
    sections = structure['sections']
    assert sections[0]['title'] == 'INSURING AGREEMENT'
    assert sections[1]['title'] == 'EXCLUSIONS'

def test_analyze_structure_with_chunks():
    """Test document structure analysis with chunked text."""
    # Setup
    mock_client = MockLLMClient()
    analyzer = StructureAnalyzer(mock_client)
    
    # Test with chunked document info
    document_info = {
        'full_text': 'Sample policy text with some content about insurance.',
        'chunks': [
            'Sample policy text with',
            'some content about insurance.'
        ]
    }
    
    # Analyze structure
    structure = analyzer.analyze_structure(document_info)
    
    # Verify structure
    assert 'sections' in structure
    assert len(structure['sections']) > 0

def test_merge_sections():
    """Test merging sections from multiple chunks."""
    # Setup
    analyzer = StructureAnalyzer(MockLLMClient())
    
    # Create test sections with some duplicates
    sections = [
        {
            'id': 'section_1',
            'title': 'DEFINITIONS',
            'level': 1,
            'text': 'Part 1 of definitions',
            'cross_references': ['Section A']
        },
        {
            'id': 'section_2',
            'title': 'DEFINITIONS',
            'level': 1,
            'text': 'Part 2 of definitions',
            'cross_references': ['Section B']
        },
        {
            'id': 'section_3',
            'title': 'EXCLUSIONS',
            'level': 1,
            'text': 'These are the exclusions',
            'cross_references': []
        }
    ]
    
    # Merge sections
    merged = analyzer._merge_sections(sections)
    
    # Verify merged structure
    assert 'sections' in merged
    assert len(merged['sections']) == 2  # Should have merged the two DEFINITIONS sections
    
    # Check the merged content
    for section in merged['sections']:
        if section['title'] == 'DEFINITIONS':
            # The merged section should have combined text
            assert 'Part 1' in section['text']
            assert 'Part 2' in section['text']
            # And combined cross-references
            assert len(section['cross_references']) == 2
            assert 'Section A' in section['cross_references']
            assert 'Section B' in section['cross_references']