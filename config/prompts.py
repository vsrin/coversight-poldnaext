"""
LLM prompts for the Policy DNA Extractor.
"""

class Prompts:
    """Collection of prompts for the LLM."""
    
    @staticmethod
    def structure_analysis_prompt(document_text: str) -> str:
        """
        Generate a prompt for document structure analysis.
        
        Args:
            document_text: The document text to analyze
            
        Returns:
            A formatted prompt string
        """
        return f"""
        # Insurance Policy Document Structure Analysis
        
        ## Background Information
        Insurance policy documents follow specific structural patterns. They typically include:
        - Declarations pages with basic policy information (policy number, named insured, policy period)
        - Forms with numbered sections and subsections (insuring agreements, exclusions, conditions)
        - Endorsements that modify the base policy
        - Defined terms that may appear in bold, ALL CAPS, or quotes
        
        ## Your Task
        Analyze the provided insurance policy document text and identify its structural components.
        For each identified section:
        1. Determine its heading/title
        2. Identify its hierarchical level (1 = top level, 2 = subsection, etc.)
        3. Extract the full text content of the section
        4. Detect any formatting cues that indicate its purpose
        5. Note any cross-references to other sections
        
        ## Document Text
        ```
        {document_text}
        ```
        
        ## Expected Output Format
        Provide your analysis in JSON format following this structure:
        ```json
        {{
          "sections": [
            {{
              "id": "unique_id",
              "title": "Section title",
              "level": 1,
              "text": "Section text content",
              "parent_id": null,
              "formatting_cues": ["bullet_list", "numbering", etc.],
              "cross_references": ["Section X", "Endorsement Y"]
            }}
          ]
        }}
        ```
        
        ## Analysis Steps
        1. First, identify the major document components (declarations, forms, endorsements)
        2. For each component, identify sections and subsections
        3. Note formatting patterns that indicate section types
        4. Identify cross-references between sections
        5. Create the structured JSON output
        
        Return ONLY the JSON output with no additional text.
        """
    
    @staticmethod
    def section_classification_prompt(section_text: str, section_title: str) -> str:
        """
        Generate a prompt for section classification.
        
        Args:
            section_text: The text content of the section
            section_title: The title of the section
            
        Returns:
            A formatted prompt string
        """
        return f"""
        # Insurance Policy Section Classification
        
        ## Background Information
        Insurance policies contain several standard section types:
        - DECLARATIONS: Basic policy information (insured, limits, premium)
        - INSURING_AGREEMENT: The coverage grant (what is covered)
        - DEFINITIONS: Terms defined for the policy
        - EXCLUSIONS: What is not covered by the policy
        - CONDITIONS: Requirements that must be met for coverage
        - ENDORSEMENT: Modifications to the base policy
        - SCHEDULE: Lists of covered items, locations, etc.
        - OTHER: Any other section type
        
        ## Your Task
        Classify the provided insurance policy section into one of these categories.
        
        ## Section Information
        Title: {section_title}
        
        Content:
        ```
        {section_text[:1000]}
        ```
        
        ## Expected Output Format
        Provide your classification in JSON format:
        ```json
        {{
          "classification": "CATEGORY_NAME",
          "confidence": 0.95,
          "evidence": "Key phrases or patterns that support this classification"
        }}
        ```
        
        Return ONLY the JSON output with no additional text.
        """
    
    @staticmethod
    def element_extraction_prompt(section_text: str, section_type: str) -> str:
        """
        Generate a prompt for element extraction.
        
        Args:
            section_text: The text content of the section
            section_type: The classification of the section
            
        Returns:
            A formatted prompt string
        """
        return f"""
        # Insurance Policy Element Extraction
        
        ## Your Task
        Analyze the insurance policy section below and identify distinct policy elements. A policy element is a specific provision, clause, or statement that serves a distinct function within the policy.
        
        ## Types of Elements to Identify
        - Coverage grants (what is covered)
        - Exclusions (what is not covered)
        - Conditions (requirements for coverage)
        - Definitions (terms defined in the policy)
        - Sub-limits (specific monetary limits)
        - Retentions (deductibles or self-insured amounts)
        - Extensions (additional coverages)
        - Territory provisions (geographic scope)
        - Time elements (time limitations)
        - Reporting obligations (claim reporting requirements)
        
        ## Section Text:
        ```
        {section_text}
        ```
        
        ## Section Classification: {section_type}
        
        ## Expected Output Format
        Provide your analysis as a JSON array of elements, where each element follows this structure:
        ```json
        [
          {{
            "text": "Full text of the element",
            "type": "One of the element types listed above",
            "subtype": "More specific classification if applicable",
            "metadata": {{
              "has_monetary_value": true/false,
              "monetary_values": ["$1,000,000", etc.],
              "contains_reference": true/false,
              "references": ["Section IV", etc.],
              "contains_condition": true/false,
              "conditions": ["Written notice must be provided...", etc.]
            }}
          }}
        ]
        ```
        
        ## Guidelines
        - Extract each distinct element separately
        - Preserve the exact text of each element
        - If an element contains sub-elements, identify both the parent and child elements
        - Pay special attention to numbered or lettered provisions
        - Focus on the substance rather than formatting
        - Ensure the JSON is valid and properly formatted
        
        Return only the JSON array with no additional text.
        """
    
    @staticmethod
    def element_classification_prompt(element_text: str, initial_type: str, section_type: str) -> str:
        """
        Generate a prompt for element classification.
        
        Args:
            element_text: The text of the element
            initial_type: Initial classification of the element
            section_type: The type of section containing the element
            
        Returns:
            A formatted prompt string
        """
        return f"""
        # Insurance Policy Element Classification
        
        ## Your Task
        Analyze the insurance policy element below and classify it with high precision according to insurance industry standards.
        
        ## Element Text:
        ```
        {element_text}
        ```
        
        ## Initial Classification: {initial_type}
        ## Section Type: {section_type}
        
        ## Element Types
        - COVERAGE_GRANT: Provides coverage for specified losses or events
        - EXCLUSION: Explicitly removes something from coverage
        - CONDITION: Establishes requirements for coverage to apply
        - DEFINITION: Defines a term used in the policy
        - SUB_LIMIT: Specifies a limit within a broader coverage
        - RETENTION: Indicates a deductible or self-insured amount
        - EXTENSION: Extends or adds to the basic coverage
        - TERRITORY: Defines geographic scope of coverage
        - TIME_ELEMENT: Establishes time-based requirements or limitations
        - REPORTING_OBLIGATION: Requirements for reporting claims
        - OTHER: Any other element type
        
        ## Expected Output Format
        Provide your classification as a JSON object:
        ```json
        {{
          "type": "One of the element types listed above",
          "subtype": "More specific classification",
          "confidence": 0.95,
          "explanation": "Brief explanation of why this classification is appropriate",
          "keywords": ["term1", "term2"],
          "function": "Brief description of this element's function in the policy"
        }}
        ```
        
        ## Guidelines
        - Focus on the substantive function of the element, not just its format
        - Consider the context of the section type in your classification
        - Assign a confidence score (0.0 to 1.0) based on classification certainty
        - If uncertain between two types, choose the most specific applicable type
        - For definitions, identify the specific term being defined
        - For monetary provisions, note the specific values involved
        
        Return only the JSON object with no additional text.
        """
    
    @staticmethod
    def relationship_analysis_prompt(elements_json: str, section_type: str, section_title: str) -> str:
        """
        Generate a prompt for relationship analysis.
        
        Args:
            elements_json: JSON representation of elements
            section_type: The type of section
            section_title: The title of the section
            
        Returns:
            A formatted prompt string
        """
        return f"""
        # Insurance Policy Element Relationship Analysis
        
        ## Your Task
        Analyze the insurance policy elements below from the same section and identify hierarchical and referential relationships between them.
        
        ## Section Type: {section_type}
        ## Section Title: {section_title}
        
        ## Elements:
        {elements_json}
        
        ## Types of Relationships to Identify
        1. Parent-Child: One element contains or encompasses another
        2. Reference: One element refers to another
        3. Dependency: One element's application depends on another
        4. Modification: One element modifies or limits another
        
        ## Expected Output Format
        Provide your analysis as a JSON array of relationships:
        ```json
        [
          {{
            "relationship_type": "PARENT_CHILD",
            "parent_id": "element_id_of_parent",
            "child_id": "element_id_of_child",
            "explanation": "Why these elements have this relationship"
          }},
          {{
            "relationship_type": "REFERENCE",
            "source_id": "element_id_that_contains_reference",
            "target_id": "element_id_being_referenced",
            "explanation": "Nature of the reference"
          }},
          {{
            "relationship_type": "DEPENDENCY",
            "dependent_id": "element_id_that_depends",
            "dependency_id": "element_id_depended_upon",
            "explanation": "Nature of the dependency"
          }},
          {{
            "relationship_type": "MODIFICATION",
            "modifier_id": "element_id_that_modifies",
            "modified_id": "element_id_being_modified",
            "explanation": "How the modification works"
          }}
        ]
        ```
        
        ## Guidelines
        - Focus on substantive relationships, not just textual proximity
        - Identify nested structures (parent-child relationships)
        - Note when one element explicitly references another
        - Identify when elements contain conditions that affect other elements
        - If no clear relationships exist, return an empty array
        
        Return only the JSON array with no additional text.
        """
    
    # Add these methods to the Prompts class in config/prompts.py

    @staticmethod
    def intent_analysis_prompt(element_text: str, element_type: str, element_subtype: str) -> str:
        """
        Generate a prompt for intent analysis.
        
        Args:
            element_text: The text of the element
            element_type: The type of the element
            element_subtype: The subtype of the element
            
        Returns:
            A formatted prompt string
        """
        return f"""
        # Insurance Policy Intent Analysis
        
        ## Your Task
        Analyze the insurance policy element below and determine its precise coverage intent - what it means to cover or exclude, under what circumstances, and with what limitations.
        
        ## Element Information
        Text: ```
        {element_text}
        ```
        
        Type: {element_type}
        Subtype: {element_subtype}
        
        ## Expected Output Format
        Provide your analysis as a JSON object:
        ```json
        {{
          "intent_summary": "Brief plain language summary of what this element means",
          "coverage_effect": "GRANTS_COVERAGE/LIMITS_COVERAGE/EXCLUDES_COVERAGE/MODIFIES_COVERAGE/DEFINES_TERM/IMPOSES_OBLIGATION",
          "intent_details": {{
            "what_is_covered": "Specific subject of coverage (if applicable)",
            "trigger_events": ["Event 1", "Event 2"],
            "temporal_conditions": "Time-related conditions that apply",
            "spatial_conditions": "Location-related conditions that apply",
            "actor_obligations": "What any party must do for this to apply"
          }},
          "intent_confidence": 0.85
        }}
        ```
        
        ## Guidelines
        - Focus on what the element actually means in practical terms, not just its technical classification
        - Consider the impact on coverage in real-world situations
        - Identify what would trigger this element to apply
        - Note any conditions that must be met for this element to apply
        - If this is a coverage grant, specify what is being covered
        - If this is an exclusion, specify what is being excluded and under what circumstances
        - For definitions, explain how the definition impacts coverage interpretation
        
        Return only the JSON object with no additional text.
        """

    @staticmethod
    def conditional_analysis_prompt(element_text: str, element_type: str) -> str:
        """
        Generate a prompt for conditional language analysis.
        
        Args:
            element_text: The text of the element
            element_type: The type of the element
            
        Returns:
            A formatted prompt string
        """
        return f"""
        # Insurance Policy Conditional Language Analysis
        
        ## Your Task
        Analyze the insurance policy element below and identify all conditional language that modifies coverage, including requirements, limitations, and triggers.
        
        ## Element Information
        Text: ```
        {element_text}
        ```
        
        Type: {element_type}
        
        ## Expected Output Format
        Provide your analysis as a JSON object:
        ```json
        {{
          "conditions": [
            {{
              "condition_text": "Full text of the condition",
              "condition_type": "PREREQUISITE/LIMITATION/EXCLUSIONARY/REPORTING/TIMING/GEOGRAPHICAL",
              "effect": "How this condition modifies coverage",
              "applies_to": "What the condition applies to",
              "consequence": "What happens if condition is/isn't met"
            }}
          ],
          "has_complex_conditions": true/false,
          "condition_count": 2,
          "confidence": 0.95
        }}
        ```
        
        ## Condition Types
        - PREREQUISITE: Must be met for coverage to apply
        - LIMITATION: Restricts the scope of coverage
        - EXCLUSIONARY: Removes certain scenarios from coverage
        - REPORTING: Requirements for reporting claims or incidents
        - TIMING: Time-based conditions
        - GEOGRAPHICAL: Location-based conditions
        
        ## Guidelines
        - Extract the exact text of each condition
        - Determine how each condition affects coverage
        - Consider both explicit and implicit conditions
        - Identify requirements that must be satisfied
        - Note consequences of meeting or failing to meet conditions
        - Count and categorize all conditions found
        
        Return only the JSON object with no additional text.
        """

    @staticmethod
    def term_extraction_prompt(element_text: str, element_type: str) -> str:
        """
        Generate a prompt for term extraction.
        
        Args:
            element_text: The text of the element
            element_type: The type of the element
            
        Returns:
            A formatted prompt string
        """
        return f"""
        # Insurance Policy Term Extraction
        
        ## Your Task
        Analyze the insurance policy element below and extract specific terms, conditions, triggers, and other critical language components that affect the interpretation and application of coverage.
        
        ## Element Information
        Text: ```
        {element_text}
        ```
        
        Type: {element_type}
        
        ## Expected Output Format
        Provide your analysis as a JSON object:
        ```json
        {{
          "extracted_terms": [
            {{
              "term": "The specific term or phrase",
              "term_type": "DEFINED_TERM/TRIGGER/CONDITION/REQUIREMENT/LIMITATION/MONETARY_VALUE/TIME_PERIOD/LOCATION",
              "context": "How this term is used in the element",
              "significance": "How this term affects coverage or interpretation"
            }}
          ],
          "defined_terms": ["term1", "term2"],
          "temporal_terms": ["term1", "term2"],
          "monetary_terms": ["term1", "term2"],
          "logical_operators": ["and", "or", "not"],
          "confidence": 0.9
        }}
        ```
        
        ## Guidelines
        - Identify defined terms (typically in quotes or otherwise highlighted)
        - Extract triggers that activate or deactivate coverage
        - Note conditions that must be satisfied
        - Identify requirements imposed on parties
        - Extract monetary values and their context
        - Note time periods and deadlines
        - Identify locations or territories mentioned
        - Extract logical operators that affect interpretation
        
        Return only the JSON object with no additional text.
        """