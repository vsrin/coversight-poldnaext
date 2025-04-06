"""
Main module for the Policy DNA Extractor.

This module orchestrates the complete policy analysis process, coordinating all five phases:
1. Document Processing and Segmentation
2. Element Extraction and Classification
3. Deep Language Analysis
4. Cross-Reference and Dependency Mapping
5. Standardization and Taxonomy Mapping (New)
"""

import os
import json
import argparse
import time
from typing import Dict, List, Optional
from config.config import get_config, AppConfig
from src.document_parser import DocumentParser
from src.structure_analyzer import StructureAnalyzer, LLMClient
from src.section_classifier import SectionClassifier
from src.document_mapper import DocumentMapper
from src.element_extractor import ElementExtractor
from src.element_classifier import ElementClassifier
from src.relationship_analyzer import ElementRelationshipAnalyzer
from src.element_mapper import ElementMapper
from src.intent_analyzer import IntentAnalyzer
from src.conditional_language_detector import ConditionalLanguageDetector
from src.term_extractor import TermExtractor
from src.language_mapper import LanguageMapper
# Phase 4 imports
from src.reference_detector import ReferenceDetector
from src.dependency_analyzer import DependencyAnalyzer
from src.conflict_identifier import ConflictIdentifier
from src.graph_builder import GraphBuilder
# Phase 5 imports (new)
from src.taxonomy.taxonomy_framework import TaxonomyManager
from src.taxonomy.taxonomy_extensions import create_extended_taxonomy
from src.taxonomy.taxonomy_mapper import TaxonomyMapper
from src.taxonomy.language_normalizer import StandardClauseLibrary, LanguageNormalizer
from src.taxonomy.policy_structure_builder import PolicyStructureBuilder
from src.taxonomy.taxonomy_visualizer import TaxonomyVisualizer

