"""
Term extractor module for identifying key terms, conditions, and triggers in policy language.
"""

import json
import re
from typing import Dict, List, Optional, Any

class TermExtractor:
    """Extracts and categorizes specific terms and triggers in policy language."""
    
    def __init__(self, llm_client):
        """
        Initialize the term extractor.
        
        Args:
            llm_client: Client for the LLM
        """
        self.llm_client = llm_client
        self.prompts = self._load_prompts()
    
    def _load_prompts(self):
        """Load prompt templates for term extraction."""
        return {
            "term_extraction": """
            # Insurance Policy Term Extraction
            
            ## Your Task
            Analyze the insurance policy element below and extract specific terms, conditions, triggers, and other critical language components that affect the interpretation and application of coverage.
            
            ## Element Information
            Text: ```
            {element_text}
            ```
            
            Type: {element_type}
            
            ## Expected Output Format
            Provide your analysis as a JSON object:
            ```json
            {{
              "extracted_terms": [
                {{
                  "term": "The specific term or phrase",
                  "term_type": "DEFINED_TERM/TRIGGER/CONDITION/REQUIREMENT/LIMITATION/MONETARY_VALUE/TIME_PERIOD/LOCATION",
                  "context": "How this term is used in the element",
                  "significance": "How this term affects coverage or interpretation"
                }}
              ],
              "defined_terms": ["term1", "term2"],
              "temporal_terms": ["term1", "term2"],
              "monetary_terms": ["term1", "term2"],
              "logical_operators": ["and", "or", "not"],
              "confidence": 0.9
            }}
            ```
            
            ## Guidelines
            - Identify defined terms (typically in quotes or otherwise highlighted)
            - Extract triggers that activate or deactivate coverage
            - Note conditions that must be satisfied
            - Identify requirements imposed on parties
            - Extract monetary values and their context
            - Note time periods and deadlines
            - Identify locations or territories mentioned
            - Extract logical operators that affect interpretation
            
            Return only the JSON object with no additional text.
            """
        }
    
    def extract_terms(self, elements: List[Dict]) -> List[Dict]:
        """
        Extract and categorize terms from policy elements.
        
        Args:
            elements: List of policy elements to analyze
            
        Returns:
            Elements with added term extraction
        """
        enhanced_elements = []
        
        for element in elements:
            try:
                # Skip extraction for elements with insufficient text
                if not element.get('text') or len(element.get('text', '')) < 10:
                    element['term_extraction'] = {
                        "extracted_terms": [],
                        "defined_terms": [],
                        "temporal_terms": [],
                        "monetary_terms": [],
                        "logical_operators": [],
                        "confidence": 0.0
                    }
                    enhanced_elements.append(element)
                    continue
                
                # Check if element already has term extraction
                if 'term_extraction' in element and element['term_extraction'].get('confidence', 0) > 0.7:
                    enhanced_elements.append(element)
                    continue
                
                # Apply pattern extraction first
                pattern_terms = self._extract_pattern_terms(element.get('text', ''))
                
                # If we found a good number of terms with pattern matching, use those
                if len(pattern_terms.get('extracted_terms', [])) >= 3 and pattern_terms.get('confidence', 0) > 0.7:
                    element['term_extraction'] = pattern_terms
                    enhanced_elements.append(element)
                    continue
                
                # Use LLM for more comprehensive extraction
                term_extraction = self._extract_terms_with_llm(
                    element.get('text', ''),
                    element.get('type', 'UNKNOWN')
                )
                
                # Merge pattern-extracted terms with LLM-extracted terms if both exist
                if pattern_terms.get('extracted_terms') and term_extraction.get('extracted_terms'):
                    # Use set operations to avoid duplicates
                    all_terms = {term['term']: term for term in pattern_terms['extracted_terms']}
                    for term in term_extraction['extracted_terms']:
                        all_terms[term['term']] = term
                    
                    term_extraction['extracted_terms'] = list(all_terms.values())
                    
                    # Update counts
                    term_extraction['confidence'] = max(pattern_terms['confidence'], term_extraction['confidence'])
                
                element['term_extraction'] = term_extraction
                enhanced_elements.append(element)
                
            except Exception as e:
                print(f"Error extracting terms for element: {str(e)}")
                # Add default term extraction in case of error
                element['term_extraction'] = {
                    "extracted_terms": [],
                    "defined_terms": [],
                    "temporal_terms": [],
                    "monetary_terms": [],
                    "logical_operators": [],
                    "confidence": 0.0
                }
                enhanced_elements.append(element)
        
        return enhanced_elements
    
    def _extract_pattern_terms(self, text: str) -> Dict:
        """
        Extract terms using pattern matching.
        
        Args:
            text: Element text
            
        Returns:
            Dictionary of extracted terms
        """
        extracted_terms = []
        defined_terms = []
        temporal_terms = []
        monetary_terms = []
        logical_operators = []
        
        # Extract defined terms (in quotes)
        quoted_terms = re.findall(r'"([^"]*)"', text)
        for term in quoted_terms:
            defined_terms.append(term)
            extracted_terms.append({
                "term": term,
                "term_type": "DEFINED_TERM",
                "context": "Term appears in quotes, indicating it has a specific definition",
                "significance": "Important for interpreting policy language"
            })
        
        # Extract monetary values
        money_matches = re.findall(r'\$\s*[\d,]+(?:\.\d+)?|\d+\s*dollars|\d+\s*percent|(\d+)%', text)
        for match in money_matches:
            if match:
                monetary_terms.append(match)
                extracted_terms.append({
                    "term": match,
                    "term_type": "MONETARY_VALUE",
                    "context": "Financial amount mentioned in the policy",
                    "significance": "May indicate limits, deductibles, or coverage amounts"
                })
        
        # Extract time periods
        time_matches = re.findall(r'\b(\d+\s*days|\d+\s*months|\d+\s*years|immediately|promptly)\b', text, re.IGNORECASE)
        for match in time_matches:
            temporal_terms.append(match)
            extracted_terms.append({
                "term": match,
                "term_type": "TIME_PERIOD",
                "context": "Time period mentioned in the policy",
                "significance": "May indicate reporting deadlines or coverage periods"
            })
        
        # Extract logical operators
        operator_matches = re.findall(r'\b(and|or|not|except|unless|but)\b', text, re.IGNORECASE)
        for match in operator_matches:
            if match.lower() not in logical_operators:
                logical_operators.append(match.lower())
        
        # Calculate confidence based on number of extracted terms
        confidence = min(0.75, 0.3 + (len(extracted_terms) * 0.05))
        
        return {
            "extracted_terms": extracted_terms,
            "defined_terms": defined_terms,
            "temporal_terms": temporal_terms,
            "monetary_terms": monetary_terms,
            "logical_operators": logical_operators,
            "confidence": confidence
        }
    
    def _extract_terms_with_llm(self, element_text: str, element_type: str) -> Dict:
        """
        Use LLM to extract terms from a policy element.
        
        Args:
            element_text: Text of the element
            element_type: Type of the element
            
        Returns:
            Term extraction results
        """
        # Prepare prompt for term extraction
        prompt = self.prompts["term_extraction"].format(
            element_text=element_text,
            element_type=element_type
        )
        
        # Call LLM with prompt
        response = self.llm_client.generate(prompt)
        
        # Parse the response
        try:
            cleaned_response = self._clean_json_response(response)
            term_extraction = json.loads(cleaned_response)
            return term_extraction
        except json.JSONDecodeError as e:
            print(f"Error parsing term extraction response: {str(e)}")
            print(f"Raw response: {response[:200]}...")
            
            # Return basic term extraction as fallback
            return {
                "extracted_terms": [],
                "defined_terms": [],
                "temporal_terms": [],
                "monetary_terms": [],
                "logical_operators": [],
                "confidence": 0.0
            }
    
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