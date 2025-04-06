"""
Conditional language detector module for identifying conditions in policy language.
"""

import json
import re
from typing import Dict, List, Optional, Any

class ConditionalLanguageDetector:
    """Detects and analyzes conditional language in policy elements."""
    
    def __init__(self, llm_client):
        """
        Initialize the conditional language detector.
        
        Args:
            llm_client: Client for the LLM
        """
        self.llm_client = llm_client
        self.prompts = self._load_prompts()
        
        # Common conditional keywords and phrases
        self.conditional_keywords = [
            "if", "when", "provided that", "subject to", "in the event", 
            "only if", "unless", "except when", "provided", "on condition that",
            "where", "wherever", "as long as", "so long as", "to the extent that"
        ]
    
    def _load_prompts(self):
        """Load prompt templates for conditional language analysis."""
        return {
            "conditional_analysis": """
            # Insurance Policy Conditional Language Analysis
            
            ## Your Task
            Analyze the insurance policy element below and identify all conditional language that modifies coverage, including requirements, limitations, and triggers.
            
            ## Element Information
            Text: ```
            {element_text}
            ```
            
            Type: {element_type}
            
            ## Expected Output Format
            Provide your analysis as a JSON object:
            ```json
            {{
              "conditions": [
                {{
                  "condition_text": "Full text of the condition",
                  "condition_type": "PREREQUISITE/LIMITATION/EXCLUSIONARY/REPORTING/TIMING/GEOGRAPHICAL",
                  "effect": "How this condition modifies coverage",
                  "applies_to": "What the condition applies to",
                  "consequence": "What happens if condition is/isn't met"
                }}
              ],
              "has_complex_conditions": true/false,
              "condition_count": 2,
              "confidence": 0.95
            }}
            ```
            
            ## Condition Types
            - PREREQUISITE: Must be met for coverage to apply
            - LIMITATION: Restricts the scope of coverage
            - EXCLUSIONARY: Removes certain scenarios from coverage
            - REPORTING: Requirements for reporting claims or incidents
            - TIMING: Time-based conditions
            - GEOGRAPHICAL: Location-based conditions
            
            ## Guidelines
            - Extract the exact text of each condition
            - Determine how each condition affects coverage
            - Consider both explicit and implicit conditions
            - Identify requirements that must be satisfied
            - Note consequences of meeting or failing to meet conditions
            - Count and categorize all conditions found
            
            Return only the JSON object with no additional text.
            """
        }
    
    def detect_conditions(self, elements: List[Dict]) -> List[Dict]:
        """
        Detect and analyze conditional language in policy elements.
        
        Args:
            elements: List of policy elements to analyze
            
        Returns:
            Elements with added conditional language analysis
        """
        enhanced_elements = []
        
        for element in elements:
            try:
                # Skip detection for elements with insufficient text
                if not element.get('text') or len(element.get('text', '')) < 10:
                    element['conditional_analysis'] = {
                        "conditions": [],
                        "has_complex_conditions": False,
                        "condition_count": 0,
                        "confidence": 0.0
                    }
                    enhanced_elements.append(element)
                    continue
                
                # Check if element already has conditional analysis
                if 'conditional_analysis' in element and element['conditional_analysis'].get('confidence', 0) > 0.7:
                    enhanced_elements.append(element)
                    continue
                
                # Apply simple pattern detection first
                simple_conditions = self._detect_simple_conditions(element.get('text', ''))
                if simple_conditions and len(simple_conditions) > 0:
                    element['conditional_analysis'] = {
                        "conditions": simple_conditions,
                        "has_complex_conditions": False,
                        "condition_count": len(simple_conditions),
                        "confidence": 0.75
                    }
                    
                    # Skip LLM analysis if only simple conditions are present
                    if not self._has_complex_language(element.get('text', '')):
                        enhanced_elements.append(element)
                        continue
                
                # Use LLM for more complex analysis
                conditional_analysis = self._analyze_conditional_language(
                    element.get('text', ''),
                    element.get('type', 'UNKNOWN')
                )
                
                element['conditional_analysis'] = conditional_analysis
                enhanced_elements.append(element)
                
            except Exception as e:
                print(f"Error detecting conditions for element: {str(e)}")
                # Add default conditional analysis in case of error
                element['conditional_analysis'] = {
                    "conditions": [],
                    "has_complex_conditions": False,
                    "condition_count": 0,
                    "confidence": 0.0
                }
                enhanced_elements.append(element)
        
        return enhanced_elements
    
    def _detect_simple_conditions(self, text: str) -> List[Dict]:
        """
        Detect simple conditional statements using pattern matching.
        
        Args:
            text: Element text
            
        Returns:
            List of detected conditions
        """
        conditions = []
        
        # Check for common conditional keywords
        for keyword in self.conditional_keywords:
            pattern = r'(?i)(' + re.escape(keyword) + r'\s[^.,;:]*[.,;:])'
            matches = re.findall(pattern, text)
            
            for match in matches:
                condition_text = match.strip()
                
                # Determine condition type
                condition_type = "PREREQUISITE"  # Default
                
                if "time" in condition_text.lower() or "day" in condition_text.lower() or "within" in condition_text.lower():
                    condition_type = "TIMING"
                elif "report" in condition_text.lower() or "notify" in condition_text.lower() or "inform" in condition_text.lower():
                    condition_type = "REPORTING"
                elif "located" in condition_text.lower() or "territory" in condition_text.lower() or "where" in condition_text.lower():
                    condition_type = "GEOGRAPHICAL"
                elif "not" in condition_text.lower() or "except" in condition_text.lower() or "unless" in condition_text.lower():
                    condition_type = "EXCLUSIONARY"
                elif "limit" in condition_text.lower() or "only" in condition_text.lower() or "extent" in condition_text.lower():
                    condition_type = "LIMITATION"
                
                conditions.append({
                    "condition_text": condition_text,
                    "condition_type": condition_type,
                    "effect": "Modifies coverage based on this condition",
                    "applies_to": "The coverage described in this element",
                    "consequence": "Coverage may be affected if this condition is not met"
                })
        
        return conditions
    
    def _has_complex_language(self, text: str) -> bool:
        """
        Determine if text contains complex conditional structures.
        
        Args:
            text: Element text
            
        Returns:
            Boolean indicating if complex conditions are present
        """
        # Check for nested conditions
        nested_condition_count = 0
        for keyword in self.conditional_keywords:
            nested_condition_count += text.lower().count(keyword)
        
        if nested_condition_count >= 2:
            return True
        
        # Check for complex expressions
        complex_patterns = [
            r"only if.*and.*",
            r"provided that.*unless",
            r"except when.*if",
            r"to the extent that.*but only if"
        ]
        
        for pattern in complex_patterns:
            if re.search(pattern, text.lower()):
                return True
        
        # Check for sentence length - longer sentences often indicate complexity
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            if len(sentence.split()) > 25:
                return True
        
        return False
    
    def _analyze_conditional_language(self, element_text: str, element_type: str) -> Dict:
        """
        Use LLM to analyze conditional language in a policy element.
        
        Args:
            element_text: Text of the element
            element_type: Type of the element
            
        Returns:
            Conditional language analysis
        """
        # Prepare prompt for conditional language analysis
        prompt = self.prompts["conditional_analysis"].format(
            element_text=element_text,
            element_type=element_type
        )
        
        # Call LLM with prompt
        response = self.llm_client.generate(prompt)
        
        # Parse the response
        try:
            cleaned_response = self._clean_json_response(response)
            conditional_analysis = json.loads(cleaned_response)
            return conditional_analysis
        except json.JSONDecodeError as e:
            print(f"Error parsing conditional language analysis response: {str(e)}")
            print(f"Raw response: {response[:200]}...")
            
            # Return basic conditional analysis as fallback
            return {
                "conditions": [],
                "has_complex_conditions": False,
                "condition_count": 0,
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