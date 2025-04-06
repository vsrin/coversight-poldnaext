"""
Conflict identifier module for the Policy DNA Extractor.

This module identifies potential conflicts or contradictions in policy language.
"""

import re
from typing import Dict, List, Set, Tuple, Optional

class ConflictIdentifier:
    """
    Identifies potential conflicts or contradictions between policy elements.
    """
    def __init__(self, config, llm_client):
        """
        Initialize the ConflictIdentifier.
        
        Args:
            config: Application configuration
            llm_client: LLM client for conflict analysis
        """
        self.config = config
        self.llm_client = llm_client
        
        # Define conflict patterns to look for
        self.conflict_patterns = {
            'contradicting_provisions': {
                'weight': 0.9,
                'description': 'Elements with directly contradicting language or effects'
            },
            'scope_overlap': {
                'weight': 0.8,
                'description': 'Elements with overlapping scope but different effects'
            },
            'definition_mismatch': {
                'weight': 0.7,
                'description': 'Terms used inconsistently with their definitions'
            },
            'condition_exclusion_conflict': {
                'weight': 0.8,
                'description': 'Conditions that conflict with exclusions'
            },
            'extension_exclusion_conflict': {
                'weight': 0.8,
                'description': 'Extensions that conflict with exclusions'
            },
            'ambiguous_precedence': {
                'weight': 0.6,
                'description': 'Unclear precedence between conflicting provisions'
            }
        }
    
    def identify_conflicts(self, document_map: Dict, dependencies_data: Dict) -> Dict:
        """
        Identify potential conflicts in the policy.
        
        Args:
            document_map: Complete document map with elements and language analysis
            dependencies_data: Output from DependencyAnalyzer
            
        Returns:
            Dictionary containing conflict analysis results
        """
        print("  Identifying dependency conflicts...")
        dependency_conflicts = self._identify_dependency_conflicts(document_map, dependencies_data)
        print(f"  Found {len(dependency_conflicts)} dependency conflicts")
        
        print("  Identifying semantic conflicts...")
        semantic_conflicts = self._identify_semantic_conflicts(document_map)
        print(f"  Found {len(semantic_conflicts)} semantic conflicts")
        
        print("  Identifying circular references...")
        circular_conflicts = self._identify_circular_references(dependencies_data)
        print(f"  Found {len(circular_conflicts)} circular reference conflicts")
        
        # Combine all conflicts
        all_conflicts = dependency_conflicts + semantic_conflicts + circular_conflicts
        
        # Add conflict IDs for tracking
        for i, conflict in enumerate(all_conflicts):
            conflict['conflict_id'] = f"CONFLICT-{i+1:04d}"
        
        # Sort conflicts by severity
        sorted_conflicts = sorted(all_conflicts, key=lambda c: c.get('severity', 0), reverse=True)
        
        # Count conflict types
        conflict_type_counts = {}
        for conflict in sorted_conflicts:
            conflict_type = conflict.get('conflict_type', 'unknown')
            conflict_type_counts[conflict_type] = conflict_type_counts.get(conflict_type, 0) + 1
        
        # Create final result
        result = {
            "conflicts": sorted_conflicts,
            "conflict_type_counts": conflict_type_counts,
            "total_conflicts": len(sorted_conflicts)
        }
        
        return result
    
    def _identify_dependency_conflicts(self, document_map: Dict, dependencies_data: Dict) -> List[Dict]:
        """
        Identify conflicts based on contradictory dependencies.
        
        Args:
            document_map: Document map with elements
            dependencies_data: Output from DependencyAnalyzer
            
        Returns:
            List of dependency conflicts
        """
        conflicts = []
        
        # Skip if no dependencies
        if not dependencies_data or 'dependencies' not in dependencies_data:
            return conflicts
        
        # Get elements for lookup
        elements_by_id = {}
        for element in document_map.get('elements', []):
            element_id = element.get('id')
            if element_id:
                elements_by_id[element_id] = element
        
        # Group dependencies by target element
        target_dependencies = {}
        for dep in dependencies_data.get('dependencies', []):
            target_id = dep.get('target_id')
            
            if target_id and target_id in elements_by_id:
                if target_id not in target_dependencies:
                    target_dependencies[target_id] = []
                target_dependencies[target_id].append(dep)
        
        # Define conflicting dependency types
        conflicting_pairs = [
            ('extends', 'restricts'),
            ('modifies', 'restricts'),
            ('requires', 'restricts')
        ]
        
        # Check each target with multiple dependencies
        for target_id, deps in target_dependencies.items():
            if len(deps) < 2:
                continue
                
            target_element = elements_by_id.get(target_id)
            
            # Check all pairs of dependencies
            for i, dep1 in enumerate(deps):
                for dep2 in deps[i+1:]:
                    dep1_type = dep1.get('dependency_type', '')
                    dep2_type = dep2.get('dependency_type', '')
                    
                    # Check if dependency types conflict
                    is_conflicting = (dep1_type, dep2_type) in conflicting_pairs or \
                                    (dep2_type, dep1_type) in conflicting_pairs
                    
                    if is_conflicting:
                        source1_id = dep1.get('source_id')
                        source2_id = dep2.get('source_id')
                        
                        # Get source elements
                        source1 = elements_by_id.get(source1_id)
                        source2 = elements_by_id.get(source2_id)
                        
                        if not source1 or not source2:
                            continue
                        
                        # Determine conflict type
                        conflict_type = 'contradicting_provisions'
                        if ('extends' in (dep1_type, dep2_type)) and ('restricts' in (dep1_type, dep2_type)):
                            conflict_type = 'extension_exclusion_conflict'
                        elif ('requires' in (dep1_type, dep2_type)) and ('restricts' in (dep1_type, dep2_type)):
                            conflict_type = 'condition_exclusion_conflict'
                        
                        # Create conflict record
                        conflict = {
                            'conflict_type': conflict_type,
                            'conflicting_elements': [
                                {
                                    'element_id': source1_id,
                                    'element_type': source1.get('type', ''),
                                    'element_text': source1.get('text', '')[:150] + '...'
                                },
                                {
                                    'element_id': source2_id,
                                    'element_type': source2.get('type', ''),
                                    'element_text': source2.get('text', '')[:150] + '...'
                                }
                            ],
                            'target_element': {
                                'element_id': target_id,
                                'element_type': target_element.get('type', ''),
                                'element_text': target_element.get('text', '')[:150] + '...'
                            },
                            'description': f"Conflicting dependencies: {dep1_type} vs {dep2_type} on same target",
                            'dependency_ids': [dep1.get('dependency_id'), dep2.get('dependency_id')],
                            'severity': self.conflict_patterns.get(conflict_type, {}).get('weight', 0.7)
                        }
                        
                        conflicts.append(conflict)
        
        return conflicts
    
    def _identify_semantic_conflicts(self, document_map: Dict) -> List[Dict]:
        """
        Identify semantic conflicts using language analysis.
        
        Args:
            document_map: Document map with language analysis
            
        Returns:
            List of semantic conflicts
        """
        conflicts = []
        elements = document_map.get('elements', [])
        
        # Check for language analysis
        language_analysis = document_map.get('elements_with_language_analysis', [])
        if not language_analysis:
            # Try to use interpretation challenges from language insights as a fallback
            if 'language_insights' in document_map and 'interpretation_challenges' in document_map['language_insights']:
                return self._convert_challenges_to_conflicts(document_map['language_insights']['interpretation_challenges'])
            return conflicts
        
        # Extract elements by ID for lookup
        elements_by_id = {}
        for element in elements:
            element_id = element.get('id')
            if element_id:
                elements_by_id[element_id] = element
        
        # Group elements by type for analysis
        elements_by_type = {}
        for element in elements:
            element_type = element.get('type')
            if element_type:
                if element_type not in elements_by_type:
                    elements_by_type[element_type] = []
                elements_by_type[element_type].append(element)
        
        # Identify conflicts between coverage grants and exclusions
        self._analyze_coverage_exclusion_conflicts(
            elements_by_type.get('COVERAGE_GRANT', []),
            elements_by_type.get('EXCLUSION', []),
            conflicts,
            elements_by_id
        )
        
        # Identify conflicts between extensions and exclusions
        self._analyze_extension_exclusion_conflicts(
            elements_by_type.get('EXTENSION', []),
            elements_by_type.get('EXCLUSION', []),
            conflicts,
            elements_by_id
        )
        
        # Identify definition conflicts
        self._analyze_definition_conflicts(
            elements_by_type.get('DEFINITION', []),
            elements,
            conflicts,
            elements_by_id
        )
        
        return conflicts
    
    def _analyze_coverage_exclusion_conflicts(self, coverage_elements, exclusion_elements, conflicts, elements_by_id):
        """
        Analyze conflicts between coverage grants and exclusions.
        
        Args:
            coverage_elements: List of coverage grant elements
            exclusion_elements: List of exclusion elements
            conflicts: List to append conflicts to
            elements_by_id: Elements by ID for lookup
        """
        if not coverage_elements or not exclusion_elements:
            return
        
        # Process in batches to handle larger documents
        batch_size = min(5, len(coverage_elements))
        for i in range(0, len(coverage_elements), batch_size):
            # Create batch of coverage elements
            coverage_batch = coverage_elements[i:i+batch_size]
            
            # Use LLM to identify conflicts
            prompt = self._create_conflict_analysis_prompt(coverage_batch, exclusion_elements)
            
            try:
                results = self.llm_client.call_llm_with_structured_output(
                    prompt=prompt,
                    output_schema={
                        "type": "object",
                        "properties": {
                            "conflicts": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "coverage_id": {"type": "string"},
                                        "exclusion_id": {"type": "string"},
                                        "description": {"type": "string"},
                                        "severity": {"type": "number", "minimum": 0, "maximum": 1}
                                    },
                                    "required": ["coverage_id", "exclusion_id", "description"]
                                }
                            }
                        }
                    }
                )
                
                # Process results
                if results and "conflicts" in results:
                    for conflict in results["conflicts"]:
                        coverage_id = conflict.get("coverage_id")
                        exclusion_id = conflict.get("exclusion_id")
                        
                        coverage = elements_by_id.get(coverage_id)
                        exclusion = elements_by_id.get(exclusion_id)
                        
                        if coverage and exclusion:
                            conflicts.append({
                                'conflict_type': 'contradicting_provisions',
                                'conflicting_elements': [
                                    {
                                        'element_id': coverage_id,
                                        'element_type': 'COVERAGE_GRANT',
                                        'element_text': coverage.get('text', '')[:150] + '...'
                                    },
                                    {
                                        'element_id': exclusion_id,
                                        'element_type': 'EXCLUSION',
                                        'element_text': exclusion.get('text', '')[:150] + '...'
                                    }
                                ],
                                'description': conflict.get("description", "Potential conflict between coverage grant and exclusion"),
                                'severity': conflict.get("severity", 0.8)
                            })
            
            except Exception as e:
                print(f"  Error analyzing coverage-exclusion conflicts: {str(e)}")
    
    def _analyze_extension_exclusion_conflicts(self, extension_elements, exclusion_elements, conflicts, elements_by_id):
        """
        Analyze conflicts between extensions and exclusions.
        
        Args:
            extension_elements: List of extension elements
            exclusion_elements: List of exclusion elements
            conflicts: List to append conflicts to
            elements_by_id: Elements by ID for lookup
        """
        if not extension_elements or not exclusion_elements:
            return
        
        # Simple keyword-based approach for demonstration
        for extension in extension_elements:
            extension_id = extension.get('id')
            extension_text = extension.get('text', '').lower()
            extension_keywords = extension.get('keywords', [])
            
            for exclusion in exclusion_elements:
                exclusion_id = exclusion.get('id')
                exclusion_text = exclusion.get('text', '').lower()
                exclusion_keywords = exclusion.get('keywords', [])
                
                # Check for keyword overlap
                common_keywords = set(k.lower() for k in extension_keywords) & set(k.lower() for k in exclusion_keywords)
                
                if common_keywords:
                    conflicts.append({
                        'conflict_type': 'extension_exclusion_conflict',
                        'conflicting_elements': [
                            {
                                'element_id': extension_id,
                                'element_type': 'EXTENSION',
                                'element_text': extension.get('text', '')[:150] + '...'
                            },
                            {
                                'element_id': exclusion_id,
                                'element_type': 'EXCLUSION',
                                'element_text': exclusion.get('text', '')[:150] + '...'
                            }
                        ],
                        'description': f"Potential conflict between extension and exclusion (common terms: {', '.join(common_keywords)})",
                        'common_keywords': list(common_keywords),
                        'severity': 0.7
                    })
    
    def _analyze_definition_conflicts(self, definition_elements, all_elements, conflicts, elements_by_id):
        """
        Analyze conflicts related to defined terms.
        
        Args:
            definition_elements: List of definition elements
            all_elements: All elements in the document
            conflicts: List to append conflicts to
            elements_by_id: Elements by ID for lookup
        """
        if not definition_elements:
            return
        
        # Extract defined terms
        defined_terms = {}
        for definition in definition_elements:
            definition_id = definition.get('id')
            definition_text = definition.get('text', '')
            
            # Simple regex to extract the defined term (could be improved)
            match = re.search(r'"([^"]+)"|\'([^\']+)\'|([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', definition_text)
            if match:
                term = match.group(1) or match.group(2) or match.group(3)
                defined_terms[term.lower()] = {
                    'definition_id': definition_id,
                    'definition_text': definition_text
                }
        
        # Check for inconsistent usage of defined terms
        for element in all_elements:
            element_id = element.get('id')
            element_type = element.get('type')
            element_text = element.get('text', '')
            
            # Skip definitions
            if element_type == 'DEFINITION':
                continue
                
            # Check for usage of defined terms
            for term, term_info in defined_terms.items():
                if term in element_text.lower():
                    # Check if term is used inconsistently
                    if self._check_inconsistent_term_usage(term, term_info['definition_text'], element_text):
                        definition = elements_by_id.get(term_info['definition_id'])
                        
                        if definition:
                            conflicts.append({
                                'conflict_type': 'definition_mismatch',
                                'conflicting_elements': [
                                    {
                                        'element_id': term_info['definition_id'],
                                        'element_type': 'DEFINITION',
                                        'element_text': definition.get('text', '')[:150] + '...'
                                    },
                                    {
                                        'element_id': element_id,
                                        'element_type': element_type,
                                        'element_text': element_text[:150] + '...'
                                    }
                                ],
                                'term': term,
                                'description': f"Term '{term}' may be used inconsistently with its definition",
                                'severity': 0.7
                            })
    
    def _check_inconsistent_term_usage(self, term, definition_text, usage_text):
        """
        Check if a term is used inconsistently with its definition.
        
        Args:
            term: The defined term
            definition_text: The definition text
            usage_text: The text where the term is used
            
        Returns:
            True if potentially inconsistent, False otherwise
        """
        # This is a simplified implementation that could be improved with more sophisticated analysis
        # For now, we'll check if the term is used with qualifiers that might change its meaning
        
        term_pattern = re.escape(term)
        modifiers = ["not", "except", "excluding", "other than", "subject to", "notwithstanding"]
        
        for modifier in modifiers:
            # Check if the term is used with the modifier
            if re.search(rf'{modifier}\s+(?:[a-z\s]+\s+)?{term_pattern}', usage_text, re.IGNORECASE):
                return True
        
        return False
    
    def _identify_circular_references(self, dependencies_data: Dict) -> List[Dict]:
        """
        Identify circular references in the dependency chains.
        
        Args:
            dependencies_data: Output from DependencyAnalyzer
            
        Returns:
            List of circular reference conflicts
        """
        conflicts = []
        
        # Check for dependency chains
        chains = dependencies_data.get('dependency_chains', [])
        if not chains:
            return conflicts
        
        # Check each chain for circularity
        for chain in chains:
            path = chain.get('path', [])
            
            if len(path) < 2:
                continue
                
            start_node = chain.get('start_node')
            end_node = chain.get('end_node')
            
            # A circular reference exists if the start node depends on the end node
            # and the end node depends (directly or indirectly) back on the start node
            if start_node and end_node:
                # Check if any element in the path targets the start node
                targets_start = any(dep.get('target_id') == start_node for dep in path)
                
                if targets_start:
                    conflicts.append({
                        'conflict_type': 'ambiguous_precedence',
                        'chain': {
                            'start_node': start_node,
                            'end_node': end_node,
                            'path': path,
                            'length': chain.get('length', 0)
                        },
                        'description': "Circular dependency creates ambiguous precedence",
                        'severity': 0.6
                    })
        
        return conflicts
    
    def _convert_challenges_to_conflicts(self, challenges: List[Dict]) -> List[Dict]:
        """
        Convert interpretation challenges to conflicts.
        
        Args:
            challenges: List of interpretation challenges
            
        Returns:
            List of conflicts
        """
        conflicts = []
        
        for i, challenge in enumerate(challenges):
            conflicts.append({
                'conflict_id': f"CONFLICT-AUTO-{i+1:04d}",
                'conflict_type': 'contradicting_provisions',
                'description': challenge.get('description', 'Potential interpretation challenge'),
                'elements': challenge.get('elements', []),
                'severity': 0.6
            })
        
        return conflicts
    
    def _create_conflict_analysis_prompt(self, coverage_elements, exclusion_elements):
        """
        Create a prompt for conflict analysis.
        
        Args:
            coverage_elements: Coverage grant elements
            exclusion_elements: Exclusion elements
            
        Returns:
            Prompt for LLM
        """
        prompt = "I need to identify potential conflicts between coverage grants and exclusions in an insurance policy.\n\n"
        
        # Format coverage elements
        prompt += "COVERAGE GRANTS:\n"
        for i, element in enumerate(coverage_elements):
            prompt += f"Coverage {i+1} [ID: {element.get('id')}]: {element.get('text', '')[:250]}...\n\n"
        
        # Format exclusion elements (limit to avoid token limits)
        max_exclusions = min(10, len(exclusion_elements))
        prompt += "\nEXCLUSIONS:\n"
        for i, element in enumerate(exclusion_elements[:max_exclusions]):
            prompt += f"Exclusion {i+1} [ID: {element.get('id')}]: {element.get('text', '')[:250]}...\n\n"
        
        # Define the task
        prompt += "\nIdentify pairs of coverage grants and exclusions that may conflict with each other. "
        prompt += "A conflict occurs when an exclusion appears to limit or negate coverage that a coverage grant provides, "
        prompt += "creating ambiguity about whether something is covered. "
        prompt += "Focus on substantive conflicts, not just overlapping terminology."
        
        # Define expected output format
        prompt += "\n\nPlease return the results in this JSON format:\n"
        prompt += """
        {
          "conflicts": [
            {
              "coverage_id": "element_id",
              "exclusion_id": "element_id",
              "description": "Description of the potential conflict",
              "severity": 0.8  // 0.0 to 1.0 scale
            }
          ]
        }
        """
        
        return prompt