class PolicyDNAExtractor:
    """Main orchestrator for policy DNA extraction."""
    
    def __init__(self, config: Optional[AppConfig] = None):
        """
        Initialize the Policy DNA Extractor.
        
        Args:
            config: Application configuration
        """
        self.config = config or get_config()
        
        # Initialize LLM client
        self.llm_client = LLMClient(self.config.llm)
        
        # Initialize document processing components
        self.document_parser = DocumentParser(self.config.parser)
        self.structure_analyzer = StructureAnalyzer(self.llm_client)
        self.section_classifier = SectionClassifier(self.llm_client)
        self.document_mapper = DocumentMapper()
        
        # Initialize element processing components
        self.element_extractor = ElementExtractor(self.llm_client)
        self.element_classifier = ElementClassifier(self.llm_client)
        self.relationship_analyzer = ElementRelationshipAnalyzer(self.llm_client)
        self.element_mapper = ElementMapper()
        
        # Initialize deep language analysis components
        self.intent_analyzer = IntentAnalyzer(self.llm_client)
        self.conditional_language_detector = ConditionalLanguageDetector(self.llm_client)
        self.term_extractor = TermExtractor(self.llm_client)
        self.language_mapper = LanguageMapper()
        
        # Initialize cross-reference and dependency mapping components
        self.reference_detector = ReferenceDetector(self.config, self.llm_client)
        self.dependency_analyzer = DependencyAnalyzer(self.config, self.llm_client)
        self.conflict_identifier = ConflictIdentifier(self.config, self.llm_client)
        self.graph_builder = GraphBuilder(self.config)
        
        # Initialize standardization and taxonomy mapping components (new)
        self.taxonomy_manager = create_extended_taxonomy()
        self.taxonomy_mapper = TaxonomyMapper(self.taxonomy_manager)
        self.clause_library = StandardClauseLibrary()
        self.clause_library.initialize_default_library()
        self.language_normalizer = LanguageNormalizer(self.clause_library)
        self.policy_structure_builder = PolicyStructureBuilder()
        self.taxonomy_visualizer = TaxonomyVisualizer()
        
        # Create output directory if it doesn't exist
        os.makedirs(self.config.output_dir, exist_ok=True)
    
    def process_document(self, document_path: str) -> Dict:
        """
        Process a document and extract its policy DNA.
        
        Args:
            document_path: Path to the document file
            
        Returns:
            Document map with extracted policy DNA
            
        Raises:
            FileNotFoundError: If the document file is not found
            ValueError: If the document format is not supported
        """
        print(f"Processing document: {document_path}")
        start_time = time.time()
        
        # PHASE 1: Document Processing and Segmentation
        
        # Step 1: Parse the document
        print("Step 1: Parsing document...")
        document_info = self.document_parser.parse_document(document_path)
        
        # Step 2: Analyze document structure
        print("Step 2: Analyzing document structure...")
        document_structure = self.structure_analyzer.analyze_structure(document_info)
        
        # Step 3: Classify sections
        print("Step 3: Classifying sections...")
        classified_sections = self.section_classifier.classify_sections(document_structure['sections'])
        
        # Step 4: Create document map
        print("Step 4: Creating document map...")
        document_map = self.document_mapper.create_document_map(document_info, classified_sections)
        
        # Save phase 1 results if in debug mode
        if self.config.debug_mode:
            self._save_intermediate_result(document_map, document_path, "phase1_document_map")
        
        # PHASE 2: Element Extraction and Classification
        
        # Step 5: Extract elements from sections
        print("Step 5: Extracting policy elements...")
        all_elements = []
        
        for section in classified_sections:
            try:
                print(f"  Extracting elements from section: {section.get('title', 'Untitled')}")
                elements = self.element_extractor.extract_elements(section)
                
                if elements:
                    print(f"  Found {len(elements)} elements")
                    all_elements.extend(elements)
            except Exception as e:
                print(f"  Error extracting elements from section {section.get('title', 'Untitled')}: {str(e)}")
        
        # Save intermediate results if in debug mode
        if self.config.debug_mode:
            self._save_intermediate_result(all_elements, document_path, "extracted_elements")
        
        # Step 6: Classify elements
        print("Step 6: Classifying policy elements...")
        classified_elements = []
        
        for section in classified_sections:
            try:
                # Get elements for this section
                section_elements = [e for e in all_elements if e.get('section_id') == section.get('id')]
                
                if section_elements:
                    print(f"  Classifying elements in section: {section.get('title', 'Untitled')}")
                    classified = self.element_classifier.classify_elements(section_elements, section)
                    classified_elements.extend(classified)
            except Exception as e:
                print(f"  Error classifying elements in section {section.get('title', 'Untitled')}: {str(e)}")
        
        # Save intermediate results if in debug mode
        if self.config.debug_mode:
            self._save_intermediate_result(classified_elements, document_path, "classified_elements")
        
        # Step 7: Analyze element relationships
        print("Step 7: Analyzing element relationships...")
        enhanced_elements = []
        
        if self.config.element_extraction.analyze_relationships:
            for section in classified_sections:
                try:
                    # Get elements for this section
                    section_elements = [e for e in classified_elements if e.get('section_id') == section.get('id')]
                    
                    if section_elements:
                        print(f"  Analyzing relationships in section: {section.get('title', 'Untitled')}")
                        with_relationships = self.relationship_analyzer.analyze_relationships(section_elements, section)
                        enhanced_elements.extend(with_relationships)
                except Exception as e:
                    print(f"  Error analyzing relationships in section {section.get('title', 'Untitled')}: {str(e)}")
                    # If error, just add the classified elements without relationships
                    section_elements = [e for e in classified_elements if e.get('section_id') == section.get('id')]
                    enhanced_elements.extend(section_elements)
        else:
            # Skip relationship analysis if disabled in config
            enhanced_elements = classified_elements
        
        # Save intermediate results if in debug mode
        if self.config.debug_mode:
            self._save_intermediate_result(enhanced_elements, document_path, "elements_with_relationships")
        
        # Step 8: Create element map
        print("Step 8: Creating element map...")
        enhanced_document_map = self.element_mapper.create_element_map(enhanced_elements, document_map)
        
        # Save phase 2 results if in debug mode
        if self.config.debug_mode:
            self._save_intermediate_result(enhanced_document_map, document_path, "phase2_element_map")
        
        # PHASE 3: Deep Language Analysis
        
        # Step 9: Analyze element intent
        print("Step 9: Analyzing element intent...")
        elements_with_intent = []
        
        try:
            elements_with_intent = self.intent_analyzer.analyze_intent(enhanced_elements)
            if self.config.debug_mode:
                self._save_intermediate_result(elements_with_intent, document_path, "elements_with_intent")
        except Exception as e:
            print(f"  Error analyzing element intent: {str(e)}")
            elements_with_intent = enhanced_elements  # Fall back to previous elements
        
        # Step 10: Detect conditional language
        print("Step 10: Detecting conditional language...")
        elements_with_conditions = []
        
        try:
            elements_with_conditions = self.conditional_language_detector.detect_conditions(elements_with_intent)
            if self.config.debug_mode:
                self._save_intermediate_result(elements_with_conditions, document_path, "elements_with_conditions")
        except Exception as e:
            print(f"  Error detecting conditional language: {str(e)}")
            elements_with_conditions = elements_with_intent  # Fall back to previous elements
        
        # Step 11: Extract specific terms
        print("Step 11: Extracting specific terms...")
        elements_with_terms = []
        
        try:
            elements_with_terms = self.term_extractor.extract_terms(elements_with_conditions)
            if self.config.debug_mode:
                self._save_intermediate_result(elements_with_terms, document_path, "elements_with_terms")
        except Exception as e:
            print(f"  Error extracting specific terms: {str(e)}")
            elements_with_terms = elements_with_conditions  # Fall back to previous elements
        
        # Step 12: Create language map
        print("Step 12: Creating language map...")
        language_document_map = {}
        
        try:
            language_document_map = self.language_mapper.create_language_map(elements_with_terms, enhanced_document_map)
        except Exception as e:
            print(f"  Error creating language map: {str(e)}")
            language_document_map = enhanced_document_map  # Fall back to phase 2 document map
        
        # Save phase 3 results if in debug mode
        if self.config.debug_mode:
            self._save_intermediate_result(language_document_map, document_path, "phase3_language_map")
            
        # PHASE 4: Cross-Reference and Dependency Mapping
        
        # Step 13: Detect references
        print("Step 13: Detecting cross-references...")
        references = []
        
        try:
            references = self.reference_detector.detect_references(language_document_map)
            if self.config.debug_mode:
                self._save_intermediate_result(references, document_path, "detected_references")
        except Exception as e:
            print(f"  Error detecting references: {str(e)}")
            # Create empty references if error occurs
            references = []
        
        # Step 14: Analyze dependencies
        print("Step 14: Analyzing logical dependencies...")
        dependencies = []
        
        try:
            dependencies = self.dependency_analyzer.analyze_dependencies(language_document_map, references)
            if self.config.debug_mode:
                self._save_intermediate_result(dependencies, document_path, "analyzed_dependencies")
        except Exception as e:
            print(f"  Error analyzing dependencies: {str(e)}")
            # Create empty dependencies if error occurs
            dependencies = []
        
        # Step 15: Identify conflicts
        print("Step 15: Identifying potential conflicts...")
        conflicts = []
        
        try:
            conflicts = self.conflict_identifier.identify_conflicts(language_document_map, dependencies)
            if self.config.debug_mode:
                self._save_intermediate_result(conflicts, document_path, "identified_conflicts")
        except Exception as e:
            print(f"  Error identifying conflicts: {str(e)}")
            # Create empty conflicts if error occurs
            conflicts = []
        
        # Step 16: Build relationship graph
        print("Step 16: Building relationship graph...")
        graph_result = {}
        
        try:
            graph_result = self.graph_builder.build_graph(language_document_map, references, dependencies, conflicts)
            language_document_map['cross_reference_map'] = graph_result
            if self.config.debug_mode:
                self._save_intermediate_result(graph_result, document_path, "relationship_graph")
        except Exception as e:
            print(f"  Error building relationship graph: {str(e)}")
            # Create empty graph if error occurs
            graph_result = {
                "graph_stats": {"node_count": 0, "edge_count": 0},
                "nodes": [],
                "edges": []
            }
            language_document_map['cross_reference_map'] = graph_result
        
        # Save phase 4 results if in debug mode
        if self.config.debug_mode:
            self._save_intermediate_result(language_document_map, document_path, "phase4_graph_map")
        
        # PHASE 5: Standardization and Taxonomy Mapping (New)
        print("\nPHASE 5: Standardization and Taxonomy Mapping")
        final_document_map = language_document_map
        
        # Step 17: Map elements to standardized taxonomy
        print("Step 17: Mapping elements to standardized taxonomy...")
        taxonomy_mapping_results = {}
        
        try:
            # Get all policy elements from previous phases
            all_current_elements = elements_with_terms  # Using the elements from Phase 3
            
            # Perform taxonomy mapping
            taxonomy_mapping_results = self.taxonomy_mapper.map_elements(all_current_elements)
            
            if self.config.debug_mode:
                self._save_intermediate_result(
                    {element_id: result.to_dict() for element_id, result in taxonomy_mapping_results.items()},
                    document_path, 
                    "taxonomy_mappings"
                )
                
            # Add taxonomy mapping confidence statistics
            confidence_stats = self.taxonomy_mapper.get_confidence_statistics(taxonomy_mapping_results)
            final_document_map['taxonomy_mapping_stats'] = confidence_stats
            
            # Add taxonomy distribution
            taxonomy_distribution = self.taxonomy_mapper.get_taxonomy_distribution(taxonomy_mapping_results)
            final_document_map['taxonomy_distribution'] = taxonomy_distribution
            
            print(f"  Mapped {len(taxonomy_mapping_results)} elements to standardized taxonomy")
            print(f"  Average mapping confidence: {confidence_stats['avg_confidence']:.2f}")
            print(f"  High confidence mappings: {confidence_stats['high_confidence_count']}")
            
        except Exception as e:
            print(f"  Error mapping elements to taxonomy: {str(e)}")
            # Continue with empty mapping results if error occurs
            taxonomy_mapping_results = {}
        
        # Step 18: Normalize policy language
        print("Step 18: Normalizing policy language...")
        normalized_elements = []
        
        try:
            normalized_elements = self.language_normalizer.normalize_elements(all_current_elements)
            
            if self.config.debug_mode:
                self._save_intermediate_result(normalized_elements, document_path, "normalized_elements")
            
            # Generate normalization report
            normalization_report = self.language_normalizer.generate_normalization_report(normalized_elements)
            final_document_map['language_normalization_report'] = normalization_report
            
            print(f"  Normalized {len(normalized_elements)} policy elements")
            print(f"  Standardized elements: {normalization_report['standardized_count']} ({normalization_report['standardized_percentage']:.1f}%)")
            print(f"  Unique provisions: {normalization_report['unique_count']} ({normalization_report['unique_percentage']:.1f}%)")
            
        except Exception as e:
            print(f"  Error normalizing policy language: {str(e)}")
            # Continue with original elements if error occurs
            normalized_elements = all_current_elements
        
        # Step 19: Build structured policy representation
        print("Step 19: Building structured policy representation...")
        
        try:
            # Extract policy metadata (simplified for integration)
            metadata = self._extract_policy_metadata(all_current_elements, document_info)
            
            # Build the comprehensive policy structure
            self.policy_structure_builder.set_policy_metadata(metadata)
            self.policy_structure_builder.set_document_map(document_map)
            self.policy_structure_builder.add_elements(all_current_elements)
            self.policy_structure_builder.add_taxonomy_mappings({
                element_id: result.to_dict() 
                for element_id, result in taxonomy_mapping_results.items()
            })
            self.policy_structure_builder.add_normalized_language(normalized_elements)
            self.policy_structure_builder.add_relationships(dependencies + references)
            
            policy_structure = self.policy_structure_builder.build_structure()
            
            # Add policy structure to document map
            final_document_map['standardized_policy_structure'] = policy_structure
            
            # Generate coverage summary
            coverage_summary = self.policy_structure_builder.get_coverage_summary()
            final_document_map['standardized_coverage_summary'] = coverage_summary
            
            print(f"  Created structured representation with {policy_structure['summary']['total_elements']} elements")
            print(f"  Mapped to {len(policy_structure['summary']['taxonomy_codes'])} taxonomy categories")
            
            if self.config.debug_mode:
                self._save_intermediate_result(policy_structure, document_path, "policy_structure")
                self._save_intermediate_result(coverage_summary, document_path, "coverage_summary")
            
        except Exception as e:
            print(f"  Error building structured policy representation: {str(e)}")
            # Continue without structured representation if error occurs
            final_document_map['standardized_policy_structure'] = {"error": "Failed to build structured representation"}
        
        # Step 20: Generate taxonomy visualizations
        print("Step 20: Generating taxonomy visualizations...")
        
        try:
            # Create visualizations directory
            vis_dir = os.path.join(self.config.output_dir, "visualizations")
            os.makedirs(vis_dir, exist_ok=True)
            
            # Generate base filename
            base_name = os.path.basename(document_path)
            file_name = os.path.splitext(base_name)[0]
            
            # Generate visualizations if we have a policy structure
            if 'standardized_policy_structure' in final_document_map and 'error' not in final_document_map['standardized_policy_structure']:
                policy_structure = final_document_map['standardized_policy_structure']
                
                # Generate HTML tree visualization
                tree_path = os.path.join(vis_dir, f"{file_name}_taxonomy_tree.html")
                self.taxonomy_visualizer.generate_html_tree(policy_structure, tree_path)
                
                # Generate coverage report
                coverage_path = os.path.join(vis_dir, f"{file_name}_coverage_report.html")
                self.taxonomy_visualizer.generate_coverage_report(policy_structure, coverage_path)
                
                # Generate uniqueness report
                uniqueness_path = os.path.join(vis_dir, f"{file_name}_uniqueness_report.html")
                self.taxonomy_visualizer.generate_uniqueness_report(policy_structure, uniqueness_path)
                
                # Generate JSON for external visualization
                json_path = os.path.join(vis_dir, f"{file_name}_visualization_data.json")
                self.taxonomy_visualizer.generate_json_visualization(policy_structure, json_path)
                
                print(f"  Generated taxonomy visualizations in: {vis_dir}")
                final_document_map['taxonomy_visualizations'] = {
                    "taxonomy_tree": tree_path,
                    "coverage_report": coverage_path,
                    "uniqueness_report": uniqueness_path,
                    "visualization_data": json_path
                }
            else:
                print("  Skipping visualization generation due to missing policy structure")
                
        except Exception as e:
            print(f"  Error generating taxonomy visualizations: {str(e)}")
            # Continue without visualizations if error occurs
        
        # Save phase 5 results if in debug mode
        if self.config.debug_mode:
            self._save_intermediate_result(final_document_map, document_path, "phase5_taxonomy_map")
        
        # Save the final document map
        output_path = self._save_document_map(final_document_map, document_path)
        
        # Calculate and display processing time
        end_time = time.time()
        processing_time = end_time - start_time
        print(f"Document processing complete in {processing_time:.2f} seconds.")
        print(f"Policy DNA extracted and saved to: {output_path}")
        
        # Print summary of extracted elements and language analysis
        self._print_extraction_summary(final_document_map)
        
        return final_document_map
    
    def _extract_policy_metadata(self, elements: List[Dict], document_info: Dict) -> Dict:
        """
        Extract policy metadata from elements and document info.
        
        Args:
            elements: Policy elements
            document_info: Document information
            
        Returns:
            Policy metadata
        """
        # Initialize with defaults
        metadata = {
            "policy_number": "Unknown",
            "insured_name": "Unknown",
            "effective_date": "Unknown",
            "expiration_date": "Unknown",
            "policy_type": "Unknown",
            "document_title": document_info.get("title", "Unknown"),
            "document_date": document_info.get("date", "Unknown"),
            "processing_date": time.strftime("%Y-%m-%d")
        }
        
        # Extract from document info if available
        if document_info.get("metadata"):
            doc_metadata = document_info["metadata"]
            if "policy_number" in doc_metadata:
                metadata["policy_number"] = doc_metadata["policy_number"]
            if "insured_name" in doc_metadata:
                metadata["insured_name"] = doc_metadata["insured_name"]
            if "effective_date" in doc_metadata:
                metadata["effective_date"] = doc_metadata["effective_date"]
            if "expiration_date" in doc_metadata:
                metadata["expiration_date"] = doc_metadata["expiration_date"]
            if "policy_type" in doc_metadata:
                metadata["policy_type"] = doc_metadata["policy_type"]
        
        # Look for declarations elements that might contain metadata
        for element in elements:
            if element.get("section_type") == "declarations":
                text = element.get("text", "").lower()
                
                # Simple pattern matching for metadata
                if "policy number" in text and ":" in text:
                    parts = text.split("policy number")[1].split(":", 1)
                    if len(parts) > 1:
                        policy_number = parts[1].strip().split()[0]
                        metadata["policy_number"] = policy_number
                
                if "insured" in text and ":" in text:
                    parts = text.split("insured")[1].split(":", 1)
                    if len(parts) > 1:
                        insured_name = parts[1].strip().split("\n")[0]
                        metadata["insured_name"] = insured_name
                
                if "effective date" in text and ":" in text:
                    parts = text.split("effective date")[1].split(":", 1)
                    if len(parts) > 1:
                        date = parts[1].strip().split()[0]
                        metadata["effective_date"] = date
                
                if "expiration date" in text and ":" in text:
                    parts = text.split("expiration date")[1].split(":", 1)
                    if len(parts) > 1:
                        date = parts[1].strip().split()[0]
                        metadata["expiration_date"] = date
                
                # Try to determine policy type
                policy_type_patterns = [
                    "commercial general liability",
                    "property",
                    "cyber",
                    "professional liability",
                    "directors and officers",
                    "employment practices liability"
                ]
                
                for pattern in policy_type_patterns:
                    if pattern in text:
                        metadata["policy_type"] = pattern.title()
                        break
        
        return metadata
    
    def _save_document_map(self, document_map: Dict, original_path: str) -> str:
        """
        Save the document map to a file.
        
        Args:
            document_map: Document map to save
            original_path: Path to the original document
            
        Returns:
            Path to the saved file
        """
        # Generate output filename based on original document name
        base_name = os.path.basename(original_path)
        file_name = os.path.splitext(base_name)[0]
        output_path = os.path.join(self.config.output_dir, f"{file_name}_policy_dna.json")
        
        # Save document map as JSON
        with open(output_path, 'w') as f:
            json.dump(document_map, f, indent=2)
            
        return output_path
    
    def _save_intermediate_result(self, data: any, original_path: str, stage_name: str) -> None:
        """
        Save intermediate processing results for debugging.
        
        Args:
            data: Data to save
            original_path: Path to the original document
            stage_name: Name of the processing stage
        """
        base_name = os.path.basename(original_path)
        file_name = os.path.splitext(base_name)[0]
        debug_dir = os.path.join(self.config.output_dir, "debug")
        os.makedirs(debug_dir, exist_ok=True)
        
        output_path = os.path.join(debug_dir, f"{file_name}_{stage_name}.json")
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"Saved intermediate result to: {output_path}")
    
    def _print_extraction_summary(self, document_map: Dict) -> None:
        """
        Print a summary of the extracted policy DNA.
        
        Args:
            document_map: The enhanced document map with elements
        """
        # Get counts
        section_count = document_map.get('section_counts', {}).get('TOTAL', 0)
        element_count = document_map.get('element_counts', {}).get('TOTAL', 0)
        
        # Print summary
        print("\nPolicy DNA Extraction Summary:")
        print(f"  Sections identified: {section_count}")
        print(f"  Elements extracted: {element_count}")
        
        # Print section counts
        print("\nSection types:")
        for section_type, count in document_map.get('section_counts', {}).items():
            if section_type != 'TOTAL':
                print(f"  - {section_type}: {count}")
        
        # Print element counts
        print("\nElement types:")
        for element_type, count in document_map.get('element_counts', {}).items():
            if element_type != 'TOTAL':
                print(f"  - {element_type}: {count}")
                
        # Print policy insights if available
        if 'policy_insights' in document_map:
            insights = document_map['policy_insights']
            print("\nKey insights:")
            
            # Coverage summary
            coverage_count = len(insights.get('coverage_summary', []))
            print(f"  - Coverage provisions: {coverage_count}")
            
            # Exclusions
            exclusion_count = len(insights.get('key_exclusions', []))
            print(f"  - Key exclusions: {exclusion_count}")
            
            # Definitions
            definition_count = len(insights.get('key_definitions', []))
            print(f"  - Defined terms: {definition_count}")
            
            # Monetary provisions
            monetary_count = len(insights.get('monetary_provisions', []))
            print(f"  - Monetary provisions: {monetary_count}")
        
        # Print language insights if available (from Phase 3)
        if 'language_insights' in document_map:
            language_insights = document_map['language_insights']
            print("\nLanguage Analysis Insights:")
            
            # Coverage summary
            coverage_summary = language_insights.get('coverage_summary', {})
            if coverage_summary:
                print(f"  - Coverage grants: {len(coverage_summary.get('coverage_grants', []))}")
                print(f"  - Key exclusions: {len(coverage_summary.get('key_exclusions', []))}")
                print(f"  - Key limitations: {len(coverage_summary.get('key_limitations', []))}")
            
            # Conditions
            key_conditions = language_insights.get('key_conditions', [])
            print(f"  - Key conditions: {len(key_conditions)}")
            
            # Defined terms
            defined_terms = language_insights.get('defined_terms_usage', {})
            if defined_terms:
                print(f"  - Defined terms: {defined_terms.get('defined_terms_count', 0)}")
                print(f"  - Terms with definitions: {defined_terms.get('terms_with_definitions', 0)}")
            
            # Interpretation challenges
            challenges = language_insights.get('interpretation_challenges', [])
            print(f"  - Potential interpretation challenges: {len(challenges)}")
            
        # Print cross-reference insights if available (from Phase 4)
        if 'cross_reference_map' in document_map:
            cross_ref_map = document_map.get('cross_reference_map', {})
            print("\nCross-Reference Insights:")
            
            # Graph statistics
            graph_stats = cross_ref_map.get('graph_stats', {})
            print(f"  - Total nodes: {graph_stats.get('node_count', 0)}")
            print(f"  - Total relationships: {graph_stats.get('edge_count', 0)}")
            
            # Reference types
            ref_types = cross_ref_map.get('reference_type_counts', {})
            for ref_type, count in ref_types.items():
                print(f"  - {ref_type} references: {count}")
            
            # Conflict count
            conflicts = cross_ref_map.get('conflicts', [])
            print(f"  - Potential conflicts: {len(conflicts)}")
            
            # Most connected elements
            most_connected = cross_ref_map.get('most_referenced', [])
            if most_connected and len(most_connected) > 0:
                print("\n  Most referenced elements:")
                for i, element in enumerate(most_connected[:3]):
                    print(f"    {i+1}. {element.get('element_text', '')[:50]}... ({element.get('reference_count', 0)} references)")
        
        # Print taxonomy and standardization insights (from Phase 5)
        if 'standardized_policy_structure' in document_map:
            print("\nTaxonomy Standardization Insights:")
            
            # Taxonomy mapping stats
            taxonomy_stats = document_map.get('taxonomy_mapping_stats', {})
            if taxonomy_stats:
                print(f"  - Average mapping confidence: {taxonomy_stats.get('avg_confidence', 0):.2f}")
                print(f"  - High confidence mappings: {taxonomy_stats.get('high_confidence_count', 0)}")
                print(f"  - Medium confidence mappings: {taxonomy_stats.get('medium_confidence_count', 0)}")
                print(f"  - Low confidence mappings: {taxonomy_stats.get('low_confidence_count', 0)}")
            
            # Language normalization stats
            norm_report = document_map.get('language_normalization_report', {})
            if norm_report:
                print(f"  - Standardized elements: {norm_report.get('standardized_count', 0)} ({norm_report.get('standardized_percentage', 0):.1f}%)")
                print(f"  - Unique provisions: {norm_report.get('unique_count', 0)} ({norm_report.get('unique_percentage', 0):.1f}%)")
            
            # Taxonomy distribution
            taxonomy_dist = document_map.get('taxonomy_distribution', {})
            if taxonomy_dist:
                print("\n  Top taxonomy categories:")
                sorted_dist = sorted(taxonomy_dist.items(), key=lambda x: x[1], reverse=True)
                for i, (code, count) in enumerate(sorted_dist[:5]):
                    print(f"    {i+1}. {code}: {count} elements")
            
            # Visualization paths
            if 'taxonomy_visualizations' in document_map:
                print("\n  Generated visualizations:")
                for vis_type, path in document_map['taxonomy_visualizations'].items():
                    print(f"    - {vis_type.replace('_', ' ').title()}: {os.path.basename(path)}")

    def run_specific_phase(self, phase: int, document_path: str, input_data: Optional[Dict] = None) -> Dict:
        """
        Run a specific phase of the pipeline.
        
        Args:
            phase: Phase number (1-5)
            document_path: Path to the document file
            input_data: Optional input data from previous phases
            
        Returns:
            Results from the specified phase
        """
        print(f"Running Phase {phase} for document: {document_path}")
        
        if phase == 1:
            # Phase 1: Document Processing and Segmentation
            print("Running Phase 1: Document Processing and Segmentation")
            
            # Step 1: Parse the document
            document_info = self.document_parser.parse_document(document_path)
            
            # Step 2: Analyze document structure
            document_structure = self.structure_analyzer.analyze_structure(document_info)
            
            # Step 3: Classify sections
            classified_sections = self.section_classifier.classify_sections(document_structure['sections'])
            
            # Step 4: Create document map
            document_map = self.document_mapper.create_document_map(document_info, classified_sections)
            
            return document_map
            
        elif phase == 2:
            # Phase 2: Element Extraction and Classification
            print("Running Phase 2: Element Extraction and Classification")
            
            if not input_data:
                raise ValueError("Input data from Phase 1 is required")
            
            document_map = input_data
            classified_sections = document_map.get('sections', [])
            
            # Extract and classify elements
            all_elements = []
            for section in classified_sections:
                elements = self.element_extractor.extract_elements(section)
                all_elements.extend(elements)
            
            classified_elements = []
            for section in classified_sections:
                section_elements = [e for e in all_elements if e.get('section_id') == section.get('id')]
                if section_elements:
                    classified = self.element_classifier.classify_elements(section_elements, section)
                    classified_elements.extend(classified)
            
            # Analyze relationships
            enhanced_elements = []
            if self.config.element_extraction.analyze_relationships:
                for section in classified_sections:
                    section_elements = [e for e in classified_elements if e.get('section_id') == section.get('id')]
                    if section_elements:
                        with_relationships = self.relationship_analyzer.analyze_relationships(section_elements, section)
                        enhanced_elements.extend(with_relationships)
            else:
                enhanced_elements = classified_elements
            
            # Create element map
            enhanced_document_map = self.element_mapper.create_element_map(enhanced_elements, document_map)
            
            return enhanced_document_map
            
        elif phase == 3:
            # Phase 3: Deep Language Analysis
            print("Running Phase 3: Deep Language Analysis")
            
            if not input_data:
                raise ValueError("Input data from Phase 2 is required")
            
            document_map = input_data
            elements = document_map.get('elements', [])
            
            # Analyze intent
            elements_with_intent = self.intent_analyzer.analyze_intent(elements)
            
            # Detect conditional language
            elements_with_conditions = self.conditional_language_detector.detect_conditions(elements_with_intent)
            
            # Extract terms
            elements_with_terms = self.term_extractor.extract_terms(elements_with_conditions)
            
            # Create language map
            language_document_map = self.language_mapper.create_language_map(elements_with_terms, document_map)
            
            return language_document_map
            
        elif phase == 4:
            # Phase 4: Cross-Reference and Dependency Mapping
            print("Running Phase 4: Cross-Reference and Dependency Mapping")
            
            if not input_data:
                raise ValueError("Input data from Phase 3 is required")
            
            document_map = input_data
            
            # Detect references
            references = self.reference_detector.detect_references(document_map)
            
            # Analyze dependencies
            dependencies = self.dependency_analyzer.analyze_dependencies(document_map, references)
            
            # Identify conflicts
            conflicts = self.conflict_identifier.identify_conflicts(document_map, dependencies)
            
            # Build graph
            graph_result = self.graph_builder.build_graph(document_map, references, dependencies, conflicts)
            document_map['cross_reference_map'] = graph_result
            
            return document_map
            
        elif phase == 5:
            # Phase 5: Standardization and Taxonomy Mapping
            print("Running Phase 5: Standardization and Taxonomy Mapping")
            
            if not input_data:
                raise ValueError("Input data from Phase 4 is required")
            
            document_map = input_data
            elements = document_map.get('elements', [])
            
            # Map elements to taxonomy
            taxonomy_mapping_results = self.taxonomy_mapper.map_elements(elements)
            
            # Add taxonomy mapping statistics
            document_map['taxonomy_mapping_stats'] = self.taxonomy_mapper.get_confidence_statistics(taxonomy_mapping_results)
            document_map['taxonomy_distribution'] = self.taxonomy_mapper.get_taxonomy_distribution(taxonomy_mapping_results)
            
            # Normalize language
            normalized_elements = self.language_normalizer.normalize_elements(elements)
            document_map['language_normalization_report'] = self.language_normalizer.generate_normalization_report(normalized_elements)
            
            # Build structured policy representation
            metadata = self._extract_policy_metadata(elements, document_map.get('document_info', {}))
            
            self.policy_structure_builder.set_policy_metadata(metadata)
            self.policy_structure_builder.set_document_map(document_map)
            self.policy_structure_builder.add_elements(elements)
            self.policy_structure_builder.add_taxonomy_mappings({
                element_id: result.to_dict() 
                for element_id, result in taxonomy_mapping_results.items()
            })
            self.policy_structure_builder.add_normalized_language(normalized_elements)
            
            references = document_map.get('references', [])
            dependencies = document_map.get('dependencies', [])
            self.policy_structure_builder.add_relationships(dependencies + references)
            
            policy_structure = self.policy_structure_builder.build_structure()
            document_map['standardized_policy_structure'] = policy_structure
            document_map['standardized_coverage_summary'] = self.policy_structure_builder.get_coverage_summary()
            
            # Generate visualizations
            if self.config.debug_mode:
                # Create visualizations directory
                vis_dir = os.path.join(self.config.output_dir, "visualizations")
                os.makedirs(vis_dir, exist_ok=True)
                
                # Generate base filename
                base_name = os.path.basename(document_path)
                file_name = os.path.splitext(base_name)[0]
                
                # Generate visualizations
                tree_path = os.path.join(vis_dir, f"{file_name}_taxonomy_tree.html")
                self.taxonomy_visualizer.generate_html_tree(policy_structure, tree_path)
                
                coverage_path = os.path.join(vis_dir, f"{file_name}_coverage_report.html")
                self.taxonomy_visualizer.generate_coverage_report(policy_structure, coverage_path)
                
                uniqueness_path = os.path.join(vis_dir, f"{file_name}_uniqueness_report.html")
                self.taxonomy_visualizer.generate_uniqueness_report(policy_structure, uniqueness_path)
                
                json_path = os.path.join(vis_dir, f"{file_name}_visualization_data.json")
                self.taxonomy_visualizer.generate_json_visualization(policy_structure, json_path)
                
                document_map['taxonomy_visualizations'] = {
                    "taxonomy_tree": tree_path,
                    "coverage_report": coverage_path,
                    "uniqueness_report": uniqueness_path,
                    "visualization_data": json_path
                }
            
            return document_map
        
        else:
            raise ValueError(f"Invalid phase number: {phase}")


