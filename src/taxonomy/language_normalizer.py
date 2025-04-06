"""
Language Normalizer Module

This module provides functionality to normalize insurance policy language while
preserving unique provisions. It includes components for standard clause detection,
semantic equivalence analysis, and unique provision identification.
"""

import json
import re
import difflib
from typing import Dict, List, Optional, Set, Tuple, Any
import numpy as np
from pathlib import Path


class StandardClause:
    """Represents a standard insurance policy clause template."""
    
    def __init__(
        self,
        id: str,
        name: str,
        text: str,
        taxonomy_code: str,
        source: str = "",
        version: str = "",
        clause_type: str = "",
        tags: Optional[List[str]] = None
    ):
        """
        Initialize a standard clause.
        
        Args:
            id: Unique identifier for this clause
            name: Human-readable name
            text: The standard text of the clause
            taxonomy_code: Associated taxonomy code
            source: Source of the standard clause (e.g., "ISO", "ACORD")
            version: Version or form number
            clause_type: Type of clause (e.g., "coverage", "exclusion")
            tags: List of tags for categorization
        """
        self.id = id
        self.name = name
        self.text = text
        self.taxonomy_code = taxonomy_code
        self.source = source
        self.version = version
        self.clause_type = clause_type
        self.tags = tags or []
        
        # For semantic matching
        self._key_terms = self._extract_key_terms(text)
        
    def _extract_key_terms(self, text: str) -> Set[str]:
        """
        Extract key terms from the clause text for semantic matching.
        
        Args:
            text: The clause text
            
        Returns:
            Set of key terms
        """
        # Simple implementation - would be more sophisticated in practice
        # Remove common stopwords and punctuation
        stopwords = {"a", "an", "the", "in", "of", "and", "or", "to", "by", "for", 
                     "with", "as", "at", "from", "on", "is", "are", "be", "will"}
        
        # Convert to lowercase and split by non-alphanumeric characters
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Remove stopwords and return unique terms
        return {word for word in words if word not in stopwords}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "text": self.text,
            "taxonomy_code": self.taxonomy_code,
            "source": self.source,
            "version": self.version,
            "clause_type": self.clause_type,
            "tags": self.tags,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StandardClause':
        """Create from dictionary representation."""
        return cls(
            id=data["id"],
            name=data["name"],
            text=data["text"],
            taxonomy_code=data["taxonomy_code"],
            source=data.get("source", ""),
            version=data.get("version", ""),
            clause_type=data.get("clause_type", ""),
            tags=data.get("tags", [])
        )


