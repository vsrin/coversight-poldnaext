"""
Insurance Policy Taxonomy Framework

This module implements a comprehensive, hierarchical taxonomy framework for
standardizing insurance policy elements based on industry standards (ACORD, ISO, NAIC).
The framework allows for flexible taxonomy definition, extension, and mapping of
extracted policy elements to standardized categories.
"""

import json
from enum import Enum
from typing import Dict, List, Optional, Set, Union
from pathlib import Path


class TaxonomyLevel(Enum):
    """Enumeration of taxonomy hierarchy levels."""
    LINE_OF_BUSINESS = 1  # Top level (e.g., Property, Liability)
    COVERAGE_CATEGORY = 2  # Category level (e.g., Building Coverage, Business Interruption)
    COVERAGE_TYPE = 3      # Specific coverage type (e.g., Building, Business Personal Property)
    COVERAGE_DETAIL = 4    # Detailed coverage (e.g., Debris Removal, Ordinance or Law)
    COVERAGE_ATTRIBUTE = 5 # Specific attributes (e.g., Valuation Method, Geographic Scope)


class ElementType(Enum):
    """Types of policy elements that can be mapped to the taxonomy."""
    COVERAGE_GRANT = "coverage_grant"
    EXCLUSION = "exclusion"
    CONDITION = "condition"
    DEFINITION = "definition"
    SUB_LIMIT = "sub_limit"
    RETENTION = "retention"
    EXTENSION = "extension"
    TERRITORY = "territory"
    TIME_ELEMENT = "time_element"
    ENDORSEMENT = "endorsement"
    TRIGGER = "trigger"
    NOTICE_REQUIREMENT = "notice_requirement"
    LIMIT = "limit"
    PREMIUM = "premium"
    OTHER = "other"


