"""
Element classifier module for categorizing policy elements by type and function.
"""

import json
from typing import Dict, List, Optional, Any

class ElementClassifier:
    """Classifies and validates policy elements."""
    
    # Define standard element types
    ELEMENT_TYPES = [
        "COVERAGE_GRANT",      # What is covered
        "EXCLUSION",           # What is not covered
        "CONDITION",           # Requirements for coverage
        "DEFINITION",          # Terms defined in the policy
        "SUB_LIMIT",           # Specific limit within a coverage
        "RETENTION",           # Deductible or self-insured retention
        "EXTENSION",           # Extension of coverage
        "TERRITORY",           # Geographic scope of coverage
        "TIME_ELEMENT",        # Time limitations or requirements
        "REPORTING_OBLIGATION", # Requirements for claim reporting
        "OTHER"                # Other element types
    ]
    
    def __init__(self, llm_client):
        """
        Initialize the element classifier.
        
        Args:
            llm_client: Client for the LLM
        """
        self.llm_client = llm_client
        self.prompts = self._load_prompts()
        
    def _load_prompts(self):
        """Load prompt templates for element classification."""
        return {
            "classification": """
            # Insurance Policy Element Classification
            
            ## Your Task
            Analyze the insurance policy element below and classify it with high precision according to insurance industry standards.
            
            ## Element Text:
            ```
            {element_text}
            ```
            
            ## Initial Classification: {initial_type}
            ## Section Type: {section_type}
            
            ## Element Types
            - COVERAGE_GRANT: Provides coverage for specified losses or events
            - EXCLUSION: Explicitly removes something from coverage
            - CONDITION: Establishes requirements for coverage to apply
            - DEFINITION: Defines a term used in the policy
            - SUB_LIMIT: Specifies a limit within a broader coverage
            - RETENTION: Indicates a deductible or self-insured amount
            - EXTENSION: Extends or adds to the basic coverage
            - TERRITORY: Defines geographic scope of coverage
            - TIME_ELEMENT: Establishes time-based requirements or limitations
            - REPORTING_OBLIGATION: Requirements for reporting claims
            - OTHER: Any other element type
            
            ## Expected Output Format
            Provide your classification as a JSON object:
            ```json
            {{
              "type": "One of the element types listed above",
              "subtype": "More specific classification",
              "confidence": 0.95,
              "explanation": "Brief explanation of why this classification is appropriate",
              "keywords": ["term1", "term2"],
              "function": "Brief description of this element's function in the policy"
            }}
            ```
            
            ## Guidelines
            - Focus on the substantive function of the element, not just its format
            - Consider the context of the section type in your classification
            - Assign a confidence score (0.0 to 1.0) based on classification certainty
            - If uncertain between two types, choose the most specific applicable type
            - For definitions, identify the specific term being defined
            - For monetary provisions, note the specific values involved
            
            Return only the JSON object with no additional text.
            """
        }
    
    def classify_elements(self, elements: List[Dict], section: Dict) -> List[Dict]:
        """
        Classify and validate policy elements.
        
        Args:
            elements: List of extracted elements
            section: The section containing these elements
            
        Returns:
            List of classified elements
        """
        classified_elements = []
        
        for element in elements:
            try:
                # Get initial classification from extraction
                initial_type = element.get('type', 'UNKNOWN')
                
                # Skip classification refinement for high-confidence simple elements
                if self._is_simple_element(element, initial_type):
                    # Add default classification metadata
                    element['confidence'] = 0.9
                    element['explanation'] = f"Clear {initial_type.lower()} based on content and structure"
                    element['keywords'] = self._extract_keywords(element.get('text', ''))
                    element['function'] = self._generate_function_description(element, initial_type)
                    classified_elements.append(element)
                    continue
                
                # For complex elements, use LLM for refined classification
                classification = self._classify_element(
                    element.get('text', ''),
                    initial_type,
                    section.get('classification', {}).get('classification', 'UNKNOWN')
                )
                
                # Update element with refined classification
                element.update(classification)
                classified_elements.append(element)
                
            except Exception as e:
                print(f"Error classifying element: {str(e)}")
                # Keep the element with original classification
                element['confidence'] = 0.5
                element['explanation'] = f"Classification error: {str(e)}"
                element['keywords'] = []
                element['function'] = "Unknown function"
                classified_elements.append(element)
        
        return classified_elements
    
    def _is_simple_element(self, element: Dict, element_type: str) -> bool:
        """
        Determine if an element is simple enough to skip refined classification.
        
        Args:
            element: The element to check
            element_type: The initial element type
            
        Returns:
            Boolean indicating if this is a simple element
        """
        element_text = element.get('text', '').lower()
        
        # Simple checks based on element type and text patterns
        if element_type == "DEFINITION" and '"' in element_text and " means " in element_text:
            return True
        elif element_type == "EXCLUSION" and any(x in element_text for x in ["not cover", "does not", "excluded", "except", "exclusion"]):
            return True
        elif element_type == "COVERAGE_GRANT" and any(x in element_text for x in ["we will pay", "we cover", "this policy covers"]):
            return True
        elif element_type == "CONDITION" and any(x in element_text for x in ["condition", "must be", "required to", "you must", "insured shall"]):
            return True
        elif element_type == "SUB_LIMIT" and any(x in element_text for x in ["limit of", "$", "maximum of", "up to"]) and any(y in element_text for y in ["per", "for", "each"]):
            return True
        
        # By default, get refined classification
        return False
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract important keywords from element text.
        
        Args:
            text: Element text
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction based on common patterns
        keywords = []
        
        # Look for quoted terms (common in policies)
        import re
        quoted_terms = re.findall(r'"([^"]*)"', text)
        keywords.extend(quoted_terms)
        
        # Add common important terms if present
        important_terms = ["bodily injury", "property damage", "liability", "loss", "damage", 
                          "claim", "notice", "insured", "coverage", "policy", "limit", 
                          "deductible", "retention", "occurrence", "accident"]
        
        for term in important_terms:
            if term in text.lower():
                keywords.append(term)
        
        # Remove duplicates and limit length
        return list(set(keywords))[:5]
    
    def _generate_function_description(self, element: Dict, element_type: str) -> str:
        """
        Generate a simple function description for an element.
        
        Args:
            element: The element
            element_type: Element type
            
        Returns:
            Function description
        """
        text = element.get('text', '').lower()
        
        # Generate descriptions based on element type
        if element_type == "COVERAGE_GRANT":
            return "Provides coverage for specified losses or events"
        elif element_type == "EXCLUSION":
            return "Explicitly removes something from coverage"
        elif element_type == "CONDITION":
            return "Establishes requirements for coverage to apply"
        elif element_type == "DEFINITION":
            # Try to extract the term being defined
            import re
            term_match = re.search(r'"([^"]*)"', text)
            if term_match:
                return f"Defines the term '{term_match.group(1)}'"
            else:
                return "Defines a term used in the policy"
        elif element_type == "SUB_LIMIT":
            return "Specifies a limit within a broader coverage"
        elif element_type == "RETENTION":
            return "Indicates a deductible or self-insured amount"
        else:
            return f"Functions as a {element_type.lower().replace('_', ' ')}"
    
    def _classify_element(self, element_text: str, initial_type: str, section_type: str) -> Dict:
        """
        Get refined classification for a policy element.
        
        Args:
            element_text: The text of the element
            initial_type: Initial classification
            section_type: Type of the containing section
            
        Returns:
            Refined classification information
        """
        # Prepare prompt for classification
        prompt = self.prompts["classification"].format(
            element_text=element_text,
            initial_type=initial_type,
            section_type=section_type
        )
        
        # Call LLM for classification
        response = self.llm_client.generate(prompt)
        
        # Parse classification response
        try:
            cleaned_response = self._clean_json_response(response)
            classification = json.loads(cleaned_response)
            
            # Validate the classification type
            if classification.get('type') not in self.ELEMENT_TYPES:
                # Default to initial type if invalid
                classification['type'] = initial_type
                classification['explanation'] = classification.get('explanation', '') + " (Corrected invalid type)"
            
            return classification
        except json.JSONDecodeError:
            # If parsing fails, return basic classification
            return {
                "type": initial_type,
                "subtype": "",
                "confidence": 0.5,
                "explanation": "Failed to get refined classification",
                "keywords": self._extract_keywords(element_text),
                "function": self._generate_function_description({}, initial_type)
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