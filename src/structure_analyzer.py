"""
Structure analyzer module for identifying document structure using LLM.
"""

import json
import uuid
import openai  # Import for OpenAI 0.28.1
from typing import Dict, List, Optional, Any
from config.prompts import Prompts
from config.config import LLMConfig, get_config

class LLMClient:
    """Client for interacting with LLM providers."""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize the LLM client.
        
        Args:
            config: Configuration for the LLM
        """
        self.config = config or get_config().llm
        
        # Initialize the appropriate API client
        if self.config.provider == "openai":
            # Using the older OpenAI API style
            openai.api_key = self.config.api_key
    
    def generate(self, prompt: str) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The LLM's response text
            
        Raises:
            RuntimeError: If there's an error communicating with the LLM
        """
        try:
            if self.config.provider == "openai":
                # Using the older OpenAI API style for 0.28.1
                response = openai.ChatCompletion.create(
                    model=self.config.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature
                )
                return response.choices[0].message.content
            else:
                raise ValueError(f"Unsupported LLM provider: {self.config.provider}")
        except Exception as e:
            raise RuntimeError(f"Error generating LLM response: {str(e)}")

class StructureAnalyzer:
    """Analyzes document structure using LLM."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None, config=None):
        """
        Initialize the structure analyzer.
        
        Args:
            llm_client: Client for the LLM
            config: Configuration for the analyzer
        """
        self.llm_client = llm_client or LLMClient(config)
    
    def analyze_structure(self, document_info: Dict) -> Dict:
        """
        Use LLM to identify document structure.
        
        Args:
            document_info: Document information from the parser
            
        Returns:
            Document structure information
        """
        # If document is chunked, analyze each chunk and merge results
        if 'chunks' in document_info and document_info['chunks']:
            all_sections = []
            
            for i, chunk in enumerate(document_info['chunks']):
                print(f"Processing chunk {i+1} of {len(document_info['chunks'])}...")
                chunk_structure = self._analyze_chunk(chunk, chunk_index=i)
                
                # Extract sections from the chunk
                if 'sections' in chunk_structure:
                    all_sections.extend(chunk_structure['sections'])
            
            # Merge sections from all chunks
            merged_structure = self._merge_sections(all_sections)
            return merged_structure
        else:
            # If document isn't chunked, analyze the full text
            return self._analyze_chunk(document_info['full_text'])
    
    def _analyze_chunk(self, text: str, chunk_index: int = 0) -> Dict:
        """
        Analyze a chunk of text to identify its structure.
        
        Args:
            text: The text chunk to analyze
            chunk_index: Index of the chunk in the document
            
        Returns:
            Structure information for the chunk
        """
        # Prepare prompt for structure analysis
        prompt = Prompts.structure_analysis_prompt(text)
        
        # Call LLM with prompt
        response = self.llm_client.generate(prompt)
        
        # Parse LLM response
        try:
            # Try to clean up the response if it's not valid JSON
            cleaned_response = response.strip()
            # If response starts with ```json and ends with ```, extract just the JSON part
            if cleaned_response.startswith('```json') and cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[7:-3].strip()
            elif cleaned_response.startswith('```') and cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[3:-3].strip()
                
            structure = json.loads(cleaned_response)
            
            # Add unique IDs to sections if not present
            if 'sections' in structure:
                for i, section in enumerate(structure['sections']):
                    if 'id' not in section or not section['id']:
                        section['id'] = f"section_{chunk_index}_{i}_{str(uuid.uuid4())[:8]}"
            
            return structure
        except json.JSONDecodeError:
            print(f"Warning: Could not parse LLM response as JSON. Response: {response[:200]}...")
            # Return empty structure if response can't be parsed
            return {'sections': []}
    
    def _merge_sections(self, all_sections: List[Dict]) -> Dict:
        """
        Merge sections from multiple chunks.
        
        Args:
            all_sections: List of sections from all chunks
            
        Returns:
            Merged document structure
        """
        # Group sections by title to identify duplicates
        sections_by_title = {}
        
        for section in all_sections:
            title = section.get('title', '').strip()
            
            if not title:
                continue
                
            if title not in sections_by_title:
                sections_by_title[title] = []
                
            sections_by_title[title].append(section)
        
        # Merge duplicate sections
        merged_sections = []
        
        for title, sections in sections_by_title.items():
            if len(sections) == 1:
                # No duplicates, add as is
                merged_sections.append(sections[0])
            else:
                # Merge duplicate sections
                merged_section = sections[0].copy()
                
                # Concatenate text from all duplicates
                all_text = [s.get('text', '') for s in sections]
                merged_section['text'] = '\n'.join(all_text)
                
                # Merge cross-references
                all_cross_refs = []
                for s in sections:
                    refs = s.get('cross_references', [])
                    if refs:
                        all_cross_refs.extend(refs)
                
                if all_cross_refs:
                    merged_section['cross_references'] = list(set(all_cross_refs))
                
                merged_sections.append(merged_section)
        
        # Sort sections by their level and position in the document
        merged_sections.sort(key=lambda s: (s.get('level', 999), s.get('id', '')))
        
        return {'sections': merged_sections}