class TaxonomyNode:
    """Represents a node in the taxonomy hierarchy."""
    
    def __init__(
        self,
        code: str,
        name: str,
        level: TaxonomyLevel,
        description: str = "",
        source: str = "",
        parent_code: Optional[str] = None,
    ):
        """
        Initialize a taxonomy node.
        
        Args:
            code: Unique identifier for this taxonomy node
            name: Human-readable name
            level: Taxonomy hierarchy level
            description: Detailed description of this category
            source: Source standard (e.g., "ACORD", "ISO", "NAIC", "Custom")
            parent_code: Code of the parent node, if any
        """
        self.code = code
        self.name = name
        self.level = level
        self.description = description
        self.source = source
        self.parent_code = parent_code
        self.children: List[str] = []  # List of child node codes
        self.synonyms: List[str] = []  # List of alternative terms/phrases
        self.examples: List[str] = []  # Example policy text snippets for this category
        self.related_codes: List[str] = []  # Related nodes in other branches
        
    def to_dict(self) -> Dict:
        """Convert node to dictionary representation."""
        return {
            "code": self.code,
            "name": self.name,
            "level": self.level.name,
            "level_value": self.level.value,
            "description": self.description,
            "source": self.source,
            "parent_code": self.parent_code,
            "children": self.children,
            "synonyms": self.synonyms,
            "examples": self.examples,
            "related_codes": self.related_codes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TaxonomyNode':
        """Create node from dictionary representation."""
        node = cls(
            code=data["code"],
            name=data["name"],
            level=TaxonomyLevel[data["level"]],
            description=data.get("description", ""),
            source=data.get("source", ""),
            parent_code=data.get("parent_code")
        )
        node.children = data.get("children", [])
        node.synonyms = data.get("synonyms", [])
        node.examples = data.get("examples", [])
        node.related_codes = data.get("related_codes", [])
        return node


class TaxonomyManager:
    """
    Manages the insurance policy taxonomy, including loading, saving, and accessing
    taxonomy nodes.
    """
    
    def __init__(self, taxonomy_data_path: Optional[str] = None):
        """
        Initialize the taxonomy manager.
        
        Args:
            taxonomy_data_path: Path to load taxonomy data from, if any
        """
        self.nodes: Dict[str, TaxonomyNode] = {}
        self.root_nodes: List[str] = []  # List of top-level node codes
        
        # Load built-in taxonomy if no path is provided
        if taxonomy_data_path is None:
            self._load_builtin_taxonomy()
        else:
            self.load_taxonomy(taxonomy_data_path)
    
    def _load_builtin_taxonomy(self):
        """Load the built-in standard insurance taxonomy."""
        # Property Insurance Line
        self.add_node(TaxonomyNode(
            code="PROP",
            name="Property Insurance",
            level=TaxonomyLevel.LINE_OF_BUSINESS,
            description="Insurance coverage for physical assets and structures",
            source="ISO"
        ))
        
        # Property subcategories
        self.add_node(TaxonomyNode(
            code="PROP.BLDG",
            name="Building Coverage",
            level=TaxonomyLevel.COVERAGE_CATEGORY,
            description="Coverage for building structures",
            source="ISO",
            parent_code="PROP"
        ))
        
        self.add_node(TaxonomyNode(
            code="PROP.BPP",
            name="Business Personal Property",
            level=TaxonomyLevel.COVERAGE_CATEGORY,
            description="Coverage for business contents and equipment",
            source="ISO",
            parent_code="PROP"
        ))
        
        self.add_node(TaxonomyNode(
            code="PROP.BI",
            name="Business Interruption",
            level=TaxonomyLevel.COVERAGE_CATEGORY,
            description="Coverage for lost income due to property damage",
            source="ISO",
            parent_code="PROP"
        ))
        
        # Property coverage types
        self.add_node(TaxonomyNode(
            code="PROP.BLDG.MAIN",
            name="Main Building Structure",
            level=TaxonomyLevel.COVERAGE_TYPE,
            description="Primary building structure coverage",
            source="ISO",
            parent_code="PROP.BLDG"
        ))
        
        self.add_node(TaxonomyNode(
            code="PROP.BLDG.APPURT",
            name="Appurtenant Structures",
            level=TaxonomyLevel.COVERAGE_TYPE,
            description="Structures attached to main building",
            source="ISO",
            parent_code="PROP.BLDG"
        ))
        
        # Liability Insurance Line
        self.add_node(TaxonomyNode(
            code="LIAB",
            name="Liability Insurance",
            level=TaxonomyLevel.LINE_OF_BUSINESS,
            description="Insurance coverage for legal liabilities",
            source="ISO"
        ))
        
        # Liability subcategories
        self.add_node(TaxonomyNode(
            code="LIAB.GL",
            name="General Liability",
            level=TaxonomyLevel.COVERAGE_CATEGORY,
            description="Liability for bodily injury and property damage",
            source="ISO",
            parent_code="LIAB"
        ))
        
        self.add_node(TaxonomyNode(
            code="LIAB.PROD",
            name="Products Liability",
            level=TaxonomyLevel.COVERAGE_CATEGORY,
            description="Liability for product-related injuries or damages",
            source="ISO",
            parent_code="LIAB"
        ))
        
        # Cyber Insurance Line
        self.add_node(TaxonomyNode(
            code="CYBER",
            name="Cyber Insurance",
            level=TaxonomyLevel.LINE_OF_BUSINESS,
            description="Insurance coverage for cyber risks and data breaches",
            source="NAIC"
        ))
        
        # Cyber subcategories
        self.add_node(TaxonomyNode(
            code="CYBER.BREACH",
            name="Data Breach Coverage",
            level=TaxonomyLevel.COVERAGE_CATEGORY,
            description="Coverage for data breach response costs",
            source="NAIC",
            parent_code="CYBER"
        ))
        
        self.add_node(TaxonomyNode(
            code="CYBER.LIAB",
            name="Cyber Liability Coverage",
            level=TaxonomyLevel.COVERAGE_CATEGORY,
            description="Liability coverage for data breaches and cyber incidents",
            source="NAIC",
            parent_code="CYBER"
        ))
        
        # Auto Insurance Line
        self.add_node(TaxonomyNode(
            code="AUTO",
            name="Auto Insurance",
            level=TaxonomyLevel.LINE_OF_BUSINESS,
            description="Insurance coverage for vehicles",
            source="ISO"
        ))
        
        # Workers Compensation Insurance Line
        self.add_node(TaxonomyNode(
            code="WC",
            name="Workers Compensation",
            level=TaxonomyLevel.LINE_OF_BUSINESS,
            description="Coverage for employee injuries or illness during employment",
            source="NAIC"
        ))
        
        # Professional Liability Insurance Line
        self.add_node(TaxonomyNode(
            code="PROF",
            name="Professional Liability",
            level=TaxonomyLevel.LINE_OF_BUSINESS,
            description="Liability coverage for professional services",
            source="ISO"
        ))
        
        # Directors & Officers Insurance Line
        self.add_node(TaxonomyNode(
            code="DO",
            name="Directors and Officers Liability",
            level=TaxonomyLevel.LINE_OF_BUSINESS,
            description="Liability coverage for company directors and officers",
            source="ISO"
        ))
        
        # Employment Practices Liability Insurance Line
        self.add_node(TaxonomyNode(
            code="EPL",
            name="Employment Practices Liability",
            level=TaxonomyLevel.LINE_OF_BUSINESS,
            description="Coverage for employment-related claims",
            source="ISO"
        ))
        
        # Marine Insurance Line
        self.add_node(TaxonomyNode(
            code="MARINE",
            name="Marine Insurance",
            level=TaxonomyLevel.LINE_OF_BUSINESS,
            description="Coverage for ocean and inland marine risks",
            source="ISO"
        ))
        
        # Expand with more nodes as needed
        
    def add_node(self, node: TaxonomyNode) -> None:
        """
        Add a node to the taxonomy.
        
        Args:
            node: The taxonomy node to add
        """
        self.nodes[node.code] = node
        
        # If it has a parent, add it as a child to that parent
        if node.parent_code:
            if node.parent_code in self.nodes:
                parent = self.nodes[node.parent_code]
                if node.code not in parent.children:
                    parent.children.append(node.code)
            else:
                # Store orphaned nodes and resolve later
                pass
        else:
            # It's a root node
            if node.code not in self.root_nodes:
                self.root_nodes.append(node.code)
    
    def get_node(self, code: str) -> Optional[TaxonomyNode]:
        """
        Get a taxonomy node by its code.
        
        Args:
            code: The node code to look up
            
        Returns:
            The node if found, None otherwise
        """
        return self.nodes.get(code)
    
    def get_children(self, code: str) -> List[TaxonomyNode]:
        """
        Get all children of a node.
        
        Args:
            code: The parent node code
            
        Returns:
            List of child nodes
        """
        node = self.get_node(code)
        if not node:
            return []
        
        return [self.nodes[child_code] for child_code in node.children 
                if child_code in self.nodes]
    
    def get_path_to_root(self, code: str) -> List[TaxonomyNode]:
        """
        Get the path from a node to the root.
        
        Args:
            code: The node code to start from
            
        Returns:
            List of nodes from the given node to the root
        """
        path = []
        current = self.get_node(code)
        
        while current:
            path.append(current)
            if not current.parent_code:
                break
            current = self.get_node(current.parent_code)
        
        return path
    
    def find_nodes_by_name(self, name: str, partial_match: bool = True) -> List[TaxonomyNode]:
        """
        Find nodes by name.
        
        Args:
            name: The name to search for
            partial_match: Whether to allow partial matching
            
        Returns:
            List of matching nodes
        """
        results = []
        name_lower = name.lower()
        
        for node in self.nodes.values():
            if partial_match:
                if name_lower in node.name.lower():
                    results.append(node)
            else:
                if name_lower == node.name.lower():
                    results.append(node)
                
        return results
    
    def get_all_nodes_at_level(self, level: TaxonomyLevel) -> List[TaxonomyNode]:
        """
        Get all nodes at a specific taxonomy level.
        
        Args:
            level: The level to filter by
            
        Returns:
            List of nodes at the specified level
        """
        return [node for node in self.nodes.values() if node.level == level]
    
    def save_taxonomy(self, file_path: str) -> None:
        """
        Save the taxonomy to a JSON file.
        
        Args:
            file_path: Path to save the file to
        """
        data = {
            "nodes": {code: node.to_dict() for code, node in self.nodes.items()},
            "root_nodes": self.root_nodes
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_taxonomy(self, file_path: str) -> None:
        """
        Load a taxonomy from a JSON file.
        
        Args:
            file_path: Path to load the taxonomy from
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        self.nodes = {}
        for code, node_data in data["nodes"].items():
            self.nodes[code] = TaxonomyNode.from_dict(node_data)
        
        self.root_nodes = data["root_nodes"]
    
    def extend_from_file(self, file_path: str) -> None:
        """
        Extend the current taxonomy with nodes from a file.
        
        Args:
            file_path: Path to the file with additional nodes
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        for code, node_data in data["nodes"].items():
            if code not in self.nodes:
                self.nodes[code] = TaxonomyNode.from_dict(node_data)
        
        for root in data["root_nodes"]:
            if root not in self.root_nodes:
                self.root_nodes.append(root)
    
    def to_dict(self) -> Dict:
        """Convert the entire taxonomy to a dictionary representation."""
        return {
            "nodes": {code: node.to_dict() for code, node in self.nodes.items()},
            "root_nodes": self.root_nodes
        }
    
    def print_hierarchy(self, start_code: Optional[str] = None, indent: int = 0) -> None:
        """
        Print the taxonomy hierarchy.
        
        Args:
            start_code: Code of the node to start from, or None for all root nodes
            indent: Indentation level for formatting
        """
        if start_code:
            nodes_to_print = [start_code]
        else:
            nodes_to_print = self.root_nodes
        
        for code in nodes_to_print:
            node = self.get_node(code)
            if not node:
                continue
                
            print("  " * indent + f"{node.code}: {node.name} ({node.level.name})")
            
            for child_code in node.children:
                self.print_hierarchy(child_code, indent + 1)


class TaxonomyExpander:
    """
    Utilities to expand the taxonomy with additional nodes from
    industry standards (ACORD, ISO, NAIC).
    """
    
    @staticmethod
    def expand_with_acord_standards(taxonomy_manager: TaxonomyManager, 
                                   acord_data_path: str) -> None:
        """
        Expand taxonomy with ACORD standard elements.
        
        Args:
            taxonomy_manager: The taxonomy manager to expand
            acord_data_path: Path to ACORD data file
        """
        # Implementation would parse ACORD XML schemas
        # and extract taxonomy elements
        pass
    
    @staticmethod
    def expand_with_iso_standards(taxonomy_manager: TaxonomyManager,
                                 iso_data_path: str) -> None:
        """
        Expand taxonomy with ISO standard elements.
        
        Args:
            taxonomy_manager: The taxonomy manager to expand
            iso_data_path: Path to ISO data file
        """
        # Implementation would parse ISO standard forms 
        # and extract taxonomy elements
        pass
    
    @staticmethod
    def expand_with_naic_standards(taxonomy_manager: TaxonomyManager,
                                  naic_data_path: str) -> None:
        """
        Expand taxonomy with NAIC standard elements.
        
        Args:
            taxonomy_manager: The taxonomy manager to expand
            naic_data_path: Path to NAIC data file
        """
        # Implementation would parse NAIC guidelines
        # and extract taxonomy elements
        pass


# Example usage
if __name__ == "__main__":
    # Create a taxonomy manager with built-in standard taxonomy
    taxonomy = TaxonomyManager()
    
    # Print the taxonomy hierarchy
    print("Insurance Policy Taxonomy Hierarchy:")
    taxonomy.print_hierarchy()
    
    # Save the taxonomy to a file
    taxonomy.save_taxonomy("standard_taxonomy.json")
    
    print("\nProperty Insurance Branch:")
    taxonomy.print_hierarchy("PROP")
    
    print("\nLiability Insurance Branch:")
    taxonomy.print_hierarchy("LIAB")