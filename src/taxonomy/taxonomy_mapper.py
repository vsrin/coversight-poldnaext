"""
Taxonomy Mapping Engine

This module provides functionality to map extracted policy elements to the standardized 
taxonomy, with confidence scoring and rule-based mapping algorithms.
"""

import re
import json
from typing import Dict, List, Optional, Set, Tuple, Any
import difflib
from pathlib import Path
import numpy as np

from src.taxonomy.taxonomy_framework import TaxonomyManager, TaxonomyNode, TaxonomyLevel, ElementType

class MappingRule:
    """Base class for taxonomy mapping rules."""
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize a mapping rule.
        
        Args:
            name: Name of the rule
            description: Description of what the rule does
        """
        self.name = name
        self.description = description
    
    def apply(self, element: Dict, taxonomy: TaxonomyManager) -> List[Tuple[str, float]]:
        """
        Apply the rule to an element and return potential taxonomy matches.
        
        Args:
            element: The policy element to map
            taxonomy: The taxonomy to map against
            
        Returns:
            List of tuples (taxonomy_code, confidence_score)
        """
        raise NotImplementedError("Subclasses must implement apply()")


class KeywordMatchRule(MappingRule):
    """Map elements based on keyword matching."""
    
    def __init__(self, keywords_by_code: Dict[str, List[str]]):
        """
        Initialize with keywords for each taxonomy code.
        
        Args:
            keywords_by_code: Dictionary mapping taxonomy codes to keyword lists
        """
        super().__init__(
            name="Keyword Match",
            description="Maps elements based on keyword presence in text"
        )
        self.keywords_by_code = keywords_by_code
    
    def apply(self, element: Dict, taxonomy: TaxonomyManager) -> List[Tuple[str, float]]:
        """
        Apply keyword matching to find taxonomy nodes.
        
        Args:
            element: The policy element to map
            taxonomy: The taxonomy to map against
            
        Returns:
            List of tuples (taxonomy_code, confidence_score)
        """
        matches = []
        element_text = element.get("text", "").lower()
        
        for code, keywords in self.keywords_by_code.items():
            # Count how many keywords match
            matches_count = sum(1 for keyword in keywords if keyword.lower() in element_text)
            
            if matches_count > 0:
                # Calculate confidence based on proportion of matched keywords
                confidence = min(0.9, matches_count / len(keywords) * 0.8)
                matches.append((code, confidence))
        
        return sorted(matches, key=lambda m: m[1], reverse=True)


class ElementTypeRule(MappingRule):
    """Map elements based on their element type."""
    
    def __init__(self, type_to_codes: Dict[ElementType, List[str]]):
        """
        Initialize with mappings from element types to taxonomy codes.
        
        Args:
            type_to_codes: Dictionary mapping element types to lists of taxonomy codes
        """
        super().__init__(
            name="Element Type",
            description="Maps elements based on their classification type"
        )
        self.type_to_codes = type_to_codes
    
    def apply(self, element: Dict, taxonomy: TaxonomyManager) -> List[Tuple[str, float]]:
        """
        Apply element type matching.
        
        Args:
            element: The policy element to map
            taxonomy: The taxonomy to map against
            
        Returns:
            List of tuples (taxonomy_code, confidence_score)
        """
        matches = []
        element_type = element.get("type")
        
        if not element_type:
            return []
        
        try:
            element_type_enum = ElementType(element_type)
            potential_codes = self.type_to_codes.get(element_type_enum, [])
            
            # All matches from element type have same base confidence
            base_confidence = 0.5
            for code in potential_codes:
                matches.append((code, base_confidence))
                
        except ValueError:
            # Element type not in our enum
            pass
        
        return matches


class SectionContextRule(MappingRule):
    """Map elements based on their document section context."""
    
    def __init__(self, section_type_to_codes: Dict[str, List[str]]):
        """
        Initialize with mappings from section types to taxonomy codes.
        
        Args:
            section_type_to_codes: Dictionary mapping section types to taxonomy codes
        """
        super().__init__(
            name="Section Context",
            description="Maps elements based on their document section"
        )
        self.section_type_to_codes = section_type_to_codes
    
    def apply(self, element: Dict, taxonomy: TaxonomyManager) -> List[Tuple[str, float]]:
        """
        Apply section context matching.
        
        Args:
            element: The policy element to map
            taxonomy: The taxonomy to map against
            
        Returns:
            List of tuples (taxonomy_code, confidence_score)
        """
        matches = []
        section_type = element.get("section_type")
        
        if not section_type:
            return []
        
        potential_codes = self.section_type_to_codes.get(section_type, [])
        
        # Section context provides medium confidence
        base_confidence = 0.6
        for code in potential_codes:
            matches.append((code, base_confidence))
        
        return matches


class TitleMatchRule(MappingRule):
    """Map elements based on their title or heading."""
    
    def __init__(self):
        """Initialize the title match rule."""
        super().__init__(
            name="Title Match",
            description="Maps elements based on similarity between titles and taxonomy names"
        )
    
    def apply(self, element: Dict, taxonomy: TaxonomyManager) -> List[Tuple[str, float]]:
        """
        Apply title matching.
        
        Args:
            element: The policy element to map
            taxonomy: The taxonomy to map against
            
        Returns:
            List of tuples (taxonomy_code, confidence_score)
        """
        matches = []
        element_title = element.get("title", "")
        
        if not element_title:
            return []
        
        # Get all taxonomy nodes
        all_nodes = taxonomy.nodes.values()
        
        for node in all_nodes:
            # Calculate similarity between title and node name
            similarity = difflib.SequenceMatcher(None, 
                                                element_title.lower(), 
                                                node.name.lower()).ratio()
            
            # Only include reasonably similar matches
            if similarity > 0.6:
                # Scale confidence based on similarity
                confidence = similarity * 0.85  # Max confidence of 0.85
                matches.append((node.code, confidence))
        
        return sorted(matches, key=lambda m: m[1], reverse=True)[:5]  # Limit to top 5


class ExclusionPatternRule(MappingRule):
    """Map exclusion elements based on pattern matching."""
    
    def __init__(self, exclusion_patterns: Dict[str, List[str]]):
        """
        Initialize with exclusion patterns for taxonomy codes.
        
        Args:
            exclusion_patterns: Dictionary mapping taxonomy codes to exclusion patterns
        """
        super().__init__(
            name="Exclusion Pattern",
            description="Maps exclusions based on common language patterns"
        )
        self.exclusion_patterns = exclusion_patterns
    
    def apply(self, element: Dict, taxonomy: TaxonomyManager) -> List[Tuple[str, float]]:
        """
        Apply exclusion pattern matching.
        
        Args:
            element: The policy element to map
            taxonomy: The taxonomy to map against
            
        Returns:
            List of tuples (taxonomy_code, confidence_score)
        """
        matches = []
        
        # Only apply to exclusions
        if element.get("type") != "exclusion":
            return []
        
        element_text = element.get("text", "").lower()
        
        for code, patterns in self.exclusion_patterns.items():
            for pattern in patterns:
                if re.search(pattern, element_text, re.IGNORECASE):
                    # Pattern matches get high confidence
                    confidence = 0.85
                    matches.append((code, confidence))
                    break  # One match per code is enough
        
        return matches


class MappingResult:
    """Represents the result of mapping an element to the taxonomy."""
    
    def __init__(
        self,
        element_id: str,
        primary_mapping: Optional[Tuple[str, float]] = None,
        all_mappings: Optional[List[Tuple[str, float]]] = None,
        rule_contributions: Optional[Dict[str, List[Tuple[str, float]]]] = None
    ):
        """
        Initialize a mapping result.
        
        Args:
            element_id: ID of the mapped element
            primary_mapping: Tuple of (taxonomy_code, confidence) for primary mapping
            all_mappings: List of all potential mappings with confidence scores
            rule_contributions: Dictionary of rule name to list of mappings from that rule
        """
        self.element_id = element_id
        self.primary_mapping = primary_mapping or (None, 0.0)
        self.all_mappings = all_mappings or []
        self.rule_contributions = rule_contributions or {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        primary_code, primary_confidence = self.primary_mapping if self.primary_mapping else (None, 0.0)
        
        return {
            "element_id": self.element_id,
            "primary_mapping": {
                "code": primary_code,
                "confidence": primary_confidence
            },
            "all_mappings": [
                {"code": code, "confidence": confidence} 
                for code, confidence in self.all_mappings
            ],
            "rule_contributions": {
                rule_name: [
                    {"code": code, "confidence": confidence} 
                    for code, confidence in mappings
                ]
                for rule_name, mappings in self.rule_contributions.items()
            }
        }


class TaxonomyMapper:
    """
    Maps extracted policy elements to standardized taxonomy nodes with confidence scores.
    """
    
    def __init__(self, taxonomy: TaxonomyManager):
        """
        Initialize the taxonomy mapper.
        
        Args:
            taxonomy: The taxonomy to map against
        """
        self.taxonomy = taxonomy
        self.rules: List[MappingRule] = []
        self.initialize_default_rules()
    
    def initialize_default_rules(self):
        """Initialize default mapping rules."""
        # Initialize keyword matching rule
        keywords_by_code = self._build_default_keywords()
        self.rules.append(KeywordMatchRule(keywords_by_code))
        
        # Initialize element type rule
        type_to_codes = self._build_default_element_types()
        self.rules.append(ElementTypeRule(type_to_codes))
        
        # Initialize section context rule
        section_type_to_codes = self._build_default_section_types()
        self.rules.append(SectionContextRule(section_type_to_codes))
        
        # Initialize title match rule
        self.rules.append(TitleMatchRule())
        
        # Initialize exclusion pattern rule
        exclusion_patterns = self._build_default_exclusion_patterns()
        self.rules.append(ExclusionPatternRule(exclusion_patterns))
    
    def _build_default_keywords(self) -> Dict[str, List[str]]:
        """
        Build default keyword mappings for taxonomy codes.
        
        Returns:
            Dictionary mapping taxonomy codes to keyword lists
        """
        # This would be expanded in a real implementation
        return {
            "PROP.BLDG": ["building", "structure", "real property", "improvements", 
                          "fixtures", "premises"],
            "PROP.BPP": ["personal property", "business personal property", "contents", 
                         "equipment", "inventory", "furniture", "fixtures"],
            "PROP.BI": ["business interruption", "time element", "business income", 
                        "extra expense", "continuing expenses", "suspended operations"],
            "LIAB.GL": ["general liability", "premises liability", "operations liability", 
                        "bodily injury", "property damage", "personal injury"],
            "CYBER.BREACH": ["data breach", "privacy breach", "notification", "credit monitoring", 
                             "forensic investigation", "personal information", "security breach"],
            "CYBER.LIAB": ["network security", "privacy liability", "cyber liability", 
                           "data breach liability", "media liability"],
            "AUTO.LIAB": ["auto liability", "automobile liability", "vehicle liability",
                          "bodily injury", "property damage"],
            "AUTO.PHYS": ["physical damage", "comprehensive", "collision", "vehicle damage"],
            "PROF.E&O": ["errors and omissions", "professional services", "negligent act", 
                         "negligent error", "professional liability", "professional duty"]
        }
    
    def _build_default_element_types(self) -> Dict[ElementType, List[str]]:
        """
        Build default element type mappings to taxonomy codes.
        
        Returns:
            Dictionary mapping element types to lists of taxonomy codes
        """
        return {
            ElementType.COVERAGE_GRANT: ["PROP", "LIAB", "CYBER", "AUTO", "WC", "PROF", "DO", "EPL", "MARINE"],
            ElementType.EXCLUSION: ["PROP", "LIAB", "CYBER", "AUTO", "WC", "PROF", "DO", "EPL", "MARINE"],
            ElementType.CONDITION: ["PROP.ATTR", "LIAB.ATTR", "CYBER.ATTR", "AUTO.ATTR"],
            ElementType.SUB_LIMIT: ["PROP.BLDG", "PROP.BPP", "PROP.BI", "LIAB.GL", "CYBER.BREACH"],
            ElementType.RETENTION: ["PROP", "LIAB", "CYBER", "AUTO", "PROF", "DO", "EPL"],
            ElementType.EXTENSION: ["PROP.BLDG", "PROP.BPP", "PROP.BI"],
            ElementType.TERRITORY: ["LIAB.ATTR", "CYBER.ATTR", "AUTO.ATTR", "PROF.ATTR"],
            ElementType.TIME_ELEMENT: ["PROP.BI"]
        }
    
    def _build_default_section_types(self) -> Dict[str, List[str]]:
        """
        Build default section type mappings to taxonomy codes.
        
        Returns:
            Dictionary mapping section types to taxonomy codes
        """
        return {
            "declarations": ["PROP", "LIAB", "CYBER", "AUTO", "WC", "PROF", "DO", "EPL", "MARINE"],
            "insuring_agreement": ["PROP", "LIAB", "CYBER", "AUTO", "WC", "PROF", "DO", "EPL", "MARINE"],
            "coverage_section": ["PROP", "LIAB", "CYBER", "AUTO", "WC", "PROF", "DO", "EPL", "MARINE"],
            "exclusions": ["PROP", "LIAB", "CYBER", "AUTO", "WC", "PROF", "DO", "EPL", "MARINE"],
            "conditions": ["PROP.ATTR", "LIAB.ATTR", "CYBER.ATTR", "AUTO.ATTR", "WC.ATTR"],
            "definitions": ["PROP", "LIAB", "CYBER", "AUTO", "WC", "PROF", "DO", "EPL", "MARINE"],
            "endorsement": ["PROP", "LIAB", "CYBER", "AUTO", "WC", "PROF", "DO", "EPL", "MARINE"],
            "limits": ["PROP", "LIAB", "CYBER", "AUTO", "WC", "PROF", "DO", "EPL", "MARINE"]
        }
    
    def _build_default_exclusion_patterns(self) -> Dict[str, List[str]]:
        """
        Build default exclusion pattern mappings to taxonomy codes.
        
        Returns:
            Dictionary mapping taxonomy codes to exclusion patterns
        """
        return {
            "PROP.BLDG": [
                r"(damage|loss).+?(from|by|due to).+?(flood|water)",
                r"(damage|loss).+?(from|by|due to).+?(earthquake|earth movement)",
                r"wear and tear",
                r"(gradual|continuous).+?(deterioration|decay)",
                r"faulty.+?(construction|design|workmanship|materials)"
            ],
            "PROP.BPP": [
                r"(money|currency|securities|accounts|bills|notes|evidences of debt)",
                r"(animals|birds|fish)",
                r"growing crops",
                r"contraband|illegal trade"
            ],
            "PROP.BI": [
                r"(consequential loss|indirect loss)",
                r"(delay|loss of market)",
                r"(suspension|lapse|cancellation).+?(lease|license|contract|order)"
            ],
            "LIAB.GL": [
                r"(expected|intended).+?(injury|damage)",
                r"contractual liability",
                r"(liquor|alcohol).+?liability",
                r"(pollution|contamination)",
                r"(asbestos|lead|silica)"
            ],
            "CYBER.BREACH": [
                r"prior.+?(acts|events|incidents)",
                r"(failure|interruption).+?(power|utility)",
                r"(war|terrorism|hostilities)"
            ],
            "CYBER.LIAB": [
                r"(bodily injury|property damage)",
                r"(patent|trade secret).+?(infringement|violation)",
                r"(intentional|deliberate).+?(violation|disregard)"
            ],
            "AUTO.LIAB": [
                r"(racing|speed contest)",
                r"(used|operated|maintained).+?(aircraft|watercraft)",
                r"(loading|unloading).+?(property)"
            ],
            "PROF.E&O": [
                r"(dishonest|fraudulent|criminal).+?(act|conduct)",
                r"(obligation|liability).+?(pay|refund).+?(fees|compensation)"
            ]
        }
    
    def add_rule(self, rule: MappingRule) -> None:
        """
        Add a mapping rule.
        
        Args:
            rule: The rule to add
        """
        self.rules.append(rule)
    
    def map_element(self, element: Dict) -> MappingResult:
        """
        Map an element to the taxonomy using all rules.
        
        Args:
            element: The policy element to map
            
        Returns:
            A MappingResult with mapping details
        """
        element_id = element.get("id", "unknown")
        rule_contributions = {}
        all_mappings = {}  # Code -> confidence
        
        # Apply all rules and gather results
        for rule in self.rules:
            rule_mappings = rule.apply(element, self.taxonomy)
            rule_contributions[rule.name] = rule_mappings
            
            # Combine confidence scores from different rules
            for code, confidence in rule_mappings:
                if code in all_mappings:
                    # Use the maximum confidence for this code
                    all_mappings[code] = max(all_mappings[code], confidence)
                else:
                    all_mappings[code] = confidence
        
        # Convert to sorted list
        all_mappings_list = sorted(
            [(code, conf) for code, conf in all_mappings.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Determine primary mapping (highest confidence)
        primary_mapping = all_mappings_list[0] if all_mappings_list else None
        
        return MappingResult(
            element_id=element_id,
            primary_mapping=primary_mapping,
            all_mappings=all_mappings_list,
            rule_contributions=rule_contributions
        )
    
    def map_elements(self, elements: List[Dict]) -> Dict[str, MappingResult]:
        """
        Map multiple elements to the taxonomy.
        
        Args:
            elements: List of policy elements to map
            
        Returns:
            Dictionary mapping element IDs to their mapping results
        """
        results = {}
        for element in elements:
            element_id = element.get("id", "unknown")
            results[element_id] = self.map_element(element)
        
        return results
    
    def export_mappings(self, mapping_results: Dict[str, MappingResult], file_path: str) -> None:
        """
        Export mapping results to a JSON file.
        
        Args:
            mapping_results: Mapping results to export
            file_path: Path to save the results to
        """
        results_dict = {
            element_id: result.to_dict()
            for element_id, result in mapping_results.items()
        }
        
        with open(file_path, 'w') as f:
            json.dump(results_dict, f, indent=2)
    
    def get_elements_by_taxonomy(self, elements: List[Dict], mapping_results: Dict[str, MappingResult], 
                              taxonomy_code: str, min_confidence: float = 0.5) -> List[Dict]:
        """
        Get all elements mapped to a specific taxonomy code.
        
        Args:
            elements: List of all policy elements
            mapping_results: Mapping results for these elements
            taxonomy_code: Taxonomy code to filter by
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of elements that map to the specified taxonomy code
        """
        elements_by_id = {element.get("id", "unknown"): element for element in elements}
        matched_elements = []
        
        for element_id, result in mapping_results.items():
            # Check if element maps to this code with sufficient confidence
            for code, confidence in result.all_mappings:
                if code == taxonomy_code and confidence >= min_confidence:
                    if element_id in elements_by_id:
                        matched_elements.append(elements_by_id[element_id])
                    break
        
        return matched_elements
    
    def get_taxonomy_distribution(self, mapping_results: Dict[str, MappingResult]) -> Dict[str, int]:
        """
        Get distribution of elements across taxonomy codes.
        
        Args:
            mapping_results: Mapping results for elements
            
        Returns:
            Dictionary mapping taxonomy codes to element counts
        """
        distribution = {}
        
        for result in mapping_results.values():
            primary_code, _ = result.primary_mapping if result.primary_mapping else (None, 0)
            if primary_code:
                distribution[primary_code] = distribution.get(primary_code, 0) + 1
        
        return distribution
    
    def get_confidence_statistics(self, mapping_results: Dict[str, MappingResult]) -> Dict:
        """
        Calculate statistics on mapping confidence.
        
        Args:
            mapping_results: Mapping results for elements
            
        Returns:
            Dictionary with confidence statistics
        """
        confidences = []
        
        for result in mapping_results.values():
            _, confidence = result.primary_mapping if result.primary_mapping else (None, 0)
            confidences.append(confidence)
        
        if not confidences:
            return {
                "avg_confidence": 0,
                "min_confidence": 0,
                "max_confidence": 0,
                "median_confidence": 0,
                "high_confidence_count": 0,
                "medium_confidence_count": 0,
                "low_confidence_count": 0
            }
        
        high_threshold = 0.8
        medium_threshold = 0.5
        
        return {
            "avg_confidence": sum(confidences) / len(confidences),
            "min_confidence": min(confidences),
            "max_confidence": max(confidences),
            "median_confidence": sorted(confidences)[len(confidences) // 2],
            "high_confidence_count": sum(1 for c in confidences if c >= high_threshold),
            "medium_confidence_count": sum(1 for c in confidences if medium_threshold <= c < high_threshold),
            "low_confidence_count": sum(1 for c in confidences if c < medium_threshold)
        }


# Example usage
if __name__ == "__main__":
    # Create a taxonomy manager
    from taxonomy_framework import TaxonomyManager
    taxonomy = TaxonomyManager()
    
    # Create a taxonomy mapper
    mapper = TaxonomyMapper(taxonomy)
    
    # Example policy element
    sample_element = {
        "id": "el123",
        "type": "coverage_grant",
        "section_type": "insuring_agreement",
        "title": "Building Coverage",
        "text": "We will pay for direct physical loss of or damage to Covered Property "
                "at the premises described in the Declarations caused by or resulting "
                "from any Covered Cause of Loss."
    }
    
    # Map the element
    result = mapper.map_element(sample_element)
    
    # Print the results
    print(f"Element ID: {result.element_id}")
    print(f"Primary mapping: {result.primary_mapping}")
    print("All potential mappings:")
    for code, confidence in result.all_mappings:
        print(f"  {code}: {confidence:.2f}")
    
    print("\nRule contributions:")
    for rule_name, mappings in result.rule_contributions.items():
        print(f"  {rule_name}:")
        for code, confidence in mappings:
            print(f"    {code}: {confidence:.2f}")