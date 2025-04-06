"""
Tests for the document parser module.
"""

import os
import pytest
from src.document_parser import DocumentParser
from config.config import ParserConfig

# Create test files directory if it doesn't exist
TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), 'test_files')
os.makedirs(TEST_FILES_DIR, exist_ok=True)

def test_document_parser_initialization():
    """Test document parser initialization."""
    # With default config
    parser = DocumentParser()
    assert parser.config is not None
    
    # With custom config
    custom_config = ParserConfig(chunk_size=5000, overlap=300)
    parser = DocumentParser(custom_config)
    assert parser.config.chunk_size == 5000
    assert parser.config.overlap == 300

def test_parse_document_file_not_found():
    """Test handling of non-existent file."""
    parser = DocumentParser()
    
    with pytest.raises(FileNotFoundError):
        parser.parse_document('non_existent_file.pdf')

def test_parse_document_unsupported_type():
    """Test handling of unsupported file type."""
    # Create a test file with unsupported extension
    test_file_path = os.path.join(TEST_FILES_DIR, 'test.xyz')
    with open(test_file_path, 'w') as f:
        f.write('Test content')
    
    parser = DocumentParser()
    
    with pytest.raises(ValueError):
        parser.parse_document(test_file_path)
    
    # Clean up
    os.remove(test_file_path)

def test_create_chunks():
    """Test text chunking functionality."""
    parser = DocumentParser(ParserConfig(chunk_size=20, overlap=5))
    
    # Test with short text (less than chunk size)
    short_text = "This is a short text."
    chunks = parser._create_chunks(short_text)
    assert len(chunks) == 1
    assert chunks[0] == short_text
    
    # Test with longer text
    long_text = "This is a longer text that should be split into multiple chunks. " * 3
    chunks = parser._create_chunks(long_text)
    assert len(chunks) > 1
    
    # Verify that chunks have appropriate content
    text_from_chunks = ' '.join(chunks)
    # The combined text should contain the important words from the original
    assert "longer" in text_from_chunks
    assert "multiple" in text_from_chunks

# If you have actual PDFs or DOCXs to test with, you can add more tests