"""
Example script to demonstrate the Policy DNA Extractor.

This script creates a simple test document and processes it with the Policy DNA Extractor.
It demonstrates both document segmentation and element extraction capabilities.
"""

import os
import tempfile
import json
from docx import Document
from src.main import PolicyDNAExtractor
from config.config import get_config

def create_test_document():
    """Create a sample insurance policy document for testing."""
    doc = Document()
    
    # Add a title
    doc.add_heading('COMMERCIAL GENERAL LIABILITY POLICY', 0)
    
    # Add declarations section
    doc.add_heading('DECLARATIONS', 1)
    doc.add_paragraph('Policy Number: TEST-12345')
    doc.add_paragraph('Named Insured: ABC Corporation')
    doc.add_paragraph('Policy Period: 01/01/2025 to 01/01/2026')
    doc.add_paragraph('Limits of Insurance: $1,000,000 Each Occurrence')
    
    # Add insuring agreement
    doc.add_heading('SECTION I - INSURING AGREEMENT', 1)
    doc.add_paragraph(
        'We will pay those sums that the insured becomes legally obligated to pay as damages '
        'because of "bodily injury" or "property damage" to which this insurance applies. We will '
        'have the right and duty to defend the insured against any "suit" seeking those damages. '
        'However, we will have no duty to defend the insured against any "suit" seeking damages for '
        '"bodily injury" or "property damage" to which this insurance does not apply.'
    )
    
    doc.add_paragraph(
        'The amount we will pay for damages is limited as described in Section III - Limits Of Insurance.'
    )
    
    doc.add_paragraph(
        'This insurance applies to "bodily injury" and "property damage" only if: '
        '(1) The "bodily injury" or "property damage" is caused by an "occurrence" that takes place in the "coverage territory"; '
        '(2) The "bodily injury" or "property damage" occurs during the policy period; and '
        '(3) Prior to the policy period, no insured listed under Paragraph 1. of Section II – Who Is An Insured and no employee authorized by you to give or receive notice of an "occurrence" or claim, knew that the "bodily injury" or "property damage" had occurred, in whole or in part.'
    )
    
    # Add exclusions
    doc.add_heading('SECTION II - EXCLUSIONS', 1)
    doc.add_paragraph(
        'This insurance does not apply to:\n'
        '1. Expected or Intended Injury\n'
        '"Bodily injury" or "property damage" expected or intended from the standpoint of the insured.\n'
        '2. Contractual Liability\n'
        '"Bodily injury" or "property damage" for which the insured is obligated to pay damages by '
        'reason of the assumption of liability in a contract or agreement.'
    )
    
    doc.add_paragraph(
        '3. Liquor Liability\n'
        '"Bodily injury" or "property damage" for which any insured may be held liable by reason of:\n'
        '(a) Causing or contributing to the intoxication of any person;\n'
        '(b) The furnishing of alcoholic beverages to a person under the legal drinking age or under the influence of alcohol; or\n'
        '(c) Any statute, ordinance or regulation relating to the sale, gift, distribution or use of alcoholic beverages.'
    )
    
    # Add definitions
    doc.add_heading('SECTION III - DEFINITIONS', 1)
    doc.add_paragraph(
        '1. "Bodily injury" means bodily injury, sickness or disease sustained by a person, including '
        'death resulting from any of these at any time.\n'
        '2. "Property damage" means:\n'
        '   a. Physical injury to tangible property, including all resulting loss of use of that property; or\n'
        '   b. Loss of use of tangible property that is not physically injured.'
    )
    
    doc.add_paragraph(
        '3. "Occurrence" means an accident, including continuous or repeated exposure to substantially '
        'the same general harmful conditions.\n'
        '4. "Coverage territory" means:\n'
        '   a. The United States of America (including its territories and possessions), Puerto Rico and Canada;\n'
        '   b. International waters or airspace, but only if the injury or damage occurs in the course of travel '
        'or transportation between any places included in a. above.'
    )
    
    # Add conditions
    doc.add_heading('SECTION IV - CONDITIONS', 1)
    doc.add_paragraph(
        '1. Bankruptcy\n'
        'Bankruptcy or insolvency of the insured or of the insured\'s estate will not relieve us of our '
        'obligations under this policy.\n'
        '2. Duties In The Event Of Occurrence, Offense, Claim Or Suit\n'
        'a. You must see to it that we are notified as soon as practicable of an "occurrence" or an offense '
        'which may result in a claim.'
    )
    
    # Add endorsement
    doc.add_heading('ENDORSEMENT - ADDITIONAL INSURED', 1)
    doc.add_paragraph(
        'This endorsement modifies insurance provided under the following:\n'
        'COMMERCIAL GENERAL LIABILITY COVERAGE PART\n\n'
        'SCHEDULE\n'
        'Name of Additional Insured Person(s) Or Organization(s):\n'
        'XYZ Partner Company\n\n'
        'Section II – Who Is An Insured is amended to include as an additional insured the person(s) or '
        'organization(s) shown in the Schedule.'
    )
    
    # Save the document to a temporary file
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, 'sample_policy.docx')
    doc.save(file_path)
    
    print(f"Created sample policy document at: {file_path}")
    return file_path

