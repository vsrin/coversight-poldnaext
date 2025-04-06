"""
Language mapper module for integrating deep language analysis into policy DNA.
"""

from typing import Dict, List, Optional, Any

class LanguageMapper:
    """Maps deep language analysis into the policy DNA representation."""
    
    def create_language_map(self, elements: List[Dict], document_map: Dict) -> Dict:
        """
        Integrate deep language analysis into document map.
        
        Args:
            elements: List of elements with deep language analysis
            document_map: The document map from previous processing
            
        Returns:
            Enhanced document map with language analysis
        """
        # Create a copy of the document map to enhance
        enhanced_map = document_map.copy()
        
        # Add all analyzed elements to the map
        enhanced_map['elements_with_language_analysis'] = elements
        
        # Create language insights
        language_insights = self._create_language_insights(elements)
        enhanced_map['language_insights'] = language_insights
        
        # Add language analysis to sections
        self._add_language_analysis_to_sections(enhanced_map, elements)
        
        # Create navigational indices for language features
        enhanced_map['language_navigation'] = self._create_language_navigation(elements)
        
        return enhanced_map
    
    def _create_language_insights(self, elements: List[Dict]) -> Dict:
        """
        Create insights based on language analysis.
        
        Args:
            elements: List of elements with language analysis
            
        Returns:
            Dictionary of language insights
        """
        insights = {
            "coverage_summary": self._generate_coverage_summary(elements),
            "key_conditions": self._identify_key_conditions(elements),
            "defined_terms_usage": self._analyze_defined_terms_usage(elements),
            "temporal_requirements": self._extract_temporal_requirements(elements),
            "interpretation_challenges": self._identify_interpretation_challenges(elements)
        }
        
        return insights
    
    def _generate_coverage_summary(self, elements: List[Dict]) -> Dict:
        """
        Generate a summary of coverage based on intent analysis.
        
        Args:
            elements: List of elements with language analysis
            
        Returns:
            Coverage summary
        """
        # Extract elements with coverage grants
        coverage_elements = [e for e in elements if 
                            e.get('intent_analysis', {}).get('coverage_effect') == 'GRANTS_COVERAGE']
        
        # Extract elements with exclusions
        exclusion_elements = [e for e in elements if 
                             e.get('intent_analysis', {}).get('coverage_effect') == 'EXCLUDES_COVERAGE']
        
        # Extract elements with limitations
        limitation_elements = [e for e in elements if 
                              e.get('intent_analysis', {}).get('coverage_effect') == 'LIMITS_COVERAGE']
        
        # Create summary
        summary = {
            "coverage_grants": [
                {
                    "intent_summary": e.get('intent_analysis', {}).get('intent_summary', ''),
                    "details": e.get('intent_analysis', {}).get('intent_details', {}),
                    "element_id": e.get('id', '')
                } for e in coverage_elements[:5]  # Limit to top 5 for brevity
            ],
            "key_exclusions": [
                {
                    "intent_summary": e.get('intent_analysis', {}).get('intent_summary', ''),
                    "details": e.get('intent_analysis', {}).get('intent_details', {}),
                    "element_id": e.get('id', '')
                } for e in exclusion_elements[:5]  # Limit to top 5 for brevity
            ],
            "key_limitations": [
                {
                    "intent_summary": e.get('intent_analysis', {}).get('intent_summary', ''),
                    "details": e.get('intent_analysis', {}).get('intent_details', {}),
                    "element_id": e.get('id', '')
                } for e in limitation_elements[:5]  # Limit to top 5 for brevity
            ]
        }
        
        return summary
    
    def _identify_key_conditions(self, elements: List[Dict]) -> List[Dict]:
        """
        Identify key conditions that affect coverage.
        
        Args:
            elements: List of elements with language analysis
            
        Returns:
            List of key conditions
        """
        all_conditions = []
        
        # Extract conditions from all elements
        for element in elements:
            conditions = element.get('conditional_analysis', {}).get('conditions', [])
            
            for condition in conditions:
                # Add element context to the condition
                enriched_condition = condition.copy()
                enriched_condition['element_id'] = element.get('id', '')
                enriched_condition['element_type'] = element.get('type', '')
                
                all_conditions.append(enriched_condition)
        
        # Sort conditions by type
        key_conditions = []
        
        # Prioritize prerequisites
        prerequisites = [c for c in all_conditions if c.get('condition_type') == 'PREREQUISITE']
        key_conditions.extend(prerequisites[:3])  # Top 3 prerequisites
        
        # Add reporting conditions
        reporting = [c for c in all_conditions if c.get('condition_type') == 'REPORTING']
        key_conditions.extend(reporting[:3])  # Top 3 reporting conditions
        
        # Add timing conditions
        timing = [c for c in all_conditions if c.get('condition_type') == 'TIMING']
        key_conditions.extend(timing[:3])  # Top 3 timing conditions
        
        return key_conditions
    
    def _analyze_defined_terms_usage(self, elements: List[Dict]) -> Dict:
        """
        Analyze how defined terms are used throughout the policy.
        
        Args:
            elements: List of elements with language analysis
            
        Returns:
            Analysis of defined terms usage
        """
        # Find all defined terms
        defined_terms = {}
        
        for element in elements:
            # Extract terms from term extraction
            terms = element.get('term_extraction', {}).get('defined_terms', [])
            
            for term in terms:
                if term not in defined_terms:
                    defined_terms[term] = {
                        "term": term,
                        "definition_element": None,
                        "usage_count": 0,
                        "usage_contexts": []
                    }
                
                # Count usage
                defined_terms[term]["usage_count"] += 1
                
                # Add usage context
                context = {
                    "element_id": element.get('id', ''),
                    "element_type": element.get('type', ''),
                    "section_id": element.get('section_id', '')
                }
                
                if context not in defined_terms[term]["usage_contexts"]:
                    defined_terms[term]["usage_contexts"].append(context)
                
                # If this is a definition element, mark it
                if element.get('type') == 'DEFINITION':
                    # Check if this element defines this term
                    if f'"{term}"' in element.get('text', '') and 'means' in element.get('text', ''):
                        defined_terms[term]["definition_element"] = element.get('id', '')
        
        # Convert to list and sort by usage count
        terms_list = list(defined_terms.values())
        terms_list.sort(key=lambda x: x["usage_count"], reverse=True)
        
        return {
            "defined_terms_count": len(terms_list),
            "terms_with_definitions": len([t for t in terms_list if t["definition_element"]]),
            "most_used_terms": terms_list[:10]  # Top 10 most used terms
        }
    
    def _extract_temporal_requirements(self, elements: List[Dict]) -> List[Dict]:
        """
        Extract time-based requirements from policy elements.
        
        Args:
            elements: List of elements with language analysis
            
        Returns:
            List of temporal requirements
        """
        temporal_requirements = []
        
        # Extract time-related terms and conditions
        for element in elements:
            # Check for time-related terms
            time_terms = element.get('term_extraction', {}).get('temporal_terms', [])
            
            # Check for time-related conditions
            conditions = element.get('conditional_analysis', {}).get('conditions', [])
            time_conditions = [c for c in conditions if c.get('condition_type') == 'TIMING']
            
            if time_terms or time_conditions:
                requirement = {
                    "element_id": element.get('id', ''),
                    "element_type": element.get('type', ''),
                    "section_id": element.get('section_id', ''),
                    "time_terms": time_terms,
                    "time_conditions": time_conditions,
                    "time_sensitive": bool(time_conditions)
                }
                
                temporal_requirements.append(requirement)
        
        return temporal_requirements
    
    def _identify_interpretation_challenges(self, elements: List[Dict]) -> List[Dict]:
        """
        Identify elements with potential interpretation challenges.
        
        Args:
            elements: List of elements with language analysis
            
        Returns:
            List of potential interpretation challenges
        """
        challenges = []
        
        for element in elements:
            potential_issues = []
            
            # Check for complex conditions
            has_complex_conditions = element.get('conditional_analysis', {}).get('has_complex_conditions', False)
            condition_count = element.get('conditional_analysis', {}).get('condition_count', 0)
            
            if has_complex_conditions or condition_count > 2:
                potential_issues.append("Complex conditional language")
            
            # Check for low confidence in analysis
            intent_confidence = element.get('intent_analysis', {}).get('intent_confidence', 1.0)
            conditional_confidence = element.get('conditional_analysis', {}).get('confidence', 1.0)
            
            if intent_confidence < 0.7 or conditional_confidence < 0.7:
                potential_issues.append("Low confidence in analysis")
            
            # Check for ambiguous logical operators
            logical_operators = element.get('term_extraction', {}).get('logical_operators', [])
            if 'and' in logical_operators and 'or' in logical_operators:
                potential_issues.append("Mixed logical operators (and/or)")
            
            # Check for multiple defined terms
            defined_terms = element.get('term_extraction', {}).get('defined_terms', [])
            if len(defined_terms) > 3:
                potential_issues.append(f"Multiple defined terms ({len(defined_terms)})")
            
            # Add to challenges if issues found
            if potential_issues:
                challenges.append({
                    "element_id": element.get('id', ''),
                    "element_type": element.get('type', ''),
                    "section_id": element.get('section_id', ''),
                    "potential_issues": potential_issues,
                    "element_text": element.get('text', '')[:150] + "..."  # Preview of text
                })
        
        return challenges
    
    def _add_language_analysis_to_sections(self, document_map: Dict, elements: List[Dict]) -> None:
        """
        Add language analysis to document sections.
        
        Args:
            document_map: Document map to enhance
            elements: List of elements with language analysis
        """
        # Group elements by section
        elements_by_section = {}
        for element in elements:
            section_id = element.get('section_id')
            if section_id:
                if section_id not in elements_by_section:
                    elements_by_section[section_id] = []
                elements_by_section[section_id].append(element)
        
        # Helper function to process sections recursively
        def process_section(section):
            section_id = section.get('id')
            
            if section_id and section_id in elements_by_section:
                # Add language analysis summary to section
                section_elements = elements_by_section[section_id]
                
                section['language_analysis'] = {
                    "element_count": len(section_elements),
                    "coverage_effects": self._summarize_coverage_effects(section_elements),
                    "condition_count": sum(e.get('conditional_analysis', {}).get('condition_count', 0) 
                                          for e in section_elements),
                    "defined_terms": list(set(sum([e.get('term_extraction', {}).get('defined_terms', []) 
                                                 for e in section_elements], [])))
                }
            
            # Process child sections recursively
            if 'children' in section:
                for child in section['children']:
                    process_section(child)
        
        # Process all root sections
        for section in document_map.get('sections', []):
            process_section(section)
    
    def _summarize_coverage_effects(self, elements: List[Dict]) -> Dict:
        """
        Summarize coverage effects in a section.
        
        Args:
            elements: List of elements in the section
            
        Returns:
            Summary of coverage effects
        """
        effects = {
            "GRANTS_COVERAGE": 0,
            "LIMITS_COVERAGE": 0,
            "EXCLUDES_COVERAGE": 0,
            "MODIFIES_COVERAGE": 0,
            "DEFINES_TERM": 0,
            "IMPOSES_OBLIGATION": 0,
            "UNKNOWN": 0
        }
        
        # Count coverage effects
        for element in elements:
            effect = element.get('intent_analysis', {}).get('coverage_effect', 'UNKNOWN')
            if effect in effects:
                effects[effect] += 1
            else:
                effects['UNKNOWN'] += 1
        
        return effects
    
    def _create_language_navigation(self, elements: List[Dict]) -> Dict:
        """
        Create navigation indices for language features.
        
        Args:
            elements: List of elements with language analysis
            
        Returns:
            Navigation indices for language features
        """
        navigation = {
            "by_coverage_effect": self._index_by_coverage_effect(elements),
            "by_condition_type": self._index_by_condition_type(elements),
            "by_defined_term": self._index_by_defined_term(elements),
            "by_interpretation_challenge": self._index_by_challenge(elements)
        }
        
        return navigation
    
    def _index_by_coverage_effect(self, elements: List[Dict]) -> Dict:
        """
        Create an index of elements by coverage effect.
        
        Args:
            elements: List of elements with language analysis
            
        Returns:
            Index by coverage effect
        """
        index = {}
        
        for element in elements:
            effect = element.get('intent_analysis', {}).get('coverage_effect', 'UNKNOWN')
            
            if effect not in index:
                index[effect] = []
            
            index[effect].append({
                "id": element.get('id', ''),
                "intent_summary": element.get('intent_analysis', {}).get('intent_summary', ''),
                "confidence": element.get('intent_analysis', {}).get('intent_confidence', 0.0)
            })
        
        return index
    
    def _index_by_condition_type(self, elements: List[Dict]) -> Dict:
        """
        Create an index of elements by condition type.
        
        Args:
            elements: List of elements with language analysis
            
        Returns:
            Index by condition type
        """
        index = {}
        
        for element in elements:
            conditions = element.get('conditional_analysis', {}).get('conditions', [])
            
            for condition in conditions:
                condition_type = condition.get('condition_type', 'UNKNOWN')
                
                if condition_type not in index:
                    index[condition_type] = []
                
                index[condition_type].append({
                    "element_id": element.get('id', ''),
                    "condition_text": condition.get('condition_text', ''),
                    "effect": condition.get('effect', '')
                })
        
        return index
    
    def _index_by_defined_term(self, elements: List[Dict]) -> Dict:
        """
        Create an index of elements by defined term.
        
        Args:
            elements: List of elements with language analysis
            
        Returns:
            Index by defined term
        """
        index = {}
        
        for element in elements:
            terms = element.get('term_extraction', {}).get('defined_terms', [])
            
            for term in terms:
                if term not in index:
                    index[term] = []
                
                index[term].append({
                    "id": element.get('id', ''),
                    "type": element.get('type', ''),
                    "section_id": element.get('section_id', '')
                })
        
        return index
    
    def _index_by_challenge(self, elements: List[Dict]) -> Dict:
        """
        Create an index of elements by interpretation challenge.
        
        Args:
            elements: List of elements with language analysis
            
        Returns:
            Index by interpretation challenge
        """
        index = {
            "complex_conditions": [],
            "low_confidence": [],
            "mixed_operators": [],
            "multiple_defined_terms": []
        }
        
        for element in elements:
            # Check for complex conditions
            has_complex_conditions = element.get('conditional_analysis', {}).get('has_complex_conditions', False)
            if has_complex_conditions:
                index["complex_conditions"].append({
                    "id": element.get('id', ''),
                    "type": element.get('type', '')
                })
            
            # Check for low confidence
            intent_confidence = element.get('intent_analysis', {}).get('intent_confidence', 1.0)
            if intent_confidence < 0.7:
                index["low_confidence"].append({
                    "id": element.get('id', ''),
                    "type": element.get('type', ''),
                    "confidence": intent_confidence
                })
            
            # Check for mixed operators
            logical_operators = element.get('term_extraction', {}).get('logical_operators', [])
            if 'and' in logical_operators and 'or' in logical_operators:
                index["mixed_operators"].append({
                    "id": element.get('id', ''),
                    "type": element.get('type', '')
                })
            
            # Check for multiple defined terms
            defined_terms = element.get('term_extraction', {}).get('defined_terms', [])
            if len(defined_terms) > 3:
                index["multiple_defined_terms"].append({
                    "id": element.get('id', ''),
                    "type": element.get('type', ''),
                    "term_count": len(defined_terms)
                })
        
        return index