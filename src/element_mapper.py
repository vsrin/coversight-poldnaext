"""
Element mapper module for creating structured representations of policy elements.
"""

from typing import Dict, List, Optional, Any

class ElementMapper:
    """Maps elements into a structured policy representation."""
    
    def create_element_map(self, all_elements: List[Dict], document_map: Dict) -> Dict:
        """
        Create a structured map of policy elements.
        
        Args:
            all_elements: List of all elements from all sections
            document_map: The document map from previous processing
            
        Returns:
            Enhanced document map with element information
        """
        # Group elements by section
        elements_by_section = {}
        for element in all_elements:
            section_id = element.get('section_id')
            if section_id:
                if section_id not in elements_by_section:
                    elements_by_section[section_id] = []
                elements_by_section[section_id].append(element)
        
        # Add elements to document map
        enhanced_map = document_map.copy()
        
        # Add all elements to the map
        enhanced_map['elements'] = all_elements
        
        # Add element counts by type
        element_counts = self._count_elements_by_type(all_elements)
        enhanced_map['element_counts'] = element_counts
        
        # Add element navigation
        element_navigation = self._create_element_navigation(all_elements)
        enhanced_map['element_navigation'] = element_navigation
        
        # Add elements to their respective sections
        self._add_elements_to_sections(enhanced_map, elements_by_section)
        
        # Add policy insights
        enhanced_map['policy_insights'] = self._generate_policy_insights(all_elements, document_map)
        
        return enhanced_map
    
    def _count_elements_by_type(self, elements: List[Dict]) -> Dict:
        """
        Count elements by type.
        
        Args:
            elements: List of elements
            
        Returns:
            Dictionary of counts by element type
        """
        counts = {}
        
        for element in elements:
            element_type = element.get('type', 'OTHER')
            
            if element_type not in counts:
                counts[element_type] = 0
                
            counts[element_type] += 1
        
        # Add total count
        counts['TOTAL'] = len(elements)
        
        return counts
    
    def _create_element_navigation(self, elements: List[Dict]) -> Dict:
        """
        Create navigation indices for elements.
        
        Args:
            elements: List of elements
            
        Returns:
            Navigation structure for elements
        """
        # Navigation by type
        nav_by_type = {}
        
        for element in elements:
            element_type = element.get('type', 'OTHER')
            
            if element_type not in nav_by_type:
                nav_by_type[element_type] = []
                
            nav_by_type[element_type].append({
                'id': element.get('id', ''),
                'text': element.get('text', '')[:100] + ('...' if len(element.get('text', '')) > 100 else ''),
                'subtype': element.get('subtype', ''),
                'section_id': element.get('section_id', ''),
                'confidence': element.get('confidence', 0.0)
            })
        
        # Navigation by relationship
        relationship_graph = {}
        
        for element in elements:
            element_id = element.get('id')
            parent_id = element.get('parent_element_id')
            child_ids = element.get('child_element_ids', [])
            
            if element_id:
                relationship_graph[element_id] = {
                    'parent': parent_id,
                    'children': child_ids
                }
                
                # Add other relationships if present
                if element.get('references'):
                    relationship_graph[element_id]['references'] = element.get('references')
                if element.get('dependencies'):
                    relationship_graph[element_id]['dependencies'] = element.get('dependencies')
                if element.get('modifies'):
                    relationship_graph[element_id]['modifies'] = element.get('modifies')
                if element.get('modified_by'):
                    relationship_graph[element_id]['modified_by'] = element.get('modified_by')
        
        # Create keyword index
        keyword_index = self._create_keyword_index(elements)
        
        return {
            'by_type': nav_by_type,
            'relationships': relationship_graph,
            'keywords': keyword_index
        }
    
    def _create_keyword_index(self, elements: List[Dict]) -> Dict:
        """
        Create an index of elements by keyword.
        
        Args:
            elements: List of elements
            
        Returns:
            Keyword index
        """
        keyword_index = {}
        
        for element in elements:
            # Skip elements without keywords
            if not element.get('keywords'):
                continue
                
            for keyword in element.get('keywords', []):
                if keyword:
                    keyword_lower = keyword.lower()
                    if keyword_lower not in keyword_index:
                        keyword_index[keyword_lower] = []
                    
                    keyword_index[keyword_lower].append({
                        'id': element.get('id', ''),
                        'type': element.get('type', 'OTHER')
                    })
        
        return keyword_index
    
    def _add_elements_to_sections(self, document_map: Dict, elements_by_section: Dict) -> None:
        """
        Add elements to their respective sections in the document map.
        
        Args:
            document_map: Document map to enhance
            elements_by_section: Dictionary of elements grouped by section ID
        """
        def process_section(section):
            section_id = section.get('id')
            
            if section_id and section_id in elements_by_section:
                section['elements'] = elements_by_section[section_id]
            else:
                section['elements'] = []
            
            # Process child sections recursively
            if 'children' in section:
                for child in section['children']:
                    process_section(child)
        
        # Process all root sections
        for section in document_map.get('sections', []):
            process_section(section)
    
    def _generate_policy_insights(self, elements: List[Dict], document_map: Dict) -> Dict:
        """
        Generate insights about the policy based on extracted elements.
        
        Args:
            elements: List of all elements
            document_map: Original document map
            
        Returns:
            Dictionary of policy insights
        """
        insights = {
            'coverage_summary': self._generate_coverage_summary(elements),
            'key_exclusions': self._identify_key_exclusions(elements),
            'key_definitions': self._identify_key_definitions(elements),
            'monetary_provisions': self._extract_monetary_provisions(elements),
            'reporting_obligations': self._extract_reporting_obligations(elements)
        }
        
        return insights
    
    def _generate_coverage_summary(self, elements: List[Dict]) -> List[Dict]:
        """
        Generate a summary of coverage grants in the policy.
        
        Args:
            elements: List of elements
            
        Returns:
            List of coverage summary items
        """
        coverage_elements = [e for e in elements if e.get('type') == 'COVERAGE_GRANT']
        summary = []
        
        for element in coverage_elements:
            # Skip elements with low confidence
            if element.get('confidence', 0) < 0.7:
                continue
                
            summary.append({
                'id': element.get('id'),
                'text': element.get('text')[:200] + ('...' if len(element.get('text', '')) > 200 else ''),
                'subtype': element.get('subtype', ''),
                'monetary_values': element.get('metadata', {}).get('monetary_values', []),
                'has_conditions': element.get('metadata', {}).get('contains_condition', False)
            })
            
        return summary
    
    def _identify_key_exclusions(self, elements: List[Dict]) -> List[Dict]:
        """
        Identify key exclusions in the policy.
        
        Args:
            elements: List of elements
            
        Returns:
            List of key exclusions
        """
        exclusion_elements = [e for e in elements if e.get('type') == 'EXCLUSION']
        key_exclusions = []
        
        for element in exclusion_elements:
            # Skip elements with low confidence
            if element.get('confidence', 0) < 0.7:
                continue
                
            key_exclusions.append({
                'id': element.get('id'),
                'text': element.get('text')[:200] + ('...' if len(element.get('text', '')) > 200 else ''),
                'subtype': element.get('subtype', '')
            })
            
        return key_exclusions
    
    def _identify_key_definitions(self, elements: List[Dict]) -> List[Dict]:
        """
        Identify key definitions in the policy.
        
        Args:
            elements: List of elements
            
        Returns:
            List of key definitions
        """
        definition_elements = [e for e in elements if e.get('type') == 'DEFINITION']
        key_definitions = []
        
        for element in definition_elements:
            # Extract the term being defined
            import re
            term_match = re.search(r'"([^"]*)"', element.get('text', ''))
            term = term_match.group(1) if term_match else ""
            
            if term:
                key_definitions.append({
                    'id': element.get('id'),
                    'term': term,
                    'definition': element.get('text')[:200] + ('...' if len(element.get('text', '')) > 200 else '')
                })
            
        return key_definitions
    
    def _extract_monetary_provisions(self, elements: List[Dict]) -> List[Dict]:
        """
        Extract provisions with monetary values.
        
        Args:
            elements: List of elements
            
        Returns:
            List of monetary provisions
        """
        monetary_provisions = []
        
        for element in elements:
            metadata = element.get('metadata', {})
            if metadata.get('has_monetary_value') and metadata.get('monetary_values'):
                monetary_provisions.append({
                    'id': element.get('id'),
                    'type': element.get('type'),
                    'subtype': element.get('subtype', ''),
                    'text': element.get('text')[:200] + ('...' if len(element.get('text', '')) > 200 else ''),
                    'monetary_values': metadata.get('monetary_values', [])
                })
                
        return monetary_provisions
    
    def _extract_reporting_obligations(self, elements: List[Dict]) -> List[Dict]:
        """
        Extract reporting obligations.
        
        Args:
            elements: List of elements
            
        Returns:
            List of reporting obligations
        """
        reporting_elements = [e for e in elements if e.get('type') == 'REPORTING_OBLIGATION' 
                              or (e.get('type') == 'CONDITION' and 'report' in e.get('text', '').lower())]
        obligations = []
        
        for element in reporting_elements:
            obligations.append({
                'id': element.get('id'),
                'text': element.get('text')[:200] + ('...' if len(element.get('text', '')) > 200 else ''),
                'time_sensitive': 'day' in element.get('text', '').lower() or 'immediate' in element.get('text', '').lower()
            })
            
        return obligations