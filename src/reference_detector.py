"""
Reference detector module for the Policy DNA Extractor.

This module identifies explicit and implicit references between policy elements.
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Any

class ReferenceDetector:
    """
    Detects explicit and implicit references between policy elements.
    """
    def __init__(self, config, llm_client):
        """
        Initialize the ReferenceDetector.
        
        Args:
            config: Application configuration
            llm_client: LLM client for detecting implicit references
        """
        self.config = config
        self.llm_client = llm_client
        
        # Common patterns for explicit references in policy text
        self.reference_patterns = [
            r"pursuant to\s+[^.;]*(Section|Clause|Part|Article|Endorsement|Paragraph)\s+([A-Z0-9\.-]+)",
            r"as (defined|described|set forth|specified) in\s+[^.;]*(Section|Clause|Part|Article|Endorsement|Paragraph)\s+([A-Z0-9\.-]+)",
            r"subject to\s+[^.;]*(Section|Clause|Part|Article|Endorsement|Paragraph)\s+([A-Z0-9\.-]+)",
            r"in accordance with\s+[^.;]*(Section|Clause|Part|Article|Endorsement|Paragraph)\s+([A-Z0-9\.-]+)",
            r"reference is made to\s+[^.;]*(Section|Clause|Part|Article|Endorsement|Paragraph)\s+([A-Z0-9\.-]+)",
            r"refer to\s+[^.;]*(Section|Clause|Part|Article|Endorsement|Paragraph)\s+([A-Z0-9\.-]+)"
        ]
        
        # Pattern for defined terms in policy text (typically in quotes or capitalized)
        self.defined_term_patterns = [
            r'"([^"]+)"',
            r"'([^']+)'",
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'  # Capitalized multi-word terms
        ]
    
    def detect_references(self, document_map: Dict) -> Dict:
        """
        Main method to detect all references within a policy document.
        
        Args:
            document_map: Complete document map with elements
            
        Returns:
            Dict containing detected references and metadata
        """
        print("  Detecting explicit references...")
        explicit_references = self._detect_explicit_references(document_map)
        print(f"  Found {len(explicit_references)} explicit references")
        
        print("  Detecting defined term references...")
        defined_term_references = self._detect_defined_term_references(document_map)
        print(f"  Found {len(defined_term_references)} defined term references")
        
        print("  Detecting implicit references...")
        implicit_references = self._detect_implicit_references(document_map)
        print(f"  Found {len(implicit_references)} implicit references")
        
        # Combine all references
        all_references = explicit_references + defined_term_references + implicit_references
        
        # Add reference IDs for tracking
        for i, ref in enumerate(all_references):
            ref['reference_id'] = f"REF-{i+1:04d}"
        
        # Add reference type counts
        reference_type_counts = {}
        for ref in all_references:
            ref_type = ref.get('reference_type', 'unknown')
            reference_type_counts[ref_type] = reference_type_counts.get(ref_type, 0) + 1
        
        # Create final result structure
        result = {
            "references": all_references,
            "reference_type_counts": reference_type_counts,
            "total_references": len(all_references)
        }
        
        return result
    
    def _detect_explicit_references(self, document_map: Dict) -> List[Dict]:
        """
        Detects explicit references using regex patterns.
        
        Args:
            document_map: Document map with all elements
            
        Returns:
            List of explicit references
        """
        references = []
        elements = document_map.get('elements', [])
        
        # Create a mapping of section IDs and identifiers for resolving references
        section_map = self._create_section_mapping(document_map)
        
        # Process each element to find explicit references
        for element in elements:
            element_id = element.get('id')
            element_text = element.get('text', '')
            
            # Skip if no text or ID
            if not element_id or not element_text:
                continue
            
            # Check for section references using regex patterns
            for pattern in self.reference_patterns:
                matches = re.finditer(pattern, element_text, re.IGNORECASE)
                
                for match in matches:
                    # Extract the referenced section
                    if len(match.groups()) >= 2:
                        section_type = match.group(1)  # Section, Clause, etc.
                        section_ref = match.group(2)   # Section number or identifier
                        
                        # Try to find the target element by section number
                        target_elements = self._find_elements_by_section_ref(elements, section_ref, section_map)
                        
                        if target_elements:
                            for target in target_elements:
                                references.append({
                                    'source_id': element_id,
                                    'target_id': target.get('id'),
                                    'reference_type': 'explicit_section',
                                    'section_type': section_type,
                                    'section_reference': section_ref,
                                    'reference_text': match.group(0),
                                    'confidence': 0.9
                                })
                        else:
                            # Reference exists but target not found
                            references.append({
                                'source_id': element_id,
                                'target_id': None,
                                'reference_type': 'unresolved_section',
                                'section_type': section_type,
                                'section_reference': section_ref,
                                'reference_text': match.group(0),
                                'confidence': 0.7
                            })
        
        return references
    
    def _detect_defined_term_references(self, document_map: Dict) -> List[Dict]:
        """
        Detects references to defined terms in the policy.
        
        Args:
            document_map: Document map with all elements
            
        Returns:
            List of defined term references
        """
        references = []
        elements = document_map.get('elements', [])
        
        # First, extract all defined terms
        defined_terms = self._extract_defined_terms(elements)
        
        # Then, find references to defined terms in other elements
        for element in elements:
            element_id = element.get('id')
            element_type = element.get('type')
            element_text = element.get('text', '')
            
            # Skip definition elements to avoid self-references
            if element_type == 'DEFINITION':
                continue
            
            # Look for each defined term in the element text
            for term, term_info in defined_terms.items():
                term_pattern = rf'\b{re.escape(term)}\b'
                matches = re.finditer(term_pattern, element_text, re.IGNORECASE)
                
                # Collect positions of all matches to avoid duplicates
                match_positions = []
                for match in matches:
                    start, end = match.span()
                    match_positions.append((start, end))
                
                # Create a reference for each unique match
                for start, end in match_positions:
                    references.append({
                        'source_id': element_id,
                        'target_id': term_info['element_id'],
                        'reference_type': 'defined_term',
                        'term': term,
                        'reference_text': element_text[start:end],
                        'position': {"start": start, "end": end},
                        'confidence': 0.85
                    })
        
        return references
    
    def _detect_implicit_references(self, document_map: Dict) -> List[Dict]:
        """
        Detects implicit semantic references between policy elements using LLM.
        
        Args:
            document_map: Document map with all elements
            
        Returns:
            List of implicit references
        """
        references = []
        elements = document_map.get('elements', [])
        
        # Create groups of elements by type for more efficient processing
        element_groups = self._group_elements_by_type(elements)
        
        # Process related element groups
        related_pairs = [
            ('COVERAGE_GRANT', 'EXCLUSION'),
            ('COVERAGE_GRANT', 'CONDITION'),
            ('EXCLUSION', 'EXCEPTION'),
            ('CONDITION', 'EXCLUSION'),
            ('DEFINITION', 'COVERAGE_GRANT')
        ]
        
        for source_type, target_type in related_pairs:
            source_elements = element_groups.get(source_type, [])
            target_elements = element_groups.get(target_type, [])
            
            if not source_elements or not target_elements:
                continue
                
            # Process in batches to avoid token limits
            batch_size = min(5, len(source_elements))
            for i in range(0, len(source_elements), batch_size):
                source_batch = source_elements[i:i+batch_size]
                batch_references = self._find_implicit_references_batch(
                    source_batch, target_elements, source_type, target_type
                )
                references.extend(batch_references)
        
        return references
    
    def _find_implicit_references_batch(self, source_elements, target_elements, source_type, target_type):
        """
        Find implicit references between a batch of source elements and target elements.
        
        Args:
            source_elements: List of source elements
            target_elements: List of target elements
            source_type: Type of source elements
            target_type: Type of target elements
            
        Returns:
            List of implicit references
        """
        references = []
        
        # Prepare context for LLM prompt
        context = "I'll analyze insurance policy elements to find implicit semantic references.\n\n"
        
        # Format source elements
        context += f"SOURCE ELEMENTS ({source_type}):\n"
        for i, element in enumerate(source_elements):
            context += f"Source {i+1} [ID: {element.get('id')}]: {element.get('text', '')[:300]}...\n\n"
        
        # Format target elements (limit number to avoid token limits)
        max_targets = min(10, len(target_elements))
        context += f"\nTARGET ELEMENTS ({target_type}):\n"
        for i, element in enumerate(target_elements[:max_targets]):
            context += f"Target {i+1} [ID: {element.get('id')}]: {element.get('text', '')[:300]}...\n\n"
        
        # Define the task
        instruction = (
            f"Identify which source elements implicitly reference or depend on which target elements. "
            f"Focus on semantic connections, not just keyword matches. "
            f"Return only pairs where there's a clear logical dependency or reference."
        )
        
        # Prepare expected output format
        output_format = """
        {
          "implicit_references": [
            {
              "source_id": "element_id",
              "target_id": "element_id",
              "reference_type": "semantic_dependency",  // Or other appropriate type
              "connection_description": "Brief description of how they are connected",
              "confidence": 0.7  // 0.0 to 1.0 scale
            }
          ]
        }
        """
        
        # Build complete prompt
        prompt = f"{context}\n\n{instruction}\n\nPlease return the results in this JSON format:\n{output_format}"
        
        try:
            # Call LLM to find references
            results = self.llm_client.call_llm_with_structured_output(
                prompt=prompt,
                output_schema={
                    "type": "object",
                    "properties": {
                        "implicit_references": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "source_id": {"type": "string"},
                                    "target_id": {"type": "string"},
                                    "reference_type": {"type": "string"},
                                    "connection_description": {"type": "string"},
                                    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                                },
                                "required": ["source_id", "target_id"]
                            }
                        }
                    },
                    "required": ["implicit_references"]
                }
            )
            
            # Process results
            if results and "implicit_references" in results:
                for ref in results["implicit_references"]:
                    # Validate source_id and target_id
                    source_id = ref.get("source_id")
                    target_id = ref.get("target_id")
                    
                    # Only add valid references
                    if source_id and target_id:
                        ref["reference_type"] = ref.get("reference_type", "semantic_dependency")
                        references.append(ref)
        
        except Exception as e:
            print(f"  Error detecting implicit references: {str(e)}")
        
        return references
    
    def _create_section_mapping(self, document_map: Dict) -> Dict:
        """
        Create a mapping of section identifiers to section IDs.
        
        Args:
            document_map: Document map with sections
            
        Returns:
            Mapping of section numbers and titles to section IDs
        """
        section_map = {}
        
        for section in document_map.get('sections', []):
            section_id = section.get('id')
            section_number = section.get('section_number')
            section_title = section.get('title')
            
            if section_id:
                # Map by section number if available
                if section_number:
                    section_map[section_number.lower()] = section_id
                
                # Map by section title if available
                if section_title:
                    # Clean up title for matching
                    clean_title = re.sub(r'[^a-zA-Z0-9]', '', section_title.lower())
                    section_map[clean_title] = section_id
        
        return section_map
    
    def _find_elements_by_section_ref(self, elements, section_ref, section_map):
        """
        Find elements that belong to a referenced section.
        
        Args:
            elements: List of all elements
            section_ref: Section reference (number or name)
            section_map: Mapping of section identifiers to section IDs
            
        Returns:
            List of elements in the referenced section
        """
        # Clean up the section reference for matching
        clean_ref = section_ref.lower()
        
        # Try to find the section ID in the mapping
        section_id = section_map.get(clean_ref)
        
        if section_id:
            # Return all elements in this section
            return [e for e in elements if e.get('section_id') == section_id]
        
        # If not found in mapping, try direct matching with elements
        matched_elements = []
        for element in elements:
            if element.get('section_number', '').lower() == clean_ref:
                matched_elements.append(element)
        
        return matched_elements
    
    def _extract_defined_terms(self, elements):
        """
        Extract all defined terms from definition elements.
        
        Args:
            elements: List of all elements
            
        Returns:
            Dictionary of defined terms and their metadata
        """
        defined_terms = {}
        
        for element in elements:
            element_id = element.get('id')
            element_type = element.get('type')
            element_text = element.get('text', '')
            
            if element_type == 'DEFINITION':
                # Try each pattern to extract the defined term
                for pattern in self.defined_term_patterns:
                    matches = re.finditer(pattern, element_text)
                    for match in matches:
                        term = match.group(1)
                        
                        # Store only if term has reasonable length
                        if term and 2 <= len(term) <= 50:
                            defined_terms[term.lower()] = {
                                'element_id': element_id,
                                'term': term,
                                'definition_text': element_text[:100]  # Store first 100 chars
                            }
                            break  # Stop after finding the first match
                
                # If no match found with patterns, try extracting from the first sentence
                if not any(t.lower() in defined_terms for t in element_text.split()):
                    first_sentence = element_text.split('.')[0] if '.' in element_text else element_text
                    words = first_sentence.split()
                    
                    # Look for patterns like "Term means..."
                    for i, word in enumerate(words):
                        if i+1 < len(words) and words[i+1].lower() in ['means', 'is', 'refers']:
                            term = word.strip('"\'.,;:')
                            
                            # Store only if term has reasonable length
                            if term and 2 <= len(term) <= 50:
                                defined_terms[term.lower()] = {
                                    'element_id': element_id,
                                    'term': term,
                                    'definition_text': element_text[:100]
                                }
                                break
                    
        return defined_terms
    
    def _group_elements_by_type(self, elements):
        """
        Group elements by their type for more efficient processing.
        
        Args:
            elements: List of all elements
            
        Returns:
            Dictionary of elements grouped by type
        """
        grouped = {}
        
        for element in elements:
            element_type = element.get('type')
            if element_type:
                if element_type not in grouped:
                    grouped[element_type] = []
                grouped[element_type].append(element)
        
        return grouped