"""
Dependency analyzer module for the Policy DNA Extractor.

This module analyzes logical dependencies between policy elements.
"""

import re
from typing import Dict, List, Tuple, Any, Optional

class DependencyAnalyzer:
    """
    Analyzes dependencies between policy elements based on references and semantics.
    """
    def __init__(self, config, llm_client):
        """
        Initialize the DependencyAnalyzer.
        
        Args:
            config: Application configuration
            llm_client: LLM client for semantic analysis
        """
        self.config = config
        self.llm_client = llm_client
        
        # Define dependency type hierarchy and weights
        self.dependency_types = {
            "modifies": 0.9,        # One element changes the meaning of another
            "restricts": 0.8,        # One element limits another (e.g., exclusion)
            "extends": 0.8,          # One element broadens another (e.g., extension)
            "requires": 0.7,         # One element creates a requirement for another
            "references": 0.6,       # Simple reference without strong dependency
            "defines": 0.5,          # Definition relationship
            "clarifies": 0.4,        # One element explains another
            "weak_connection": 0.2   # Elements are related but no clear dependency
        }
    
    def analyze_dependencies(self, document_map: Dict, references_data: Dict) -> Dict:
        """
        Analyze dependencies between policy elements based on references.
        
        Args:
            document_map: Complete document map with elements
            references_data: Output from ReferenceDetector
            
        Returns:
            Dictionary containing dependency analysis results
        """
        print("  Converting references to dependencies...")
        reference_dependencies = self._convert_references_to_dependencies(references_data)
        print(f"  Created {len(reference_dependencies)} reference-based dependencies")
        
        print("  Identifying element type dependencies...")
        type_dependencies = self._identify_element_type_dependencies(document_map)
        print(f"  Found {len(type_dependencies)} element type dependencies")
        
        print("  Analyzing conditional dependencies...")
        conditional_dependencies = self._analyze_conditional_dependencies(document_map)
        print(f"  Found {len(conditional_dependencies)} conditional dependencies")
        
        # Combine all dependencies
        all_dependencies = reference_dependencies + type_dependencies + conditional_dependencies
        
        # Remove duplicates and resolve conflicts
        unique_dependencies = self._deduplicate_dependencies(all_dependencies)
        
        # Add dependency IDs for tracking
        for i, dep in enumerate(unique_dependencies):
            dep['dependency_id'] = f"DEP-{i+1:04d}"
        
        # Create dependency chains
        dependency_chains = self._build_dependency_chains(unique_dependencies)
        
        # Count dependency types
        dependency_type_counts = {}
        for dep in unique_dependencies:
            dep_type = dep.get('dependency_type', 'unknown')
            dependency_type_counts[dep_type] = dependency_type_counts.get(dep_type, 0) + 1
        
        # Create final result
        result = {
            "dependencies": unique_dependencies,
            "dependency_chains": dependency_chains,
            "dependency_type_counts": dependency_type_counts,
            "total_dependencies": len(unique_dependencies)
        }
        
        return result
    
    def _convert_references_to_dependencies(self, references_data: Dict) -> List[Dict]:
        """
        Convert reference data to dependency objects.
        
        Args:
            references_data: Output from ReferenceDetector
            
        Returns:
            List of dependencies derived from references
        """
        dependencies = []
        
        # Skip if no references
        if not references_data or 'references' not in references_data:
            return dependencies
        
        # Process each reference
        for ref in references_data['references']:
            source_id = ref.get('source_id')
            target_id = ref.get('target_id')
            reference_type = ref.get('reference_type', '')
            confidence = ref.get('confidence', 0.5)
            
            # Skip references with no target
            if not source_id or not target_id:
                continue
            
            # Map reference types to dependency types
            dependency_type = self._map_reference_to_dependency_type(reference_type)
            
            # Calculate dependency strength based on confidence and type
            type_weight = self.dependency_types.get(dependency_type, 0.5)
            strength = confidence * type_weight
            
            # Create dependency object
            dependency = {
                'source_id': source_id,
                'target_id': target_id,
                'dependency_type': dependency_type,
                'strength': round(strength, 2),
                'origin': 'reference',
                'reference_data': {
                    'reference_id': ref.get('reference_id'),
                    'reference_type': reference_type,
                    'reference_text': ref.get('reference_text', '')
                }
            }
            
            dependencies.append(dependency)
        
        return dependencies
    
    def _map_reference_to_dependency_type(self, reference_type: str) -> str:
        """
        Map reference types to dependency types.
        
        Args:
            reference_type: Type of reference
            
        Returns:
            Corresponding dependency type
        """
        # Mapping of reference types to dependency types
        mapping = {
            'explicit_section': 'references',
            'defined_term': 'defines',
            'semantic_dependency': 'references',
            'unresolved_section': 'weak_connection'
        }
        
        return mapping.get(reference_type, 'references')
    
    def _identify_element_type_dependencies(self, document_map: Dict) -> List[Dict]:
        """
        Identify dependencies based on element types and their relationships.
        
        Args:
            document_map: Document map with elements
            
        Returns:
            List of dependencies based on element types
        """
        dependencies = []
        elements = document_map.get('elements', [])
        
        # Define relationships between element types
        type_relationships = [
            ('COVERAGE_GRANT', 'EXCLUSION', 'restricts'),
            ('EXCLUSION', 'EXCEPTION', 'modifies'),
            ('COVERAGE_GRANT', 'CONDITION', 'requires'),
            ('COVERAGE_GRANT', 'SUBLIMIT', 'restricts'),
            ('COVERAGE_GRANT', 'EXTENSION', 'extends'),
            ('DEFINITION', 'COVERAGE_GRANT', 'defines')
        ]
        
        # Group elements by type and section
        elements_by_type_and_section = {}
        for element in elements:
            element_type = element.get('type')
            section_id = element.get('section_id')
            
            if element_type and section_id:
                key = (element_type, section_id)
                if key not in elements_by_type_and_section:
                    elements_by_type_and_section[key] = []
                elements_by_type_and_section[key].append(element)
        
        # Find dependencies based on element types within the same section
        for source_type, target_type, dependency_type in type_relationships:
            # Check all sections for this type relationship
            for section_id in set(s_id for _, s_id in elements_by_type_and_section.keys()):
                source_elements = elements_by_type_and_section.get((source_type, section_id), [])
                target_elements = elements_by_type_and_section.get((target_type, section_id), [])
                
                if not source_elements or not target_elements:
                    continue
                
                # Connect elements based on keyword similarity
                for source in source_elements:
                    source_id = source.get('id')
                    source_text = source.get('text', '').lower()
                    source_keywords = source.get('keywords', [])
                    
                    for target in target_elements:
                        target_id = target.get('id')
                        target_text = target.get('text', '').lower()
                        target_keywords = target.get('keywords', [])
                        
                        # Skip self-references
                        if source_id == target_id:
                            continue
                        
                        # Check for keyword matches
                        common_keywords = set(source_keywords) & set(target_keywords)
                        
                        # Check for text similarity (simple keyword check)
                        text_similarity = 0
                        if source_keywords and target_text:
                            for keyword in source_keywords:
                                if keyword.lower() in target_text:
                                    text_similarity += 1
                        
                        # Create dependency if sufficient similarity
                        if common_keywords or text_similarity > 0:
                            strength = min(0.5 + (len(common_keywords) * 0.1) + (text_similarity * 0.05), 0.9)
                            
                            dependencies.append({
                                'source_id': source_id,
                                'target_id': target_id,
                                'dependency_type': dependency_type,
                                'strength': round(strength, 2),
                                'origin': 'element_type',
                                'similarity_data': {
                                    'common_keywords': list(common_keywords),
                                    'text_similarity': text_similarity
                                }
                            })
        
        return dependencies
    
    def _analyze_conditional_dependencies(self, document_map: Dict) -> List[Dict]:
        """
        Analyze dependencies based on conditional language from Phase 3.
        
        Args:
            document_map: Document map with language analysis
            
        Returns:
            List of conditional dependencies
        """
        dependencies = []
        
        # Check for elements with language analysis
        elements_with_language = document_map.get('elements_with_language_analysis', [])
        if not elements_with_language:
            return dependencies
        
        # Extract elements by ID for easier lookup
        elements_by_id = {}
        for element in document_map.get('elements', []):
            element_id = element.get('id')
            if element_id:
                elements_by_id[element_id] = element
        
        # Process each element with conditional language
        for element in elements_with_language:
            element_id = element.get('id')
            conditional_analysis = element.get('conditional_analysis', {})
            conditions = conditional_analysis.get('conditions', [])
            
            # Skip if no conditions
            if not element_id or not conditions:
                continue
            
            # Process each condition
            for condition in conditions:
                condition_type = condition.get('condition_type', '')
                condition_text = condition.get('condition_text', '')
                
                if not condition_text:
                    continue
                    
                # Find potential target elements for this condition
                target_elements = self._find_elements_related_to_condition(
                    condition_text, elements_by_id, element_id
                )
                
                # Create dependencies for the targets
                for target_id, similarity_score in target_elements:
                    # Map condition type to dependency type
                    dependency_type = 'requires'
                    if 'exception' in condition_type.lower():
                        dependency_type = 'modifies'
                    elif 'limitation' in condition_type.lower():
                        dependency_type = 'restricts'
                        
                    # Calculate strength based on similarity and condition type
                    base_strength = 0.7 if dependency_type == 'requires' else 0.8
                    strength = base_strength * similarity_score
                    
                    dependencies.append({
                        'source_id': element_id,
                        'target_id': target_id,
                        'dependency_type': dependency_type,
                        'strength': round(strength, 2),
                        'origin': 'conditional',
                        'condition_data': {
                            'condition_type': condition_type,
                            'condition_text': condition_text,
                            'similarity_score': similarity_score
                        }
                    })
        
        return dependencies
    
    def _find_elements_related_to_condition(self, condition_text, elements_by_id, source_id):
        """
        Find elements that may be related to a condition.
        
        Args:
            condition_text: Text of the condition
            elements_by_id: Dictionary of elements by ID
            source_id: ID of the source element (to avoid self-references)
            
        Returns:
            List of tuples containing (element_id, similarity_score)
        """
        # Simple keyword matching for demonstration
        related_elements = []
        
        # Extract key terms from condition text
        words = re.findall(r'\b[A-Za-z]{3,}\b', condition_text)
        key_terms = [w.lower() for w in words if len(w) > 3]
        
        if not key_terms:
            return []
        
        # Check each element for matching terms
        for element_id, element in elements_by_id.items():
            # Skip self-reference
            if element_id == source_id:
                continue
                
            element_text = element.get('text', '').lower()
            
            # Count matching terms
            match_count = 0
            for term in key_terms:
                if term in element_text:
                    match_count += 1
            
            # Calculate similarity score
            if match_count > 0:
                similarity = match_count / len(key_terms)
                
                # Only include elements with reasonable similarity
                if similarity >= 0.2:
                    related_elements.append((element_id, similarity))
        
        # Sort by similarity score
        related_elements.sort(key=lambda x: x[1], reverse=True)
        
        # Limit to top 3 results
        return related_elements[:3]
    
    def _deduplicate_dependencies(self, dependencies: List[Dict]) -> List[Dict]:
        """
        Remove duplicate dependencies and resolve conflicts.
        
        Args:
            dependencies: List of all dependencies
            
        Returns:
            Deduplicated dependencies
        """
        # Group dependencies by source and target
        dependency_map = {}
        
        for dep in dependencies:
            source_id = dep.get('source_id')
            target_id = dep.get('target_id')
            
            if not source_id or not target_id:
                continue
                
            key = (source_id, target_id)
            
            if key not in dependency_map:
                dependency_map[key] = []
                
            dependency_map[key].append(dep)
        
        # Resolve conflicts for each source-target pair
        unique_dependencies = []
        
        for key, deps in dependency_map.items():
            if len(deps) == 1:
                # Only one dependency, no conflict
                unique_dependencies.append(deps[0])
            else:
                # Multiple dependencies, resolve conflict
                resolved = self._resolve_dependency_conflict(deps)
                unique_dependencies.append(resolved)
        
        return unique_dependencies
    
    def _resolve_dependency_conflict(self, dependencies: List[Dict]) -> Dict:
        """
        Resolve conflicts between multiple dependencies for the same source-target pair.
        
        Args:
            dependencies: List of conflicting dependencies
            
        Returns:
            Resolved dependency
        """
        # Sort by strength, highest first
        sorted_deps = sorted(dependencies, key=lambda d: d.get('strength', 0), reverse=True)
        
        # Start with the strongest dependency
        resolved = dict(sorted_deps[0])
        
        # Check for multiple origins and combine evidence
        origins = set(d.get('origin', '') for d in dependencies)
        if len(origins) > 1:
            resolved['origin'] = '+'.join(sorted(origins))
            
            # Combine evidence from different sources
            evidence = {}
            for d in dependencies:
                origin = d.get('origin', '')
                if origin == 'reference' and 'reference_data' in d:
                    evidence['reference_data'] = d['reference_data']
                elif origin == 'element_type' and 'similarity_data' in d:
                    evidence['similarity_data'] = d['similarity_data']
                elif origin == 'conditional' and 'condition_data' in d:
                    evidence['condition_data'] = d['condition_data']
            
            resolved['combined_evidence'] = evidence
        
        return resolved
    
    def _build_dependency_chains(self, dependencies: List[Dict]) -> List[Dict]:
        """
        Build chains of dependencies to identify indirect relationships.
        
        Args:
            dependencies: List of unique dependencies
            
        Returns:
            List of dependency chains
        """
        # Build a graph of dependencies
        dependency_graph = {}
        for dep in dependencies:
            source_id = dep.get('source_id')
            target_id = dep.get('target_id')
            
            if not source_id or not target_id:
                continue
                
            if source_id not in dependency_graph:
                dependency_graph[source_id] = []
                
            dependency_graph[source_id].append({
                'target_id': target_id,
                'dependency_id': dep.get('dependency_id', ''),
                'dependency_type': dep.get('dependency_type', ''),
                'strength': dep.get('strength', 0)
            })
        
        # Find important chains (length > 1 and high cumulative strength)
        chains = []
        
        # Identify starting nodes that have outgoing but no incoming edges
        starting_nodes = set(dependency_graph.keys())
        for deps in dependency_graph.values():
            for dep in deps:
                if dep['target_id'] in starting_nodes:
                    starting_nodes.remove(dep['target_id'])
        
        # Traverse the graph from each starting node
        for start_node in starting_nodes:
            self._find_chains(start_node, dependency_graph, [], chains)
        
        # Filter and sort chains
        significant_chains = [
            chain for chain in chains
            if len(chain['path']) > 1 and chain['cumulative_strength'] > 0.5
        ]
        
        significant_chains.sort(key=lambda c: c['cumulative_strength'], reverse=True)
        
        return significant_chains[:20]  # Return top 20 chains
    
    def _find_chains(self, node, graph, current_path, all_chains, depth=0, visited=None):
        """
        Recursively find chains in the dependency graph.
        
        Args:
            node: Current node
            graph: Dependency graph
            current_path: Current path
            all_chains: All chains found so far
            depth: Current recursion depth
            visited: Set of visited nodes
        """
        # Initialize visited set if not provided
        if visited is None:
            visited = set()
        
        # Prevent cycles and limit depth
        if node in visited or depth > 5:
            return
            
        visited.add(node)
        
        # Get dependencies for current node
        dependencies = graph.get(node, [])
        
        for dep in dependencies:
            target = dep['target_id']
            
            # Add current dependency to path
            new_path = current_path + [dep]
            
            # Calculate cumulative strength
            cumulative_strength = 1.0
            for p in new_path:
                cumulative_strength *= p['strength']
            
            # Add chain if length > 1
            if len(new_path) > 1:
                all_chains.append({
                    'path': new_path,
                    'start_node': current_path[0]['target_id'] if current_path else node,
                    'end_node': target,
                    'length': len(new_path),
                    'cumulative_strength': round(cumulative_strength, 3)
                })
            
            # Continue traversal
            self._find_chains(target, graph, new_path, all_chains, depth + 1, visited.copy())