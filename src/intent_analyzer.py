"""
Intent analyzer module for determining coverage intent of policy elements.
"""

import json
import re
from typing import Dict, List, Optional, Any

class IntentAnalyzer:
    """Analyzes policy elements to determine coverage intent."""
    
    def __init__(self, llm_client):
        """
        Initialize the intent analyzer.
        
        Args:
            llm_client: Client for the LLM
        """
        self.llm_client = llm_client
        self.prompts = self._load_prompts()
    
    def _load_prompts(self):
        """Load prompt templates for intent analysis."""
        return {
            "intent_analysis": """
            # Insurance Policy Intent Analysis
            
            ## Your Task
            Analyze the insurance policy element below and determine its precise coverage intent - what it means to cover or exclude, under what circumstances, and with what limitations.
            
            ## Element Information
            Text: ```
            {element_text}
            ```
            
            Type: {element_type}
            Subtype: {element_subtype}
            
            ## Expected Output Format
            Provide your analysis as a JSON object:
            ```json
            {{
              "intent_summary": "Brief plain language summary of what this element means",
              "coverage_effect": "GRANTS_COVERAGE/LIMITS_COVERAGE/EXCLUDES_COVERAGE/MODIFIES_COVERAGE/DEFINES_TERM/IMPOSES_OBLIGATION",
              "intent_details": {{
                "what_is_covered": "Specific subject of coverage (if applicable)",
                "trigger_events": ["Event 1", "Event 2"],
                "temporal_conditions": "Time-related conditions that apply",
                "spatial_conditions": "Location-related conditions that apply",
                "actor_obligations": "What any party must do for this to apply"
              }},
              "intent_confidence": 0.85
            }}
            ```
            
            ## Guidelines
            - Focus on what the element actually means in practical terms, not just its technical classification
            - Consider the impact on coverage in real-world situations
            - Identify what would trigger this element to apply
            - Note any conditions that must be met for this element to apply
            - If this is a coverage grant, specify what is being covered
            - If this is an exclusion, specify what is being excluded and under what circumstances
            - For definitions, explain how the definition impacts coverage interpretation
            
            Return only the JSON object with no additional text.
            """
        }
    
    def analyze_intent(self, elements: List[Dict]) -> List[Dict]:
        """
        Analyze coverage intent for a list of policy elements.
        
        Args:
            elements: List of policy elements to analyze
            
        Returns:
            Elements with added intent analysis
        """
        enhanced_elements = []
        
        for element in elements:
            try:
                # Skip analysis for elements with insufficient text
                if not element.get('text') or len(element.get('text', '')) < 10:
                    element['intent_analysis'] = {
                        "intent_summary": "Insufficient text for intent analysis",
                        "coverage_effect": "UNKNOWN",
                        "intent_details": {},
                        "intent_confidence": 0.0
                    }
                    enhanced_elements.append(element)
                    continue
                
                # Check if element already has intent analysis
                if 'intent_analysis' in element and element['intent_analysis'].get('intent_confidence', 0) > 0.7:
                    enhanced_elements.append(element)
                    continue
                
                # Apply heuristic analysis first
                heuristic_intent = self._apply_intent_heuristics(element)
                if heuristic_intent and heuristic_intent.get('intent_confidence', 0) > 0.8:
                    element['intent_analysis'] = heuristic_intent
                    enhanced_elements.append(element)
                    continue
                
                # Use LLM for more complex analysis
                intent_analysis = self._analyze_element_intent(
                    element.get('text', ''),
                    element.get('type', 'UNKNOWN'),
                    element.get('subtype', '')
                )
                
                element['intent_analysis'] = intent_analysis
                enhanced_elements.append(element)
                
            except Exception as e:
                print(f"Error analyzing intent for element: {str(e)}")
                # Add default intent analysis in case of error
                element['intent_analysis'] = {
                    "intent_summary": f"Error during intent analysis: {str(e)}",
                    "coverage_effect": "UNKNOWN",
                    "intent_details": {},
                    "intent_confidence": 0.0
                }
                enhanced_elements.append(element)
        
        return enhanced_elements
    
    def _apply_intent_heuristics(self, element: Dict) -> Optional[Dict]:
        """
        Apply heuristics to determine intent for common element patterns.
        
        Args:
            element: The element to analyze
            
        Returns:
            Intent analysis if heuristics match, None otherwise
        """
        element_text = element.get('text', '').lower()
        element_type = element.get('type', '')
        
        # Coverage grant heuristics
        if element_type == 'COVERAGE_GRANT':
            if 'we will pay' in element_text or 'the company will pay' in element_text:
                return {
                    "intent_summary": "Promises to pay for covered damages or losses",
                    "coverage_effect": "GRANTS_COVERAGE",
                    "intent_details": {
                        "what_is_covered": self._extract_coverage_subject(element_text),
                        "trigger_events": self._extract_triggers(element_text),
                        "temporal_conditions": "",
                        "spatial_conditions": "",
                        "actor_obligations": ""
                    },
                    "intent_confidence": 0.85
                }
        
        # Exclusion heuristics
        if element_type == 'EXCLUSION':
            if 'this insurance does not apply to' in element_text or 'we will not pay' in element_text:
                return {
                    "intent_summary": "Explicitly removes specific situations from coverage",
                    "coverage_effect": "EXCLUDES_COVERAGE",
                    "intent_details": {
                        "what_is_covered": "",
                        "trigger_events": self._extract_triggers(element_text),
                        "temporal_conditions": "",
                        "spatial_conditions": "",
                        "actor_obligations": ""
                    },
                    "intent_confidence": 0.85
                }
        
        # Definition heuristics
        if element_type == 'DEFINITION':
            term_match = re.search(r'"([^"]*)"', element_text)
            if term_match and ' means ' in element_text:
                term = term_match.group(1)
                return {
                    "intent_summary": f"Defines the term '{term}' for interpreting policy coverage",
                    "coverage_effect": "DEFINES_TERM",
                    "intent_details": {
                        "defined_term": term,
                        "definition_impact": "Influences interpretation of policy provisions using this term"
                    },
                    "intent_confidence": 0.9
                }
        
        # No clear heuristic match
        return None
    
    def _extract_coverage_subject(self, text: str) -> str:
        """
        Extract the subject of coverage from element text.
        
        Args:
            text: Element text
            
        Returns:
            Subject of coverage
        """
        # Try to extract what is being covered from common patterns
        if 'damages because of' in text:
            match = re.search(r'damages because of\s*["\']?([^"\']*)["\']?', text)
            if match:
                return match.group(1).strip()
        
        if 'pay for' in text:
            match = re.search(r'pay for\s*["\']?([^"\']*)["\']?', text)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def _extract_triggers(self, text: str) -> List[str]:
        """
        Extract trigger events from element text.
        
        Args:
            text: Element text
            
        Returns:
            List of trigger events
        """
        triggers = []
        
        # Look for 'caused by' pattern
        if 'caused by' in text:
            match = re.search(r'caused by\s*["\']?([^"\']*)["\']?', text)
            if match:
                triggers.append(match.group(1).strip())
        
        # Look for 'if' conditions
        if ' if ' in text:
            match = re.search(r'if\s*([^.]*)', text)
            if match:
                triggers.append(match.group(1).strip())
        
        return triggers
    
    def _analyze_element_intent(self, element_text: str, element_type: str, element_subtype: str) -> Dict:
        """
        Use LLM to analyze the intent of a policy element.
        
        Args:
            element_text: Text of the element
            element_type: Type of the element
            element_subtype: Subtype of the element
            
        Returns:
            Intent analysis
        """
        # Prepare prompt for intent analysis
        prompt = self.prompts["intent_analysis"].format(
            element_text=element_text,
            element_type=element_type,
            element_subtype=element_subtype
        )
        
        # Call LLM with prompt
        response = self.llm_client.generate(prompt)
        
        # Parse the response
        try:
            cleaned_response = self._clean_json_response(response)
            intent_analysis = json.loads(cleaned_response)
            return intent_analysis
        except json.JSONDecodeError as e:
            print(f"Error parsing intent analysis response: {str(e)}")
            print(f"Raw response: {response[:200]}...")
            
            # Return basic intent analysis as fallback
            return {
                "intent_summary": "Failed to parse intent analysis",
                "coverage_effect": "UNKNOWN",
                "intent_details": {},
                "intent_confidence": 0.0
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