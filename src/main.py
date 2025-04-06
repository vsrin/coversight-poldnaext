"""
Main module for the Policy DNA Extractor.

This module orchestrates the complete policy analysis process, coordinating both
document processing/segmentation and element extraction/classification stages.
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
        
        # Save the enhanced document map
        output_path = self._save_document_map(enhanced_document_map, document_path)
        
        # Calculate and display processing time
        end_time = time.time()
        processing_time = end_time - start_time
        print(f"Document processing complete in {processing_time:.2f} seconds.")
        print(f"Policy DNA extracted and saved to: {output_path}")
        
        # Print summary of extracted elements
        self._print_extraction_summary(enhanced_document_map)
        
        return enhanced_document_map
    
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

def main():
    """Main entry point for the Policy DNA Extractor."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Extract Policy DNA from insurance documents")
    parser.add_argument("document", help="Path to the insurance document file")
    parser.add_argument("--output-dir", help="Directory to save output files")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--skip-relationships", action="store_true", help="Skip relationship analysis")
    
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
    extractor.process_document(args.document)

if __name__ == "__main__":
    main()