class StandardClauseLibrary:
    """Manages a collection of standard insurance policy clauses."""
    
    def __init__(self, clauses: Optional[List[StandardClause]] = None):
        """
        Initialize the standard clause library.
        
        Args:
            clauses: Initial list of standard clauses
        """
        self.clauses: Dict[str, StandardClause] = {}
        if clauses:
            for clause in clauses:
                self.add_clause(clause)
    
    def add_clause(self, clause: StandardClause) -> None:
        """
        Add a clause to the library.
        
        Args:
            clause: Standard clause to add
        """
        self.clauses[clause.id] = clause
    
    def get_clause(self, clause_id: str) -> Optional[StandardClause]:
        """
        Get a clause by ID.
        
        Args:
            clause_id: ID of the clause to retrieve
            
        Returns:
            The standard clause if found, None otherwise
        """
        return self.clauses.get(clause_id)
    
    def get_clauses_by_taxonomy(self, taxonomy_code: str) -> List[StandardClause]:
        """
        Get all clauses for a specific taxonomy code.
        
        Args:
            taxonomy_code: Taxonomy code to filter by
            
        Returns:
            List of standard clauses with matching taxonomy code
        """
        return [clause for clause in self.clauses.values() 
                if clause.taxonomy_code == taxonomy_code]
    
    def get_clauses_by_type(self, clause_type: str) -> List[StandardClause]:
        """
        Get all clauses of a specific type.
        
        Args:
            clause_type: Type to filter by
            
        Returns:
            List of standard clauses with matching type
        """
        return [clause for clause in self.clauses.values() 
                if clause.clause_type == clause_type]
    
    def search_clauses(self, query: str) -> List[Tuple[StandardClause, float]]:
        """
        Search for clauses by text or name.
        
        Args:
            query: Search query
            
        Returns:
            List of tuples (clause, relevance_score)
        """
        results = []
        query_lower = query.lower()
        query_terms = set(re.findall(r'\b[a-zA-Z]{3,}\b', query_lower))
        
        for clause in self.clauses.values():
            # Check for exact substring match in name
            name_match = query_lower in clause.name.lower()
            
            # Calculate term overlap with clause text
            term_overlap = len(query_terms.intersection(clause._key_terms)) / max(1, len(query_terms))
            
            # Text similarity using sequence matcher
            text_similarity = difflib.SequenceMatcher(None, query_lower, clause.text.lower()).ratio()
            
            # Combined relevance score
            relevance = max(
                0.95 if name_match else 0,  # High score for name match
                term_overlap * 0.8,         # Term overlap score
                text_similarity * 0.7       # Text similarity score
            )
            
            if relevance > 0.2:  # Minimum threshold
                results.append((clause, relevance))
        
        # Sort by relevance score descending
        return sorted(results, key=lambda x: x[1], reverse=True)
    
    def save_library(self, file_path: str) -> None:
        """
        Save the library to a JSON file.
        
        Args:
            file_path: Path to save the file to
        """
        data = {
            "clauses": [clause.to_dict() for clause in self.clauses.values()]
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_library(self, file_path: str) -> None:
        """
        Load a library from a JSON file.
        
        Args:
            file_path: Path to load the library from
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        self.clauses = {}
        for clause_data in data["clauses"]:
            clause = StandardClause.from_dict(clause_data)
            self.clauses[clause.id] = clause
    
    def initialize_default_library(self) -> None:
        """Initialize with a default set of standard clauses."""
        # Property Insurance - Building Coverage
        self.add_clause(StandardClause(
            id="STD-PROP-BLDG-001",
            name="Standard Building Coverage Grant",
            text=("We will pay for direct physical loss of or damage to Covered Property "
                  "at the premises described in the Declarations caused by or resulting "
                  "from any Covered Cause of Loss."),
            taxonomy_code="PROP.BLDG",
            source="ISO",
            version="CP 00 10",
            clause_type="coverage_grant"
        ))
        
        self.add_clause(StandardClause(
            id="STD-PROP-BLDG-002",
            name="Debris Removal Coverage",
            text=("We will pay your expense to remove debris of Covered Property and other "
                  "debris that is on the described premises, when such debris is caused by "
                  "or results from a Covered Cause of Loss that occurs during the policy period."),
            taxonomy_code="PROP.BLDG.DEBRISREM",
            source="ISO",
            version="CP 00 10",
            clause_type="coverage_extension"
        ))
        
        # Property Insurance - Water Damage Exclusion
        self.add_clause(StandardClause(
            id="STD-PROP-EXCL-001",
            name="Standard Water Damage Exclusion",
            text=("We will not pay for loss or damage caused directly or indirectly by "
                  "water that backs up or overflows or is otherwise discharged from a "
                  "sewer, drain, sump, sump pump or related equipment."),
            taxonomy_code="PROP.BLDG",
            source="ISO",
            version="CP 10 30",
            clause_type="exclusion"
        ))
        
        # Liability Insurance - CGL Coverage Grant
        self.add_clause(StandardClause(
            id="STD-LIAB-GL-001",
            name="Standard CGL Bodily Injury Coverage",
            text=("We will pay those sums that the insured becomes legally obligated to pay "
                  "as damages because of \"bodily injury\" or \"property damage\" to which this "
                  "insurance applies. We will have the right and duty to defend the insured "
                  "against any \"suit\" seeking those damages."),
            taxonomy_code="LIAB.GL",
            source="ISO",
            version="CG 00 01",
            clause_type="coverage_grant"
        ))
        
        # Cyber Insurance - Data Breach Response
        self.add_clause(StandardClause(
            id="STD-CYBER-BREACH-001",
            name="Standard Data Breach Response Coverage",
            text=("We will pay for reasonable and necessary expenses incurred by you with "
                  "our prior consent in response to an actual or suspected data breach, including: "
                  "1. forensic services to determine the cause and extent of the breach; "
                  "2. notification services to comply with breach notification laws; "
                  "3. call center services; and "
                  "4. credit monitoring services."),
            taxonomy_code="CYBER.BREACH",
            source="NAIC",
            clause_type="coverage_grant"
        ))
        
        # Add more standard clauses as needed


class SemanticEquivalenceDetector:
    """
    Detects when policy language is semantically equivalent to 
    standard clauses, even if the wording differs.
    """
    
    def __init__(self, clause_library: StandardClauseLibrary):
        """
        Initialize the detector.
        
        Args:
            clause_library: Library of standard clauses to compare against
        """
        self.clause_library = clause_library
    
    def find_equivalent_clause(self, text: str) -> Tuple[Optional[StandardClause], float]:
        """
        Find the most semantically equivalent standard clause.
        
        Args:
            text: The policy text to analyze
            
        Returns:
            Tuple of (most equivalent clause, similarity score),
            or (None, 0.0) if no equivalent found
        """
        # Normalize the text
        normalized_text = self._normalize_text(text)
        
        best_match = None
        best_score = 0.0
        
        # Basic approach: use sequence matcher for similarity
        for clause in self.clause_library.clauses.values():
            normalized_clause = self._normalize_text(clause.text)
            similarity = difflib.SequenceMatcher(None, 
                                             normalized_text, 
                                             normalized_clause).ratio()
            
            # Apply term overlap enhancement
            text_terms = set(re.findall(r'\b[a-zA-Z]{3,}\b', normalized_text))
            clause_terms = clause._key_terms
            term_overlap = len(text_terms.intersection(clause_terms)) / max(1, len(clause_terms))
            
            # Combined score
            score = (similarity * 0.7) + (term_overlap * 0.3)
            
            if score > best_score:
                best_score = score
                best_match = clause
        
        # Threshold for equivalence
        if best_score < 0.75:  # Configurable threshold
            return None, 0.0
            
        return best_match, best_score
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove excess whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation that doesn't affect meaning
        text = re.sub(r'[,;:\(\)\[\]]', ' ', text)
        
        # Replace common synonym terms
        synonyms = {
            r'\bpremises\b': 'property',
            r'\bbuilding\b': 'structure',
            r'\bstructure\b': 'building',
            r'\bpay\b': 'provide',
            r'\bprovide\b': 'pay',
            r'\bcovered property\b': 'insured property',
            r'\binsured property\b': 'covered property',
            r'\bcovered cause of loss\b': 'insured peril',
            r'\binsured peril\b': 'covered cause of loss'
        }
        
        for pattern, replacement in synonyms.items():
            text = re.sub(pattern, replacement, text)
        
        return text.strip()


class UniqueProvisionDetector:
    """
    Detects unique provisions in policy language that should be preserved.
    """
    
    def __init__(self, clause_library: StandardClauseLibrary, 
                equivalence_detector: SemanticEquivalenceDetector):
        """
        Initialize the detector.
        
        Args:
            clause_library: Library of standard clauses
            equivalence_detector: Semantic equivalence detector
        """
        self.clause_library = clause_library
        self.equivalence_detector = equivalence_detector
    
    def analyze_provision(self, element: Dict) -> Dict:
        """
        Analyze a policy element to detect uniqueness.
        
        Args:
            element: Policy element to analyze
            
        Returns:
            Analysis results including uniqueness status
        """
        element_text = element.get("text", "")
        element_type = element.get("type", "")
        
        # Find semantically equivalent standard clause
        equivalent_clause, similarity_score = self.equivalence_detector.find_equivalent_clause(element_text)
        
        # Calculate uniqueness metrics
        uniqueness_score = 1.0 - similarity_score if equivalent_clause else 1.0
        
        # Filter clauses by type for additional comparison
        similar_type_clauses = self.clause_library.get_clauses_by_type(element_type)
        
        # Identify unique phrases or terms
        unique_phrases = self._identify_unique_phrases(element_text, similar_type_clauses)
        
        # Determine if provision is unique
        is_unique = uniqueness_score > 0.25 or len(unique_phrases) > 0
        
        # Final analysis
        analysis = {
            "is_unique": is_unique,
            "uniqueness_score": uniqueness_score,
            "closest_standard_clause": equivalent_clause.id if equivalent_clause else None,
            "similarity_score": similarity_score,
            "unique_phrases": unique_phrases
        }
        
        return analysis
    
    def _identify_unique_phrases(self, text: str, comparison_clauses: List[StandardClause]) -> List[str]:
        """
        Identify unique phrases in text compared to standard clauses.
        
        Args:
            text: Text to analyze
            comparison_clauses: Clauses to compare against
            
        Returns:
            List of unique phrases found
        """
        # This would be more sophisticated in practice
        
        # Extract sentences from text
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        unique_phrases = []
        
        for sentence in sentences:
            is_unique = True
            
            # Compare with each standard clause
            for clause in comparison_clauses:
                clause_sentences = re.split(r'(?<=[.!?])\s+', clause.text)
                
                # Check if sentence is similar to any in the standard clause
                for clause_sentence in clause_sentences:
                    similarity = difflib.SequenceMatcher(None, 
                                                     sentence.lower(), 
                                                     clause_sentence.lower()).ratio()
                    
                    if similarity > 0.7:  # Configurable threshold
                        is_unique = False
                        break
                
                if not is_unique:
                    break
            
            if is_unique and len(sentence) > 20:  # Only include substantial phrases
                unique_phrases.append(sentence)
        
        return unique_phrases


class LanguageNormalizer:
    """
    Normalizes policy language while preserving unique provisions.
    """
    
    def __init__(self, clause_library: StandardClauseLibrary):
        """
        Initialize the normalizer.
        
        Args:
            clause_library: Library of standard clauses
        """
        self.clause_library = clause_library
        self.equivalence_detector = SemanticEquivalenceDetector(clause_library)
        self.unique_detector = UniqueProvisionDetector(clause_library, self.equivalence_detector)
    
    def normalize_element(self, element: Dict) -> Dict:
        """
        Normalize a policy element's language.
        
        Args:
            element: Policy element to normalize
            
        Returns:
            Normalized element with mapping and uniqueness information
        """
        element_id = element.get("id", "unknown")
        element_text = element.get("text", "")
        element_type = element.get("type", "")
        
        # Analyze uniqueness
        uniqueness_analysis = self.unique_detector.analyze_provision(element)
        
        # Find equivalent standard clause
        equivalent_clause, similarity_score = self.equivalence_detector.find_equivalent_clause(element_text)
        
        # Create normalized element
        normalized = element.copy()
        
        # If highly similar to a standard clause, use the standard text
        if equivalent_clause and similarity_score > 0.9 and not uniqueness_analysis["is_unique"]:
            normalized["normalized_text"] = equivalent_clause.text
            normalized["normalization_source"] = "standard_clause"
            normalized["standard_clause_id"] = equivalent_clause.id
        else:
            # Keep original text but mark as unique
            normalized["normalized_text"] = element_text
            normalized["normalization_source"] = "original"
            normalized["standard_clause_id"] = None
        
        # Add analysis information
        normalized["uniqueness_analysis"] = uniqueness_analysis
        normalized["similarity_score"] = similarity_score
        
        return normalized
    
    def normalize_elements(self, elements: List[Dict]) -> List[Dict]:
        """
        Normalize multiple policy elements.
        
        Args:
            elements: List of policy elements to normalize
            
        Returns:
            List of normalized elements
        """
        return [self.normalize_element(element) for element in elements]
    
    def generate_normalization_report(self, normalized_elements: List[Dict]) -> Dict:
        """
        Generate a summary report of normalization results.
        
        Args:
            normalized_elements: List of normalized elements
            
        Returns:
            Report summary statistics
        """
        total_elements = len(normalized_elements)
        standardized_count = sum(1 for e in normalized_elements if e.get("normalization_source") == "standard_clause")
        unique_count = sum(1 for e in normalized_elements if e.get("uniqueness_analysis", {}).get("is_unique", False))
        
        # Group by standard clause
        standard_clause_counts = {}
        for element in normalized_elements:
            clause_id = element.get("standard_clause_id")
            if clause_id:
                standard_clause_counts[clause_id] = standard_clause_counts.get(clause_id, 0) + 1
        
        # Calculate average similarity score
        avg_similarity = sum(e.get("similarity_score", 0) for e in normalized_elements) / total_elements
        
        return {
            "total_elements": total_elements,
            "standardized_count": standardized_count,
            "standardized_percentage": (standardized_count / total_elements) * 100 if total_elements > 0 else 0,
            "unique_count": unique_count,
            "unique_percentage": (unique_count / total_elements) * 100 if total_elements > 0 else 0,
            "average_similarity_score": avg_similarity,
            "standard_clause_usage": standard_clause_counts,
        }
    
    def export_normalized_elements(self, normalized_elements: List[Dict], file_path: str) -> None:
        """
        Export normalized elements to a JSON file.
        
        Args:
            normalized_elements: Normalized elements to export
            file_path: Path to save the results to
        """
        with open(file_path, 'w') as f:
            json.dump(normalized_elements, f, indent=2)


# Example usage
if __name__ == "__main__":
    # Create a standard clause library
    library = StandardClauseLibrary()
    library.initialize_default_library()
    
    # Create a language normalizer
    normalizer = LanguageNormalizer(library)
    
    # Example policy elements
    sample_elements = [
        {
            "id": "el1",
            "type": "coverage_grant",
            "text": "We will pay for direct physical loss of or damage to Covered Property "
                    "at the premises described in the Declarations caused by or resulting "
                    "from any Covered Cause of Loss."
        },
        {
            "id": "el2",
            "type": "exclusion",
            "text": "We do not cover loss or damage caused by or resulting from water "
                    "that backs up from a sewer, drain or sump pump."
        },
        {
            "id": "el3",
            "type": "coverage_grant",
            "text": "We shall reimburse the insured for direct physical damage to the "
                    "structure identified in the policy schedule resulting from an "
                    "occurrence during the policy period. Payment shall not exceed "
                    "the limits specified in section III."
        }
    ]
    
    # Normalize the elements
    normalized_elements = normalizer.normalize_elements(sample_elements)
    
    # Print the results
    for element in normalized_elements:
        print(f"Element ID: {element['id']}")
        print(f"Original text: {element['text'][:50]}...")
        print(f"Normalized text: {element['normalized_text'][:50]}...")
        print(f"Normalization source: {element['normalization_source']}")
        print(f"Standard clause ID: {element['standard_clause_id']}")
        print(f"Is unique: {element['uniqueness_analysis']['is_unique']}")
        print(f"Uniqueness score: {element['uniqueness_analysis']['uniqueness_score']:.2f}")
        print(f"Similarity score: {element['similarity_score']:.2f}")
        print()
    
    # Generate a report
    report = normalizer.generate_normalization_report(normalized_elements)
    print("Normalization Report:")
    for key, value in report.items():
        print(f"  {key}: {value}")