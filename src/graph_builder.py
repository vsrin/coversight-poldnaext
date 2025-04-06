"""
Graph builder module for the Policy DNA Extractor.

This module builds a navigable relationship graph of policy elements.
"""

from typing import Dict, List, Set, Tuple, Any, Optional

class GraphBuilder:
    """
    Builds a relationship graph of policy elements.
    """
    def __init__(self, config):
        """
        Initialize the GraphBuilder.
        
        Args:
            config: Application configuration
        """
        self.config = config
    
    def build_graph(self, document_map: Dict, references_data: Dict, dependencies_data: Dict, conflicts_data: Dict) -> Dict:
        """
        Build a comprehensive graph of policy element relationships.
        
        Args:
            document_map: Complete document map with elements
            references_data: Output from ReferenceDetector
            dependencies_data: Output from DependencyAnalyzer
            conflicts_data: Output from ConflictIdentifier
            
        Returns:
            Dictionary containing the relationship graph
        """
        print("  Creating element nodes...")
        nodes = self._create_nodes(document_map)
        print(f"  Created {len(nodes)} nodes")
        
        print("  Creating relationship edges...")
        edges = self._create_edges(references_data, dependencies_data, conflicts_data)
        print(f"  Created {len(edges)} edges")
        
        print("  Analyzing graph connectivity...")
        connectivity_metrics = self._analyze_connectivity(nodes, edges)
        
        print("  Identifying key elements...")
        key_elements = self._identify_key_elements(nodes, edges)
        print(f"  Identified {len(key_elements)} key elements")
        
        # Create the graph result
        graph_result = {
            "nodes": nodes,
            "edges": edges,
            "graph_stats": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "connectivity": connectivity_metrics
            },
            "most_referenced": key_elements[:10],  # Top 10 most referenced
            "reference_type_counts": references_data.get("reference_type_counts", {}),
            "dependency_type_counts": dependencies_data.get("dependency_type_counts", {}),
            "conflicts": conflicts_data.get("conflicts", [])
        }
        
        return graph_result
    
    def _create_nodes(self, document_map: Dict) -> List[Dict]:
        """
        Create nodes from document elements.
        
        Args:
            document_map: Document map with elements
            
        Returns:
            List of nodes
        """
        nodes = []
        elements = document_map.get('elements', [])
        
        for element in elements:
            element_id = element.get('id')
            
            if not element_id:
                continue
                
            # Create node with basic information
            node = {
                'id': element_id,
                'type': element.get('type', 'UNKNOWN'),
                'section_id': element.get('section_id', ''),
                'text': element.get('text', '')[:200],  # Limit text length
                'metadata': {
                    'subtype': element.get('subtype', ''),
                    'keywords': element.get('keywords', [])
                }
            }
            
            # Add language analysis if available
            if 'elements_with_language_analysis' in document_map:
                for lang_element in document_map['elements_with_language_analysis']:
                    if lang_element.get('id') == element_id:
                        # Add intent analysis
                        if 'intent_analysis' in lang_element:
                            node['intent'] = {
                                'intent_summary': lang_element['intent_analysis'].get('intent_summary', ''),
                                'coverage_effect': lang_element['intent_analysis'].get('coverage_effect', '')
                            }
                        
                        # Add conditional analysis (summarized)
                        if 'conditional_analysis' in lang_element:
                            conditions = lang_element['conditional_analysis'].get('conditions', [])
                            if conditions:
                                node['conditions'] = {
                                    'count': len(conditions),
                                    'types': list(set(c.get('condition_type', '') for c in conditions if 'condition_type' in c))
                                }
                        
                        break
            
            nodes.append(node)
        
        return nodes
    
    def _create_edges(self, references_data: Dict, dependencies_data: Dict, conflicts_data: Dict) -> List[Dict]:
        """
        Create edges from references, dependencies, and conflicts.
        
        Args:
            references_data: Output from ReferenceDetector
            dependencies_data: Output from DependencyAnalyzer
            conflicts_data: Output from ConflictIdentifier
            
        Returns:
            List of edges
        """
        edges = []
        
        # Add reference edges
        for ref in references_data.get('references', []):
            source_id = ref.get('source_id')
            target_id = ref.get('target_id')
            
            if not source_id or not target_id:
                continue
                
            edge = {
                'id': ref.get('reference_id', f"REF-{len(edges):04d}"),
                'source': source_id,
                'target': target_id,
                'type': 'reference',
                'subtype': ref.get('reference_type', 'unknown'),
                'text': ref.get('reference_text', '')[:100] if 'reference_text' in ref else '',
                'weight': ref.get('confidence', 0.5),
                'metadata': {}
            }
            
            edges.append(edge)
        
        # Add dependency edges
        for dep in dependencies_data.get('dependencies', []):
            source_id = dep.get('source_id')
            target_id = dep.get('target_id')
            
            if not source_id or not target_id:
                continue
                
            # Check if this dependency duplicates a reference
            if not any(e['source'] == source_id and e['target'] == target_id and e['type'] == 'reference' for e in edges):
                edge = {
                    'id': dep.get('dependency_id', f"DEP-{len(edges):04d}"),
                    'source': source_id,
                    'target': target_id,
                    'type': 'dependency',
                    'subtype': dep.get('dependency_type', 'unknown'),
                    'weight': dep.get('strength', 0.5),
                    'metadata': {
                        'origin': dep.get('origin', 'unknown')
                    }
                }
                
                edges.append(edge)
        
        # Add conflict edges
        for conflict in conflicts_data.get('conflicts', []):
            conflict_id = conflict.get('conflict_id', f"CONF-{len(edges):04d}")
            
            # Get conflicting elements
            elements = conflict.get('conflicting_elements', [])
            if not elements or len(elements) < 2:
                continue
                
            # Create edges between all conflicting elements
            for i, element1 in enumerate(elements):
                for element2 in elements[i+1:]:
                    edge = {
                        'id': f"{conflict_id}-{i}",
                        'source': element1.get('element_id'),
                        'target': element2.get('element_id'),
                        'type': 'conflict',
                        'subtype': conflict.get('conflict_type', 'unknown'),
                        'weight': conflict.get('severity', 0.5),
                        'metadata': {
                            'description': conflict.get('description', '')
                        }
                    }
                    
                    edges.append(edge)
        
        return edges
    
    def _analyze_connectivity(self, nodes: List[Dict], edges: List[Dict]) -> Dict:
        """
        Analyze the connectivity of the graph.
        
        Args:
            nodes: List of nodes
            edges: List of edges
            
        Returns:
            Dictionary of connectivity metrics
        """
        # Create adjacency list for graph representation
        graph = {}
        for node in nodes:
            graph[node['id']] = []
        
        for edge in edges:
            source = edge.get('source')
            target = edge.get('target')
            
            if source in graph and target in graph:
                graph[source].append(target)
        
        # Calculate connectivity metrics
        total_nodes = len(nodes)
        isolated_nodes = sum(1 for node_id, connections in graph.items() if not connections and not any(edge['target'] == node_id for edge in edges))
        
        # Find connected components
        components = self._find_connected_components(graph)
        
        return {
            'connected_components': len(components),
            'largest_component_size': max(len(comp) for comp in components) if components else 0,
            'isolated_nodes': isolated_nodes,
            'isolated_percentage': round(isolated_nodes / total_nodes * 100, 2) if total_nodes > 0 else 0
        }
    
    def _find_connected_components(self, graph: Dict) -> List[Set]:
        """
        Find connected components in the graph.
        
        Args:
            graph: Adjacency list representation of the graph
            
        Returns:
            List of sets, each set containing nodes in a connected component
        """
        visited = set()
        components = []
        
        def dfs(node, component):
            visited.add(node)
            component.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor, component)
        
        # Find components using DFS
        for node in graph:
            if node not in visited:
                component = set()
                dfs(node, component)
                components.append(component)
        
        return components
    
    def _identify_key_elements(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        """
        Identify key elements in the graph based on connectivity.
        
        Args:
            nodes: List of nodes
            edges: List of edges
            
        Returns:
            List of key elements with metrics
        """
        # Count incoming references for each node
        incoming_count = {}
        for node in nodes:
            incoming_count[node['id']] = 0
        
        for edge in edges:
            target = edge.get('target')
            if target in incoming_count:
                incoming_count[target] += 1
        
        # Create list of key elements with metrics
        key_elements = []
        for node in nodes:
            node_id = node['id']
            references = incoming_count.get(node_id, 0)
            
            if references > 0:
                key_elements.append({
                    'element_id': node_id,
                    'element_type': node.get('type', 'UNKNOWN'),
                    'element_text': node.get('text', '')[:100],
                    'reference_count': references
                })
        
        # Sort by reference count, highest first
        key_elements.sort(key=lambda x: x['reference_count'], reverse=True)
        
        return key_elements
    
    def find_path(self, graph_data: Dict, start_id: str, end_id: str) -> Dict:
        """
        Find path between two elements in the graph.
        
        Args:
            graph_data: Graph data returned by build_graph
            start_id: ID of the starting element
            end_id: ID of the ending element
            
        Returns:
            Dictionary containing the path and metadata
        """
        # Build adjacency list
        graph = {}
        edges_by_pair = {}
        
        for node in graph_data.get('nodes', []):
            graph[node['id']] = []
        
        for edge in graph_data.get('edges', []):
            source = edge.get('source')
            target = edge.get('target')
            
            if source in graph and target in graph:
                graph[source].append(target)
                
                # Store edge data for path reconstruction
                edge_key = (source, target)
                if edge_key not in edges_by_pair:
                    edges_by_pair[edge_key] = []
                edges_by_pair[edge_key].append(edge)
        
        # Find path using BFS
        visited = set()
        queue = [(start_id, [])]
        visited.add(start_id)
        
        while queue:
            node, path = queue.pop(0)
            
            # Check if we've reached the destination
            if node == end_id:
                return self._construct_path_result(path + [node], edges_by_pair, graph_data.get('nodes', []))
            
            # Explore neighbors
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [node]))
        
        # No path found
        return {
            'path_exists': False,
            'path': [],
            'edges': [],
            'path_length': 0
        }
    
    def _construct_path_result(self, path: List[str], edges_by_pair: Dict, nodes: List[Dict]) -> Dict:
        """
        Construct path result with node and edge details.
        
        Args:
            path: List of node IDs in the path
            edges_by_pair: Dictionary of edges by source-target pair
            nodes: List of all nodes
            
        Returns:
            Path result dictionary
        """
        # Find nodes in the path
        path_nodes = []
        for node_id in path:
            for node in nodes:
                if node['id'] == node_id:
                    path_nodes.append(node)
                    break
        
        # Find edges in the path
        path_edges = []
        for i in range(len(path) - 1):
            source = path[i]
            target = path[i+1]
            
            edge_key = (source, target)
            if edge_key in edges_by_pair and edges_by_pair[edge_key]:
                # Use the first edge if multiple exist
                path_edges.append(edges_by_pair[edge_key][0])
        
        return {
            'path_exists': True,
            'path': path,
            'nodes': path_nodes,
            'edges': path_edges,
            'path_length': len(path) - 1
        }
    
    def find_dependencies(self, graph_data: Dict, element_id: str, direction='outgoing') -> Dict:
        """
        Find all dependencies for an element.
        
        Args:
            graph_data: Graph data returned by build_graph
            element_id: ID of the element
            direction: 'outgoing' for elements this depends on, 'incoming' for elements depending on this
            
        Returns:
            Dictionary containing the dependencies
        """
        # Extract nodes and edges
        nodes = {node['id']: node for node in graph_data.get('nodes', [])}
        
        dependencies = []
        
        for edge in graph_data.get('edges', []):
            source = edge.get('source')
            target = edge.get('target')
            
            if direction == 'outgoing' and source == element_id:
                if target in nodes:
                    dependencies.append({
                        'element_id': target,
                        'element_type': nodes[target].get('type', 'UNKNOWN'),
                        'element_text': nodes[target].get('text', '')[:100],
                        'relationship': {
                            'type': edge.get('type', 'unknown'),
                            'subtype': edge.get('subtype', 'unknown'),
                            'weight': edge.get('weight', 0.5)
                        }
                    })
            elif direction == 'incoming' and target == element_id:
                if source in nodes:
                    dependencies.append({
                        'element_id': source,
                        'element_type': nodes[source].get('type', 'UNKNOWN'),
                        'element_text': nodes[source].get('text', '')[:100],
                        'relationship': {
                            'type': edge.get('type', 'unknown'),
                            'subtype': edge.get('subtype', 'unknown'),
                            'weight': edge.get('weight', 0.5)
                        }
                    })
        
        # Group by relationship type
        grouped = {}
        for dep in dependencies:
            rel_type = dep['relationship']['type']
            if rel_type not in grouped:
                grouped[rel_type] = []
            grouped[rel_type].append(dep)
        
        return {
            'element_id': element_id,
            'element_type': nodes.get(element_id, {}).get('type', 'UNKNOWN'),
            'dependency_direction': direction,
            'total_dependencies': len(dependencies),
            'dependencies_by_type': grouped,
            'dependencies': dependencies
        }
    
    def find_elements_by_type(self, graph_data: Dict, element_type: str) -> List[Dict]:
        """
        Find all elements of a specific type.
        
        Args:
            graph_data: Graph data returned by build_graph
            element_type: Type of elements to find
            
        Returns:
            List of elements of the specified type
        """
        elements = []
        
        for node in graph_data.get('nodes', []):
            if node.get('type') == element_type:
                elements.append({
                    'element_id': node['id'],
                    'element_text': node.get('text', '')[:100],
                    'section_id': node.get('section_id', '')
                })
        
        return elements
    
    def find_conflicts_for_element(self, graph_data: Dict, element_id: str) -> List[Dict]:
        """
        Find all conflicts involving a specific element.
        
        Args:
            graph_data: Graph data returned by build_graph
            element_id: ID of the element
            
        Returns:
            List of conflicts involving the element
        """
        conflicts = []
        
        for conflict in graph_data.get('conflicts', []):
            # Check if element is involved in this conflict
            elements = conflict.get('conflicting_elements', [])
            
            if any(e.get('element_id') == element_id for e in elements):
                conflicts.append(conflict)
        
        return conflicts