def display_element_examples(document_map, element_type, count=3):
    """
    Display examples of specific element types from the document map.
    
    Args:
        document_map: The processed document map
        element_type: Type of element to display
        count: Number of examples to show
    """
    elements = [e for e in document_map.get('elements', []) if e.get('type') == element_type]
    
    if not elements:
        print(f"No {element_type} elements found.")
        return
    
    print(f"\nExamples of {element_type} elements:")
    for i, element in enumerate(elements[:count]):
        print(f"  Example {i+1}:")
        print(f"    Text: {element.get('text', '')[:150]}...")
        print(f"    Subtype: {element.get('subtype', 'None')}")
        print(f"    Confidence: {element.get('confidence', 0.0)}")
        if element.get('keywords'):
            print(f"    Keywords: {', '.join(element.get('keywords', []))}")
        print()

def main():
    """Main function to demonstrate the Policy DNA Extractor."""
    print("Policy DNA Extractor Example")
    print("===========================")
    
    # Create a sample document
    print("\nStep 1: Creating a sample policy document...")
    document_path = create_test_document()
    
    # Initialize the extractor
    print("\nStep 2: Initializing the Policy DNA Extractor...")
    config = get_config()
    config.output_dir = os.path.join(os.getcwd(), 'output')
    config.debug_mode = True  # Enable debug mode for this demo
    extractor = PolicyDNAExtractor(config)
    
    # Process the document
    print("\nStep 3: Processing the document...")
    try:
        document_map = extractor.process_document(document_path)
        
        # Display processing summary
        print("\nProcessing Summary:")
        print(f"Document ID: {document_map['document_id']}")
        print(f"Sections found: {document_map['section_counts']['TOTAL']}")
        print(f"Elements extracted: {document_map['element_counts']['TOTAL']}")
        
        # Display section counts
        print("\nSection count by type:")
        for section_type, count in sorted(document_map['section_counts'].items()):
            if section_type != 'TOTAL':
                print(f"  - {section_type}: {count}")
        
        # Display element counts
        print("\nElement count by type:")
        for element_type, count in sorted(document_map['element_counts'].items()):
            if element_type != 'TOTAL':
                print(f"  - {element_type}: {count}")
        
        # Display examples of different element types
        display_element_examples(document_map, "COVERAGE_GRANT")
        display_element_examples(document_map, "EXCLUSION")
        display_element_examples(document_map, "DEFINITION")
        
        # Display any hierarchical relationships
        print("\nHierarchical Relationships:")
        relationship_count = 0
        for element in document_map.get('elements', []):
            if element.get('child_element_ids'):
                relationship_count += 1
                print(f"  Parent: {element.get('text', '')[:50]}...")
                print(f"  Children: {len(element.get('child_element_ids', []))}")
                print()
                
        if relationship_count == 0:
            print("  No hierarchical relationships detected.")
        
        # Display policy insights
        if 'policy_insights' in document_map:
            insights = document_map['policy_insights']
            
            # Display key definitions
            if insights.get('key_definitions'):
                print("\nKey Defined Terms:")
                for definition in insights.get('key_definitions', [])[:5]:
                    print(f"  - \"{definition.get('term', '')}\": {definition.get('definition', '')[:100]}...")
            
            # Display monetary provisions
            if insights.get('monetary_provisions'):
                print("\nMonetary Provisions:")
                for provision in insights.get('monetary_provisions', [])[:3]:
                    print(f"  - {provision.get('text', '')[:100]}...")
                    print(f"    Values: {', '.join(provision.get('monetary_values', []))}")
                
        print(f"\nOutput saved to: {config.output_dir}")
        print("\nProcessing completed successfully!")
    except Exception as e:
        print(f"\nError processing document: {str(e)}")
        
if __name__ == "__main__":
    main()