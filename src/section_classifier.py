"""
Section classifier module for categorizing document sections using LLM.
"""

import json
from typing import Dict, List, Any, Optional
from config.prompts import Prompts
from config.config import get_config
from src.structure_analyzer import LLMClient

class SectionClassifier:
    """Classifies document sections using LLM."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize the section classifier.
        
        Args:
            llm_client: Client for the LLM
        """
        self.llm_client = llm_client or LLMClient()
        self.config = get_config()
        
    def classify_sections(self, sections: List[Dict]) -> List[Dict]:
        """
        Classify each section by type.
        
        Args:
            sections: List of document sections
            
        Returns:
            List of sections with classification added
        """
        classified_sections = []
        
        for section in sections:
            try:
                classification = self._classify_section(section)
                section['classification'] = classification
                classified_sections.append(section)
                print(f"Classified section: {section['title']} as {classification.get('classification', 'UNKNOWN')}")
            except Exception as e:
                print(f"Error classifying section {section.get('title', 'Unknown')}: {str(e)}")
                # Add section without classification in case of error
                section['classification'] = {
                    'classification': 'UNKNOWN',
                    'confidence': 0.0,
                    'evidence': f"Error: {str(e)}"
                }
                classified_sections.append(section)
            
        return classified_sections
    
    def _classify_section(self, section: Dict) -> Dict:
        """
        Classify a single section using LLM.
        
        Args:
            section: Section information
            
        Returns:
            Classification information
        """
        # Extract section text and title
        section_text = section.get('text', '')
        section_title = section.get('title', '')
        
        # Skip empty sections
        if not section_text and not section_title:
            return {
                'classification': 'UNKNOWN',
                'confidence': 0.0,
                'evidence': 'Empty section'
            }
        
        # Use heuristics for quick classification if possible
        heuristic_classification = self._apply_heuristics(section_title, section_text)
        if heuristic_classification:
            return heuristic_classification
        
        # Prepare prompt for classification
        prompt = Prompts.section_classification_prompt(section_text, section_title)
        
        # Call LLM with prompt
        response = self.llm_client.generate(prompt)
        
        # Parse LLM response
        try:
            classification = json.loads(response)
            return classification
        except json.JSONDecodeError:
            # If response can't be parsed, make a best guess based on title
            print(f"Warning: Could not parse LLM response as JSON. Response: {response[:200]}...")
            return self._classify_by_title(section_title)
    
    def _apply_heuristics(self, title: str, text: str) -> Optional[Dict]:
        """
        Apply simple heuristics to classify sections without using LLM.
        
        Args:
            title: Section title
            text: Section text
            
        Returns:
            Classification info if heuristics match, None otherwise
        """
        # Convert title to uppercase for case-insensitive matching
        title_upper = title.upper()
        
        # Simple keyword matching
        if "DECLARATIONS" in title_upper or "DECLARATIONS PAGE" in title_upper:
            return {
                'classification': 'DECLARATIONS',
                'confidence': 0.9,
                'evidence': 'Title explicitly mentions declarations'
            }
        elif "DEFINITIONS" in title_upper or "DEFINED TERMS" in title_upper:
            return {
                'classification': 'DEFINITIONS',
                'confidence': 0.9,
                'evidence': 'Title explicitly mentions definitions'
            }
        elif "EXCLUSIONS" in title_upper or "WHAT IS NOT COVERED" in title_upper:
            return {
                'classification': 'EXCLUSIONS',
                'confidence': 0.9,
                'evidence': 'Title explicitly mentions exclusions'
            }
        elif "CONDITIONS" in title_upper:
            return {
                'classification': 'CONDITIONS',
                'confidence': 0.9,
                'evidence': 'Title explicitly mentions conditions'
            }
        elif "INSURING AGREEMENT" in title_upper or "COVERAGE" in title_upper:
            return {
                'classification': 'INSURING_AGREEMENT',
                'confidence': 0.9,
                'evidence': 'Title indicates coverage grant'
            }
        elif "ENDORSEMENT" in title_upper:
            return {
                'classification': 'ENDORSEMENT',
                'confidence': 0.9,
                'evidence': 'Title explicitly mentions endorsement'
            }
        elif "SCHEDULE" in title_upper:
            return {
                'classification': 'SCHEDULE',
                'confidence': 0.9,
                'evidence': 'Title explicitly mentions schedule'
            }
            
        # Check text patterns for definitions sections
        if text and '"' in text and "means" in text.lower():
            definition_pattern_count = text.lower().count(" means ")
            if definition_pattern_count > 2:
                return {
                    'classification': 'DEFINITIONS',
                    'confidence': 0.8,
                    'evidence': f'Contains multiple definition patterns (term "means"): {definition_pattern_count} instances'
                }
        
        # No clear heuristic match
        return None
    
    def _classify_by_title(self, title: str) -> Dict:
        """
        Make a best guess at classification based on section title.
        
        Args:
            title: Section title
            
        Returns:
            Classification information
        """
        title_lower = title.lower()
        
        # Common title patterns
        if "coverage" in title_lower or "insur" in title_lower:
            return {
                'classification': 'INSURING_AGREEMENT',
                'confidence': 0.6,
                'evidence': 'Title suggests coverage'
            }
        elif "exclusion" in title_lower or "not covered" in title_lower or "limitation" in title_lower:
            return {
                'classification': 'EXCLUSIONS',
                'confidence': 0.6,
                'evidence': 'Title suggests exclusions'
            }
        elif "definition" in title_lower or "meaning" in title_lower or "glossary" in title_lower:
            return {
                'classification': 'DEFINITIONS',
                'confidence': 0.6,
                'evidence': 'Title suggests definitions'
            }
        elif "condition" in title_lower or "requirement" in title_lower or "obligation" in title_lower:
            return {
                'classification': 'CONDITIONS',
                'confidence': 0.6,
                'evidence': 'Title suggests conditions'
            }
        elif "declar" in title_lower or "information" in title_lower:
            return {
                'classification': 'DECLARATIONS',
                'confidence': 0.5,
                'evidence': 'Title might indicate declarations'
            }
        elif "schedule" in title_lower or "list" in title_lower:
            return {
                'classification': 'SCHEDULE',
                'confidence': 0.5,
                'evidence': 'Title might indicate a schedule'
            }
        elif "endorse" in title_lower or "rider" in title_lower or "amendment" in title_lower:
            return {
                'classification': 'ENDORSEMENT',
                'confidence': 0.6,
                'evidence': 'Title suggests an endorsement'
            }
        
        # Default classification when no patterns match
        return {
            'classification': 'OTHER',
            'confidence': 0.3,
            'evidence': 'No clear classification patterns in title'
        }