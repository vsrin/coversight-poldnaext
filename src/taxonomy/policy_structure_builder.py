"""
Policy Structure Builder

This module creates a structured representation of the complete policy,
integrating taxonomy mappings and normalized language.
"""

import json
import uuid
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime
from pathlib import Path


class PolicyStructureBuilder:
    """
    Builds a comprehensive structured representation of an insurance policy
    by integrating various analysis components.
    """
    
    def __init__(self):
        """Initialize the policy structure builder."""
        self.policy_structure = {
            "metadata": {},
            "document_map": {},
            "elements": {},
            "taxonomy_mappings": {},
            "normalized_language": {},
            "relationships": {}
        }
        # Track visited nodes for cycle detection
        self._visited_nodes = set()
        # Track relationship paths to detect circular references
        self._relationship_paths = {}
    
    def set_policy_metadata(self, metadata: Dict) -> None:
        """
        Set policy metadata.
        
        Args:
            metadata: Policy metadata (e.g., policy number, effective dates)
        """
        self.policy_structure["metadata"] = metadata
    
    def set_document_map(self, document_map: Dict) -> None:
        """
        Set the document map from document processing.
        
        Args:
            document_map: Document structure map
        """
        # Use only essential document map components to avoid cycles
        if isinstance(document_map, dict):
            essential_keys = ["document_id", "title", "sections", "section_counts"]
            self.policy_structure["document_map"] = {
                k: document_map.get(k, {}) for k in essential_keys 
                if k in document_map
            }
        else:
            self.policy_structure["document_map"] = {}
    
    def add_elements(self, elements: List[Dict]) -> None:
        """
        Add policy elements from element extraction.
        
        Args:
            elements: Extracted policy elements
        """
        # Index elements by ID for efficient access
        for element in elements:
            # Ensure element has an ID
            element_id = element.get("id", str(uuid.uuid4()))
            
            # Create a clean copy without circular references
            clean_element = self._clean_element_for_storage(element)
            self.policy_structure["elements"][element_id] = clean_element
    
    def _clean_element_for_storage(self, element: Dict) -> Dict:
        """
        Create a clean copy of an element without potential circular references.
        
        Args:
            element: The element to clean
            
        Returns:
            A clean copy of the element
        """
        # Copy only essential element properties to avoid cycles
        essential_props = [
            "id", "text", "title", "type", "subtype", "section_id", 
            "confidence", "keywords"
        ]
        
        clean_element = {}
        for prop in essential_props:
            if prop in element:
                clean_element[prop] = element[prop]
        
        return clean_element
    
    def add_taxonomy_mappings(self, mappings: Dict[str, Dict]) -> None:
        """
        Add taxonomy mappings for policy elements.
        
        Args:
            mappings: Element ID to taxonomy mapping results
        """
        # Store mappings without potential circular references
        for element_id, mapping in mappings.items():
            # Ensure mapping is a dictionary
            if isinstance(mapping, dict):
                self.policy_structure["taxonomy_mappings"][element_id] = mapping
    
    def add_normalized_language(self, normalized_elements: List[Dict]) -> None:
        """
        Add normalized language for policy elements.
        
        Args:
            normalized_elements: Normalized policy elements
        """
        for element in normalized_elements:
            element_id = element.get("id")
            if element_id:
                normalized_info = {
                    "normalized_text": element.get("normalized_text"),
                    "normalization_source": element.get("normalization_source"),
                    "standard_clause_id": element.get("standard_clause_id"),
                    "uniqueness_analysis": element.get("uniqueness_analysis", {}),
                    "similarity_score": element.get("similarity_score", 0.0)
                }
                self.policy_structure["normalized_language"][element_id] = normalized_info
    
    def add_relationships(self, relationships: List[Dict]) -> None:
        """
        Add relationships between policy elements with cycle detection.
        
        Args:
            relationships: Element relationships
        """
        # Reset relationship tracking
        self._relationship_paths = {}
        
        # First pass: build a relationship graph to detect cycles
        for relationship in relationships:
            source_id = relationship.get("source_id")
            target_id = relationship.get("target_id")
            
            if source_id and target_id:
                # Initialize path lists if needed
                if source_id not in self._relationship_paths:
                    self._relationship_paths[source_id] = []
                
                # Check for direct cycles (A → B → A)
                has_cycle = False
                for rel_path in self._relationship_paths.get(target_id, []):
                    if rel_path[-1] == source_id:
                        has_cycle = True
                        break
                
                if not has_cycle:
                    # Add this relationship
                    if source_id not in self.policy_structure["relationships"]:
                        self.policy_structure["relationships"][source_id] = []
                    
                    # Store a clean version
                    clean_relationship = {
                        "source_id": source_id,
                        "target_id": target_id,
                        "type": relationship.get("type", "unknown"),
                        "subtype": relationship.get("subtype", ""),
                        "description": relationship.get("description", ""),
                        "weight": relationship.get("weight", 1.0)
                    }
                    
                    self.policy_structure["relationships"][source_id].append(clean_relationship)
                    
                    # Update path tracking for cycle detection
                    new_paths = []
                    # Add source → target path
                    new_paths.append([source_id, target_id])
                    # Add extended paths: X → source → target
                    for source_path in self._relationship_paths.get(source_id, []):
                        if target_id not in source_path:  # Prevent cycles
                            extended_path = source_path.copy()
                            extended_path.append(target_id)
                            new_paths.append(extended_path)
                    
                    # Store the new paths for target
                    if target_id not in self._relationship_paths:
                        self._relationship_paths[target_id] = []
                    self._relationship_paths[target_id].extend(new_paths)
    
    def build_structure(self) -> Dict:
        """
        Build the final structured representation.
        
        Returns:
            Complete policy structure
        """
        try:
            # Add creation timestamp
            self.policy_structure["metadata"]["structure_created_at"] = datetime.now().isoformat()
            
            # Verify no cycles in relationships
            self._verify_no_cycles()
            
            # Add analysis summary
            self.policy_structure["summary"] = self._generate_summary()
            
            return self.policy_structure
        except Exception as e:
            # Log the error and return a basic structure
            print(f"Error building policy structure: {str(e)}")
            return {
                "metadata": self.policy_structure.get("metadata", {}),
                "error": str(e),
                "elements_count": len(self.policy_structure.get("elements", {})),
                "mappings_count": len(self.policy_structure.get("taxonomy_mappings", {})),
                "relationships_count": sum(len(rels) for rels in self.policy_structure.get("relationships", {}).values())
            }
    
    def _verify_no_cycles(self) -> None:
        """
        Verify that there are no cycles in the relationships.
        
        Raises:
            ValueError: If a cycle is detected
        """
        # Check if any element has a path to itself
        for element_id, paths in self._relationship_paths.items():
            for path in paths:
                if element_id in path:
                    raise ValueError("Circular reference detected")
    
    def _generate_summary(self) -> Dict:
        """
        Generate a summary of the policy structure.
        
        Returns:
            Summary statistics
        """
        # Count elements by type
        element_types = {}
        for element in self.policy_structure["elements"].values():
            element_type = element.get("type", "unknown")
            element_types[element_type] = element_types.get(element_type, 0) + 1
        
        # Count taxonomy mappings by code (primary mappings only)
        taxonomy_codes = {}
        for mapping in self.policy_structure["taxonomy_mappings"].values():
            primary = mapping.get("primary_mapping", {})
            code = primary.get("code")
            if code:
                taxonomy_codes[code] = taxonomy_codes.get(code, 0) + 1
        
        # Count normalization sources
        normalization_sources = {}
        for norm in self.policy_structure["normalized_language"].values():
            source = norm.get("normalization_source", "unknown")
            normalization_sources[source] = normalization_sources.get(source, 0) + 1
        
        # Count relationships by type
        relationship_types = {}
        for rel_list in self.policy_structure["relationships"].values():
            for rel in rel_list:
                rel_type = rel.get("type", "unknown")
                relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
        
        return {
            "total_elements": len(self.policy_structure["elements"]),
            "element_types": element_types,
            "taxonomy_mapping_count": len(self.policy_structure["taxonomy_mappings"]),
            "taxonomy_codes": taxonomy_codes,
            "normalized_language_count": len(self.policy_structure["normalized_language"]),
            "normalization_sources": normalization_sources,
            "relationship_count": sum(len(rel_list) for rel_list in self.policy_structure["relationships"].values()),
            "relationship_types": relationship_types
        }
    
    def save_structure(self, file_path: str) -> None:
        """
        Save the structure to a JSON file.
        
        Args:
            file_path: Path to save the structure to
        """
        try:
            structure = self.build_structure()
            with open(file_path, 'w') as f:
                json.dump(structure, f, indent=2)
        except Exception as e:
            print(f"Error saving structure: {str(e)}")
            # Save a simplified version if full structure fails
            simplified = {
                "metadata": self.policy_structure.get("metadata", {}),
                "error": str(e),
                "elements_count": len(self.policy_structure.get("elements", {}))
            }
            with open(file_path, 'w') as f:
                json.dump(simplified, f, indent=2)
    
    def get_elements_by_taxonomy(self, taxonomy_code: str, 
                              min_confidence: float = 0.5) -> List[Dict]:
        """
        Get all elements mapped to a specific taxonomy code.
        
        Args:
            taxonomy_code: Taxonomy code to filter by
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of elements that map to the specified taxonomy code
        """
        matched_elements = []
        
        for element_id, mapping in self.policy_structure["taxonomy_mappings"].items():
            # Look at all mappings, not just primary
            all_mappings = mapping.get("all_mappings", [])
            
            for map_info in all_mappings:
                code = map_info.get("code")
                confidence = map_info.get("confidence", 0.0)
                
                if code == taxonomy_code and confidence >= min_confidence:
                    if element_id in self.policy_structure["elements"]:
                        element = self.policy_structure["elements"][element_id]
                        
                        # Add mapping information to the element
                        element_with_mapping = element.copy()
                        element_with_mapping["mapping_confidence"] = confidence
                        
                        # Add normalized text if available
                        if element_id in self.policy_structure["normalized_language"]:
                            norm_info = self.policy_structure["normalized_language"][element_id]
                            element_with_mapping["normalized_text"] = norm_info.get("normalized_text")
                        
                        matched_elements.append(element_with_mapping)
                        break
        
        return matched_elements
    
    def get_coverage_summary(self) -> Dict:
        """
        Generate a coverage summary from the policy structure.
        
        Returns:
            Coverage summary information
        """
        # Find all coverage grants
        coverage_grants = []
        for element_id, element in self.policy_structure["elements"].items():
            if element.get("type") == "coverage_grant":
                # Get mapping info
                mapping_info = self.policy_structure["taxonomy_mappings"].get(element_id, {})
                primary_mapping = mapping_info.get("primary_mapping", {})
                
                # Get normalization info
                norm_info = self.policy_structure["normalized_language"].get(element_id, {})
                
                # Create coverage item
                coverage_item = {
                    "id": element_id,
                    "title": element.get("title", "Untitled Coverage"),
                    "taxonomy_code": primary_mapping.get("code"),
                    "confidence": primary_mapping.get("confidence", 0.0),
                    "text": norm_info.get("normalized_text") or element.get("text", ""),
                    "is_unique": norm_info.get("uniqueness_analysis", {}).get("is_unique", False),
                    "section": element.get("section_id")
                }
                
                # Add associated sublimits
                coverage_item["sublimits"] = self._find_associated_elements(element_id, "sublimit")
                
                # Add associated exclusions
                coverage_item["exclusions"] = self._find_associated_elements(element_id, "exclusion")
                
                coverage_grants.append(coverage_item)
        
        # Group by taxonomy code
        coverage_by_taxonomy = {}
        for coverage in coverage_grants:
            code = coverage.get("taxonomy_code") or "uncategorized"
            if code not in coverage_by_taxonomy:
                coverage_by_taxonomy[code] = []
            
            coverage_by_taxonomy[code].append(coverage)
        
        return {
            "total_coverages": len(coverage_grants),
            "taxonomy_distribution": {
                code: len(items) for code, items in coverage_by_taxonomy.items()
            },
            "coverage_grants": coverage_grants,
            "coverage_by_taxonomy": coverage_by_taxonomy
        }
    
    def _find_associated_elements(self, element_id: str, relationship_type: str) -> List[Dict]:
        """
        Find elements associated with an element through a specific relationship type.
        
        Args:
            element_id: Element ID to find related elements for
            relationship_type: Type of relationship to search for
            
        Returns:
            List of associated elements
        """
        associated_elements = []
        
        # Check relationships
        relationships = self.policy_structure["relationships"].get(element_id, [])
        for rel in relationships:
            if rel.get("type") == relationship_type and rel.get("target_id"):
                target_id = rel.get("target_id")
                if target_id in self.policy_structure["elements"]:
                    target_element = self.policy_structure["elements"][target_id]
                    
                    # Get normalization info if available
                    norm_info = self.policy_structure["normalized_language"].get(target_id, {})
                    normalized_text = norm_info.get("normalized_text")
                    
                    # Create associated element entry
                    associated = {
                        "id": target_id,
                        "title": target_element.get("title", "Untitled"),
                        "text": normalized_text or target_element.get("text", ""),
                        "relationship_type": relationship_type,
                        "is_unique": norm_info.get("uniqueness_analysis", {}).get("is_unique", False)
                    }
                    
                    associated_elements.append(associated)
        
        return associated_elements