"""
Element relationship analyzer module for identifying connections between policy elements.
"""

import json
from typing import Dict, List, Optional, Any

class ElementRelationshipAnalyzer:
    """Analyzes relationships between policy elements."""
    
    # Define relationship types
    RELATIONSHIP_TYPES = [
        "PARENT_CHILD",     # One element contains or encompasses another
        "REFERENCE",        # One element refers to another
        "DEPENDENCY",       # One element's application depends on another
        "MODIFICATION"      # One element modifies or limits another
    ]
    
    def __init__(self, llm_client):
        """
        Initialize the relationship analyzer.
        
        Args:
            llm_client: Client for the LLM
        """
        self.llm_client = llm_client
        self.prompts = self._load_prompts()
    
    def _load_prompts(self):
        """Load prompt templates for relationship analysis."""
        return {
            "relationships": """
            # Insurance Policy Element Relationship Analysis
            
            ## Your Task
            Analyze the insurance policy elements below from the same section and identify hierarchical and referential relationships between them.
            
            ## Section Type: {section_type}
            ## Section Title: {section_title}
            
            ## Elements:
            {elements_json}
            
            ## Types of Relationships to Identify
            1. Parent-Child: One element contains or encompasses another
            2. Reference: One element refers to another
            3. Dependency: One element's application depends on another
            4. Modification: One element modifies or limits another
            
            ## Expected Output Format
            Provide your analysis as a JSON array of relationships:
            ```json
            [
              {{
                "relationship_type": "PARENT_CHILD",
                "parent_id": "element_id_of_parent",
                "child_id": "element_id_of_child",
                "explanation": "Why these elements have this relationship"
              }},
              {{
                "relationship_type": "REFERENCE",
                "source_id": "element_id_that_contains_reference",
                "target_id": "element_id_being_referenced",
                "explanation": "Nature of the reference"
              }},
              {{
                "relationship_type": "DEPENDENCY",
                "dependent_id": "element_id_that_depends",
                "dependency_id": "element_id_depended_upon",
                "explanation": "Nature of the dependency"
              }},
              {{
                "relationship_type": "MODIFICATION",
                "modifier_id": "element_id_that_modifies",
                "modified_id": "element_id_being_modified",
                "explanation": "How the modification works"
              }}
            ]
            ```
            
            ## Guidelines
            - Focus on substantive relationships, not just textual proximity
            - Identify nested structures (parent-child relationships)
            - Note when one element explicitly references another
            - Identify when elements contain conditions that affect other elements
            - If no clear relationships exist, return an empty array
            
            Return only the JSON array with no additional text.
            """
        }
    
    def analyze_relationships(self, elements: List[Dict], section: Dict) -> List[Dict]:
        """
        Analyze relationships between elements in a section.
        
        Args:
            elements: List of elements to analyze
            section: The section containing these elements
            
        Returns:
            Updated elements with relationship information
        """
        # Skip relationship analysis if there are fewer than 2 elements
        if len(elements) < 2:
            return elements
            
        # Apply basic structural heuristics first
        elements = self._apply_structural_heuristics(elements)
        
        # Prepare elements summary for the prompt
        elements_summary = []
        for element in elements:
            elements_summary.append({
                "id": element.get('id'),
                "type": element.get('type', 'UNKNOWN'),
                "text": element.get('text', '')[:300]  # Limit text length
            })
        
        # Prepare prompt for relationship analysis
        prompt = self.prompts["relationships"].format(
            section_type=section.get('classification', {}).get('classification', 'UNKNOWN'),
            section_title=section.get('title', 'Untitled Section'),
            elements_json=json.dumps(elements_summary, indent=2)
        )
        
        # Call LLM for relationship analysis
        response = self.llm_client.generate(prompt)
        
        # Parse relationships and update elements
        try:
            cleaned_response = self._clean_json_response(response)
            relationships = json.loads(cleaned_response)
            
            # Update elements with relationship information
            elements_by_id = {element['id']: element for element in elements}
            
            for relationship in relationships:
                relationship_type = relationship.get('relationship_type')
                
                if relationship_type == 'PARENT_CHILD':
                    parent_id = relationship.get('parent_id')
                    child_id = relationship.get('child_id')
                    
                    if parent_id in elements_by_id and child_id in elements_by_id:
                        # Update child with parent reference
                        elements_by_id[child_id]['parent_element_id'] = parent_id
                        
                        # Update parent with child reference
                        parent = elements_by_id[parent_id]
                        if 'child_element_ids' not in parent:
                            parent['child_element_ids'] = []
                        if child_id not in parent['child_element_ids']:
                            parent['child_element_ids'].append(child_id)
                
                # Handle other relationship types by storing in element metadata
                elif relationship_type == 'REFERENCE':
                    source_id = relationship.get('source_id')
                    target_id = relationship.get('target_id')
                    
                    if source_id in elements_by_id and target_id in elements_by_id:
                        source = elements_by_id[source_id]
                        if 'references' not in source:
                            source['references'] = []
                        source['references'].append({
                            'target_id': target_id,
                            'explanation': relationship.get('explanation', '')
                        })
                
                elif relationship_type == 'DEPENDENCY':
                    dependent_id = relationship.get('dependent_id')
                    dependency_id = relationship.get('dependency_id')
                    
                    if dependent_id in elements_by_id and dependency_id in elements_by_id:
                        dependent = elements_by_id[dependent_id]
                        if 'dependencies' not in dependent:
                            dependent['dependencies'] = []
                        dependent['dependencies'].append({
                            'dependency_id': dependency_id,
                            'explanation': relationship.get('explanation', '')
                        })
                
                elif relationship_type == 'MODIFICATION':
                    modifier_id = relationship.get('modifier_id')
                    modified_id = relationship.get('modified_id')
                    
                    if modifier_id in elements_by_id and modified_id in elements_by_id:
                        modifier = elements_by_id[modifier_id]
                        if 'modifies' not in modifier:
                            modifier['modifies'] = []
                        modifier['modifies'].append({
                            'modified_id': modified_id,
                            'explanation': relationship.get('explanation', '')
                        })
                        
                        modified = elements_by_id[modified_id]
                        if 'modified_by' not in modified:
                            modified['modified_by'] = []
                        modified['modified_by'].append({
                            'modifier_id': modifier_id,
                            'explanation': relationship.get('explanation', '')
                        })
            
            return list(elements_by_id.values())
            
        except json.JSONDecodeError as e:
            print(f"Error parsing relationship analysis response: {str(e)}")
            print(f"Raw response: {response[:200]}...")
            return elements
    
    def _apply_structural_heuristics(self, elements: List[Dict]) -> List[Dict]:
        """
        Apply structural heuristics to identify basic relationships.
        
        Args:
            elements: List of elements to analyze
            
        Returns:
            Elements with basic relationships identified
        """
        # Create dictionary for lookup
        elements_by_id = {element['id']: element for element in elements}
        
        # Look for numbered or lettered elements that suggest parent-child relationships
        import re
        
        # Regular expressions for identifying numbered and lettered items
        number_pattern = r'^(\d+\.|\(\d+\)|\d+\))'
        letter_pattern = r'^([a-zA-Z]\.|\([a-zA-Z]\)|\s[a-zA-Z]\))'
        
        # Identify potential parent elements (often have no numbering or are major numbers)
        parents = []
        children = []
        
        for element in elements:
            text = element.get('text', '').strip()
            # Skip very short elements
            if len(text) < 10:
                continue
                
            # Check for numbering patterns
            has_number = re.match(number_pattern, text)
            has_letter = re.match(letter_pattern, text)
            
            if has_number:
                # Check if it's a major number (likely a parent)
                if text.startswith('1.') or text.startswith('(1)') or text.startswith('1)'):
                    parents.append(element)
                else:
                    children.append(element)
            elif has_letter:
                children.append(element)
            else:
                # Elements without numbering might be parents
                parents.append(element)
        
        # Identify relationships based on sequential numbering
        current_parent = None
        for i, element in enumerate(elements):
            text = element.get('text', '').strip()
            
            # If this is a parent element, set as current parent
            if element in parents and len(text) > 20:  # Ensure it's substantial
                current_parent = element
                continue
                
            # If we have a current parent and this is a child, link them
            if current_parent and element in children:
                element['parent_element_id'] = current_parent['id']
                
                if 'child_element_ids' not in current_parent:
                    current_parent['child_element_ids'] = []
                if element['id'] not in current_parent['child_element_ids']:
                    current_parent['child_element_ids'].append(element['id'])
        
        return elements
    
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
        
        # Handle empty arrays
        if response == "" or response.isspace():
            return "[]"
            
        return response