def main():
    """Main entry point for the Policy DNA Extractor."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Extract Policy DNA from insurance documents")
    parser.add_argument("document", help="Path to the insurance document file")
    parser.add_argument("--output-dir", help="Directory to save output files")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--skip-relationships", action="store_true", help="Skip relationship analysis")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3, 4, 5], help="Run specific phase (1-5)")
    parser.add_argument("--input", help="Input JSON file for specific phase")
    
    args = parser.parse_args()
    
    # Update configuration if necessary
    config = get_config()
    
    if args.output_dir:
        config.output_dir = args.output_dir
        
    if args.debug:
        config.debug_mode = True
        
    if args.skip_relationships:
        config.element_extraction.analyze_relationships = False
    
    # Create and run the extractor
    extractor = PolicyDNAExtractor(config)
    
    # Process document based on specified phase
    if args.phase:
        if args.phase > 1 and not args.input:
            parser.error(f"Input JSON file is required for phase {args.phase}")
            return
        
        input_data = None
        if args.input:
            try:
                with open(args.input, 'r') as f:
                    input_data = json.load(f)
            except Exception as e:
                parser.error(f"Error loading input file: {str(e)}")
                return
        
        try:
            # Run specific phase
            result = extractor.run_specific_phase(args.phase, args.document, input_data)
            
            # Generate output filename
            base_name = os.path.basename(args.document)
            file_name = os.path.splitext(base_name)[0]
            output_path = os.path.join(config.output_dir, f"{file_name}_phase{args.phase}_result.json")
            
            # Save result
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
                
            print(f"Phase {args.phase} completed. Result saved to: {output_path}")
            
        except Exception as e:
            print(f"Error running phase {args.phase}: {str(e)}")
    else:
        # Run all phases
        try:
            extractor.process_document(args.document)
        except Exception as e:
            print(f"Error processing document: {str(e)}")

if __name__ == "__main__":
    main()