"""
Configuration settings for the Policy DNA Extractor.
"""

import os
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union

class LLMConfig(BaseModel):
    """Configuration for the LLM client."""
    provider: str = "openai"  # The LLM provider (e.g., "openai", "anthropic", "gemini")
    model: str = Field(default="gpt-3.5-turbo")  # The model to use
    api_key: Optional[str] = None  # API key (default: read from environment)
    max_tokens: int = 4000  # Maximum response tokens
    temperature: float = 0.2  # Response randomness (0.0 to 1.0)
    
    def __init__(self, **data):
        super().__init__(**data)
        # Try to get API key from environment if not provided
        if self.api_key is None:
            if self.provider == "openai":
                self.api_key = os.environ.get("OPENAI_API_KEY")
            elif self.provider == "anthropic":
                self.api_key = os.environ.get("ANTHROPIC_API_KEY")
            elif self.provider == "gemini":
                self.api_key = os.environ.get("GOOGLE_API_KEY")
                
        if self.api_key is None:
            raise ValueError(f"No API key provided for {self.provider}")

class ParserConfig(BaseModel):
    """Configuration for document parsing."""
    chunk_size: int = 8000  # Size of text chunks for LLM processing
    overlap: int = 500  # Overlap between chunks to maintain context
    preserve_tables: bool = True  # Whether to preserve tables in parsing
    extract_images: bool = False  # Whether to extract and analyze images

class SectionTypes(BaseModel):
    """Defines the possible section types for classification."""
    types: List[str] = [
        "DECLARATIONS",
        "INSURING_AGREEMENT",
        "DEFINITIONS",
        "EXCLUSIONS",
        "CONDITIONS",
        "ENDORSEMENT",
        "SCHEDULE",
        "OTHER"
    ]

class ElementTypes(BaseModel):
    """Defines the possible element types for classification."""
    types: List[str] = [
        "COVERAGE_GRANT",
        "EXCLUSION",
        "CONDITION",
        "DEFINITION",
        "SUB_LIMIT",
        "RETENTION",
        "EXTENSION",
        "TERRITORY",
        "TIME_ELEMENT",
        "REPORTING_OBLIGATION",
        "OTHER"
    ]

class ElementExtractionConfig(BaseModel):
    """Configuration for element extraction."""
    min_confidence: float = 0.6  # Minimum confidence score for valid classifications
    extract_monetary_values: bool = True  # Whether to extract monetary values
    extract_references: bool = True  # Whether to extract references
    analyze_relationships: bool = True  # Whether to analyze relationships between elements

class AppConfig(BaseModel):
    """Main application configuration."""
    llm: LLMConfig = LLMConfig()
    parser: ParserConfig = ParserConfig()
    section_types: SectionTypes = SectionTypes()
    element_types: ElementTypes = ElementTypes()
    element_extraction: ElementExtractionConfig = ElementExtractionConfig()
    debug_mode: bool = False
    output_dir: str = "output"

# Create default configuration
default_config = AppConfig()

def get_config() -> AppConfig:
    """Get the application configuration."""
    return default_config