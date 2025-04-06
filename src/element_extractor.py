"""
Element extractor module for identifying policy elements from document sections.
"""

import json
import uuid
from typing import Dict, List, Optional, Any

class ElementExtractor:
    """Extracts policy elements from section text."""
    
    def __init__(self, llm_client):
        """
        Initialize the element extractor.
        
        Args:
            llm_client: Client for the LLM
        """
        self.llm_client = llm_client
        self.prompts = self._load_prompts()
    
    def _load_prompts(self):
        """Load prompt templates for element extraction."""
        return {
            "extraction": """
            # Insurance Policy Element Extraction
            
            ## Your Task
            Analyze the insurance policy section below and identify distinct policy elements. A policy element is a specific provision, clause, or statement that serves a distinct function within the policy.
            
            ## Types of Elements to Identify
            - Coverage grants (what is covered)
            - Exclusions (what is not covered)
            - Conditions (requirements for coverage)
            - Definitions (terms defined in the policy)
            - Sub-limits (specific monetary limits)
            - Retentions (deductibles or self-insured amounts)
            - Extensions (additional coverages)
            - Territory provisions (geographic scope)
            - Time elements (time limitations)
            - Reporting obligations (claim reporting requirements)
            
            ## Section Text:
            ```
            {section_text}
            ```
            
            ## Section Classification: {section_type}
            
            ## Expected Output Format
            Provide your analysis as a JSON array of elements, where each element follows this structure:
            ```json
            [
              {{
                "text": "Full text of the element",
                "type": "One of the element types listed above",
                "subtype": "More specific classification if applicable",
                "metadata": {{
                  "has_monetary_value": true/false,
                  "monetary_values": ["$1,000,000", etc.],
                  "contains_reference": true/false,
                  "references": ["Section IV", etc.],
                  "contains_condition": true/false,
                  "conditions": ["Written notice must be provided...", etc.]
                }}
              }}
            ]
            ```
            
            ## Guidelines
            - Extract each distinct element separately
            - Preserve the exact text of each element
            - If an element contains sub-elements, identify both the parent and child elements
            - Pay special attention to numbered or lettered provisions
            - Focus on the substance rather than formatting
            - Ensure the JSON is valid and properly formatted
            
            Return only the JSON array with no additional text.
            """
        }
    
    def extract_elements(self, section: Dict) -> List[Dict]:
        """
        Extract policy elements from a section.
        
        Args:
            section: A document section containing policy text
            
        Returns:
            List of extracted elements
        """
        # Skip empty sections
        if not section.get('text'):
            return []
        
        # Prepare the prompt with section details
        section_text = section.get('text', '')
        section_type = section.get('classification', {}).get('classification', 'UNKNOWN')
        
        prompt = self.prompts["extraction"].format(
            section_text=section_text,
            section_type=section_type
        )
        
        # Call LLM with the prompt
        response = self.llm_client.generate(prompt)
        
        # Parse response to get elements
        try:
            # Clean up the response (remove code blocks if present)
            cleaned_response = self._clean_json_response(response)
            elements = json.loads(cleaned_response)
            
            # Add section ID and generate unique IDs for elements
            for i, element in enumerate(elements):
                element['id'] = f"element_{section.get('id')}_{i}_{str(uuid.uuid4())[:8]}"
                element['section_id'] = section.get('id')
                
                # Initialize relationship fields
                element['parent_element_id'] = None
                element['child_element_ids'] = []
            
            return elements
        except json.JSONDecodeError as e:
            print(f"Error parsing element extraction response: {str(e)}")
            print(f"Raw response: {response[:200]}...")
            return []
    
    def _clean_json_response(self, response: str) -> str:
        """
        Clean LLM response to extract valid JSON.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Cleaned JSON string
        """
        response = response.strip()
        
        # Remove markdown code blocks if present
        if response.startswith('```json') and response.endswith('```'):
            response = response[7:-3].strip()
        elif response.startswith('```') and response.endswith('```'):
            response = response[3:-3].strip()
            
        return response