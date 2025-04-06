"""
Taxonomy Visualizer

This module provides functionality to generate visual representations of 
the mapped policy taxonomy structure.
"""

import json
import os
from typing import Dict, List, Optional, Set, Tuple, Any
from pathlib import Path


class TaxonomyVisualizer:
    """
    Creates visual representations of policy taxonomy mappings.
    """
    
    @staticmethod
    def generate_html_tree(policy_structure: Dict, output_file: str) -> None:
        """
        Generate an HTML visualization of the policy taxonomy tree.
        
        Args:
            policy_structure: Complete policy structure
            output_file: Path for the output HTML file
        """
        # Extract taxonomy mappings
        taxonomy_mappings = policy_structure.get("taxonomy_mappings", {})
        elements = policy_structure.get("elements", {})
        
        # Group elements by taxonomy code
        elements_by_code = {}
        for element_id, mapping in taxonomy_mappings.items():
            primary = mapping.get("primary_mapping", {})
            code = primary.get("code")
            confidence = primary.get("confidence", 0)
            
            if code and confidence >= 0.5:  # Only include reasonably confident mappings
                if code not in elements_by_code:
                    elements_by_code[code] = []
                
                if element_id in elements:
                    element = elements[element_id]
                    element_with_mapping = {
                        "id": element_id,
                        "title": element.get("title", "Untitled"),
                        "type": element.get("type", "unknown"),
                        "confidence": confidence
                    }
                    elements_by_code[code].append(element_with_mapping)
        
        # Create a hierarchical structure
        taxonomy_tree = _build_taxonomy_tree(elements_by_code)
        
        # Generate HTML
        html = _generate_tree_html(taxonomy_tree, policy_structure.get("metadata", {}))
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write(html)


    @staticmethod
    def generate_coverage_report(policy_structure: Dict, output_file: str) -> None:
        """
        Generate a coverage report showing taxonomy mappings.
        
        Args:
            policy_structure: Complete policy structure
            output_file: Path for the output HTML file
        """
        # Extract coverage summary
        coverage_summary = _extract_coverage_summary(policy_structure)
        
        # Generate HTML
        html = _generate_coverage_html(coverage_summary, policy_structure.get("metadata", {}))
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write(html)


    @staticmethod
    def generate_uniqueness_report(policy_structure: Dict, output_file: str) -> None:
        """
        Generate a report highlighting unique provisions.
        
        Args:
            policy_structure: Complete policy structure
            output_file: Path for the output HTML file
        """
        # Extract uniqueness data
        uniqueness_data = _extract_uniqueness_data(policy_structure)
        
        # Generate HTML
        html = _generate_uniqueness_html(uniqueness_data, policy_structure.get("metadata", {}))
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write(html)


    @staticmethod
    def generate_json_visualization(policy_structure: Dict, output_file: str) -> None:
        """
        Generate a JSON file suitable for visualization with external tools.
        
        Args:
            policy_structure: Complete policy structure
            output_file: Path for the output JSON file
        """
        # Create a visualization-friendly structure
        vis_data = {
            "metadata": policy_structure.get("metadata", {}),
            "taxonomy": _create_visualization_taxonomy(policy_structure),
            "elements": _create_visualization_elements(policy_structure),
            "relationships": _create_visualization_relationships(policy_structure)
        }
        
        # Write to file
        with open(output_file, 'w') as f:
            json.dump(vis_data, f, indent=2)


# Helper functions for visualization

def _build_taxonomy_tree(elements_by_code: Dict[str, List[Dict]]) -> Dict:
    """
    Build a hierarchical taxonomy tree from flat elements by code.
    
    Args:
        elements_by_code: Dictionary mapping taxonomy codes to elements
        
    Returns:
        Hierarchical tree structure
    """
    tree = {}
    
    for code, elements in elements_by_code.items():
        # Split the code by dots to get hierarchy
        parts = code.split('.')
        
        # Insert into tree
        current = tree
        for i, part in enumerate(parts):
            # Build the full code up to this part
            current_code = '.'.join(parts[:i+1])
            
            if part not in current:
                current[part] = {
                    'code': current_code,
                    'elements': [],
                    'children': {}
                }
            
            # If this is the full code, add the elements
            if current_code == code:
                current[part]['elements'] = elements
            
            # Move to next level of hierarchy
            current = current[part]['children']
    
    return tree


def _generate_tree_html(taxonomy_tree: Dict, metadata: Dict) -> str:
    """
    Generate HTML representation of the taxonomy tree.
    
    Args:
        taxonomy_tree: Hierarchical taxonomy tree
        metadata: Policy metadata
        
    Returns:
        HTML string
    """
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Policy Taxonomy Visualization</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1, h2, h3 {{
                color: #2c3e50;
            }}
            .metadata {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
            .taxonomy-tree {{
                margin-top: 30px;
            }}
            .tree-node {{
                margin-bottom: 10px;
            }}
            .node-header {{
                cursor: pointer;
                font-weight: bold;
                background-color: #e9ecef;
                padding: 8px 12px;
                border-radius: 4px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .node-header:hover {{
                background-color: #dee2e6;
            }}
            .node-content {{
                padding: 10px 20px;
                border-left: 2px solid #dee2e6;
                margin-left: 20px;
                display: none;
            }}
            .element-list {{
                list-style-type: none;
                padding-left: 0;
            }}
            .element-item {{
                background-color: #f1f3f5;
                margin: 5px 0;
                padding: 8px 12px;
                border-radius: 4px;
                display: flex;
                justify-content: space-between;
            }}
            .confidence {{
                background-color: #28a745;
                color: white;
                padding: 2px 6px;
                border-radius: 10px;
                font-size: 0.8em;
            }}
            .element-type {{
                color: #6c757d;
                font-style: italic;
                margin-left: 10px;
            }}
            .expanded {{
                display: block;
            }}
        </style>
    </head>
    <body>
        <h1>Policy Taxonomy Visualization</h1>
        
        <div class="metadata">
            <h2>Policy Information</h2>
            <p><strong>Policy Number:</strong> {metadata.get("policy_number", "N/A")}</p>
            <p><strong>Insured:</strong> {metadata.get("insured_name", "N/A")}</p>
            <p><strong>Policy Period:</strong> {metadata.get("effective_date", "N/A")} to {metadata.get("expiration_date", "N/A")}</p>
            <p><strong>Policy Type:</strong> {metadata.get("policy_type", "N/A")}</p>
        </div>
        
        <div class="taxonomy-tree">
            <h2>Taxonomy Structure</h2>
            {_render_tree_node(taxonomy_tree)}
        </div>
        
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                const headers = document.querySelectorAll('.node-header');
                headers.forEach(header => {{
                    header.addEventListener('click', function() {{
                        const content = this.nextElementSibling;
                        content.classList.toggle('expanded');
                    }});
                }});
            }});
        </script>
    </body>
    </html>
    """
    
    return html


def _render_tree_node(tree: Dict, level: int = 0) -> str:
    """
    Recursively render HTML for tree nodes.
    
    Args:
        tree: Tree node to render
        level: Current nesting level
        
    Returns:
        HTML string for this node and its children
    """
    html = ""
    
    for key, node in tree.items():
        code = node.get('code', key)
        elements = node.get('elements', [])
        children = node.get('children', {})
        
        element_count = len(elements)
        child_count = len(children)
        
        html += f"""
        <div class="tree-node">
            <div class="node-header">
                <span>{code} ({key})</span>
                <span>{element_count} elements, {child_count} subcategories</span>
            </div>
            <div class="node-content">
                <div class="elements">
                    <h4>Elements ({element_count})</h4>
                    <ul class="element-list">
        """
        
        # Add elements
        for element in elements:
            confidence = element.get('confidence', 0) * 100
            confidence_class = "high" if confidence >= 80 else "medium" if confidence >= 60 else "low"
            
            html += f"""
                        <li class="element-item">
                            <span>{element.get('title', 'Untitled')}<span class="element-type">{element.get('type', '')}</span></span>
                            <span class="confidence confidence-{confidence_class}">{confidence:.0f}%</span>
                        </li>
            """
        
        html += """
                    </ul>
                </div>
        """
        
        # Add children
        if children:
            html += f"""
                <div class="children">
                    <h4>Subcategories</h4>
                    {_render_tree_node(children, level + 1)}
                </div>
            """
        
        html += """
            </div>
        </div>
        """
    
    return html


def _extract_coverage_summary(policy_structure: Dict) -> Dict:
    """
    Extract coverage summary from policy structure.
    
    Args:
        policy_structure: Complete policy structure
        
    Returns:
        Coverage summary data
    """
    # This function would typically call into the PolicyStructureBuilder's
    # get_coverage_summary method or extract the data directly
    
    elements = policy_structure.get("elements", {})
    taxonomy_mappings = policy_structure.get("taxonomy_mappings", {})
    normalized_language = policy_structure.get("normalized_language", {})
    
    coverage_elements = []
    
    for element_id, element in elements.items():
        if element.get("type") == "coverage_grant":
            # Get mapping info
            mapping = taxonomy_mappings.get(element_id, {})
            primary_mapping = mapping.get("primary_mapping", {})
            code = primary_mapping.get("code")
            confidence = primary_mapping.get("confidence", 0)
            
            # Get normalization info
            norm = normalized_language.get(element_id, {})
            
            # Create coverage item
            coverage = {
                "id": element_id,
                "title": element.get("title", "Untitled Coverage"),
                "text": norm.get("normalized_text") or element.get("text", ""),
                "taxonomy_code": code,
                "confidence": confidence,
                "is_unique": norm.get("uniqueness_analysis", {}).get("is_unique", False)
            }
            
            coverage_elements.append(coverage)
    
    # Group by taxonomy code
    by_taxonomy = {}
    for coverage in coverage_elements:
        code = coverage.get("taxonomy_code") or "uncategorized"
        if code not in by_taxonomy:
            by_taxonomy[code] = []
        
        by_taxonomy[code].append(coverage)
    
    return {
        "coverages": coverage_elements,
        "by_taxonomy": by_taxonomy
    }


def _generate_coverage_html(coverage_summary: Dict, metadata: Dict) -> str:
    """
    Generate HTML for coverage report.
    
    Args:
        coverage_summary: Coverage summary data
        metadata: Policy metadata
        
    Returns:
        HTML string
    """
    coverages = coverage_summary.get("coverages", [])
    by_taxonomy = coverage_summary.get("by_taxonomy", {})
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Policy Coverage Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1, h2, h3 {{
                color: #2c3e50;
            }}
            .metadata {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
            .coverage-section {{
                margin-top: 20px;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                overflow: hidden;
            }}
            .section-header {{
                background-color: #e9ecef;
                padding: 12px 15px;
                font-weight: bold;
                border-bottom: 1px solid #dee2e6;
            }}
            .coverage-list {{
                list-style-type: none;
                padding: 0;
                margin: 0;
            }}
            .coverage-item {{
                padding: 15px;
                border-bottom: 1px solid #dee2e6;
            }}
            .coverage-item:last-child {{
                border-bottom: none;
            }}
            .coverage-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }}
            .coverage-title {{
                font-weight: bold;
                font-size: 1.1em;
            }}
            .coverage-text {{
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 4px;
                font-family: monospace;
                white-space: pre-wrap;
            }}
            .confidence {{
                background-color: #28a745;
                color: white;
                padding: 2px 6px;
                border-radius: 10px;
                font-size: 0.8em;
            }}
            .coverage-unique {{
                background-color: #fd7e14;
                color: white;
                padding: 2px 6px;
                border-radius: 10px;
                font-size: 0.8em;
                margin-left: 5px;
            }}
        </style>
    </head>
    <body>
        <h1>Policy Coverage Report</h1>
        
        <div class="metadata">
            <h2>Policy Information</h2>
            <p><strong>Policy Number:</strong> {metadata.get("policy_number", "N/A")}</p>
            <p><strong>Insured:</strong> {metadata.get("insured_name", "N/A")}</p>
            <p><strong>Policy Period:</strong> {metadata.get("effective_date", "N/A")} to {metadata.get("expiration_date", "N/A")}</p>
            <p><strong>Policy Type:</strong> {metadata.get("policy_type", "N/A")}</p>
            <p><strong>Total Coverage Elements:</strong> {len(coverages)}</p>
        </div>
        
        <h2>Coverage by Taxonomy</h2>
    """
    
    # Add sections for each taxonomy code
    for code, items in by_taxonomy.items():
        html += f"""
        <div class="coverage-section">
            <div class="section-header">
                {code} ({len(items)} items)
            </div>
            <ul class="coverage-list">
        """
        
        for coverage in items:
            confidence = coverage.get('confidence', 0) * 100
            is_unique = coverage.get('is_unique', False)
            
            html += f"""
                <li class="coverage-item">
                    <div class="coverage-header">
                        <span class="coverage-title">{coverage.get('title', 'Untitled Coverage')}</span>
                        <span>
                            <span class="confidence">{confidence:.0f}% confidence</span>
                            {('<span class="coverage-unique">Unique</span>' if is_unique else '')}
                        </span>
                    </div>
                    <div class="coverage-text">{coverage.get('text', '')}</div>
                </li>
            """
        
        html += """
            </ul>
        </div>
        """
    
    html += """
    </body>
    </html>
    """
    
    return html


def _extract_uniqueness_data(policy_structure: Dict) -> Dict:
    """
    Extract data about unique provisions from policy structure.
    
    Args:
        policy_structure: Complete policy structure
        
    Returns:
        Uniqueness data
    """
    elements = policy_structure.get("elements", {})
    normalized_language = policy_structure.get("normalized_language", {})
    
    unique_elements = []
    standardized_elements = []
    
    for element_id, norm in normalized_language.items():
        uniqueness_analysis = norm.get("uniqueness_analysis", {})
        is_unique = uniqueness_analysis.get("is_unique", False)
        
        if element_id in elements:
            element = elements[element_id]
            item = {
                "id": element_id,
                "title": element.get("title", "Untitled"),
                "type": element.get("type", "unknown"),
                "text": element.get("text", ""),
                "normalized_text": norm.get("normalized_text", ""),
                "uniqueness_score": uniqueness_analysis.get("uniqueness_score", 0),
                "unique_phrases": uniqueness_analysis.get("unique_phrases", [])
            }
            
            if is_unique:
                unique_elements.append(item)
            else:
                standardized_elements.append(item)
    
    return {
        "unique_elements": unique_elements,
        "standardized_elements": standardized_elements,
        "unique_count": len(unique_elements),
        "standardized_count": len(standardized_elements)
    }


def _generate_uniqueness_html(uniqueness_data: Dict, metadata: Dict) -> str:
    """
    Generate HTML for uniqueness report.
    
    Args:
        uniqueness_data: Uniqueness data
        metadata: Policy metadata
        
    Returns:
        HTML string
    """
    unique_elements = uniqueness_data.get("unique_elements", [])
    unique_count = uniqueness_data.get("unique_count", 0)
    standardized_count = uniqueness_data.get("standardized_count", 0)
    total_count = unique_count + standardized_count
    
    unique_percentage = (unique_count / total_count * 100) if total_count > 0 else 0
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Policy Uniqueness Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1, h2, h3 {{
                color: #2c3e50;
            }}
            .metadata {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
            .summary {{
                background-color: #e9ecef;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
                display: flex;
                justify-content: space-around;
            }}
            .stat-box {{
                text-align: center;
            }}
            .stat-value {{
                font-size: 2em;
                font-weight: bold;
                color: #2c3e50;
            }}
            .stat-label {{
                font-size: 0.9em;
                color: #6c757d;
            }}
            .element-list {{
                list-style-type: none;
                padding: 0;
            }}
            .element-item {{
                margin-bottom: 20px;
                padding: 15px;
                border: 1px solid #dee2e6;
                border-radius: 5px;
            }}
            .element-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }}
            .element-title {{
                font-weight: bold;
                font-size: 1.1em;
            }}
            .element-type {{
                color: #6c757d;
                font-style: italic;
            }}
            .uniqueness-score {{
                background-color: #fd7e14;
                color: white;
                padding: 2px 6px;
                border-radius: 10px;
                font-size: 0.8em;
            }}
            .text-comparison {{
                display: flex;
                gap: 20px;
            }}
            .text-box {{
                flex: 1;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 4px;
                font-family: monospace;
                white-space: pre-wrap;
            }}
            .original-text {{
                border-left: 4px solid #fd7e14;
            }}
            .normalized-text {{
                border-left: 4px solid #0d6efd;
            }}
            .unique-phrases {{
                margin-top: 10px;
            }}
            .phrase {{
                background-color: #fff3cd;
                padding: 8px;
                margin: 5px 0;
                border-radius: 4px;
                border-left: 4px solid #ffc107;
            }}
        </style>
    </head>
    <body>
        <h1>Policy Uniqueness Report</h1>
        
        <div class="metadata">
            <h2>Policy Information</h2>
            <p><strong>Policy Number:</strong> {metadata.get("policy_number", "N/A")}</p>
            <p><strong>Insured:</strong> {metadata.get("insured_name", "N/A")}</p>
            <p><strong>Policy Period:</strong> {metadata.get("effective_date", "N/A")} to {metadata.get("expiration_date", "N/A")}</p>
            <p><strong>Policy Type:</strong> {metadata.get("policy_type", "N/A")}</p>
        </div>
        
        <div class="summary">
            <div class="stat-box">
                <div class="stat-value">{unique_count}</div>
                <div class="stat-label">Unique Elements</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{standardized_count}</div>
                <div class="stat-label">Standard Elements</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{unique_percentage:.1f}%</div>
                <div class="stat-label">Uniqueness Percentage</div>
            </div>
        </div>
        
        <h2>Unique Provisions</h2>
        <p>These provisions contain unique language that differs significantly from standard clauses.</p>
        
        <ul class="element-list">
    """
    
    # Sort unique elements by uniqueness score
    sorted_elements = sorted(unique_elements, key=lambda x: x.get("uniqueness_score", 0), reverse=True)
    
    for element in sorted_elements:
        uniqueness_score = element.get("uniqueness_score", 0) * 100
        unique_phrases = element.get("unique_phrases", [])
        
        html += f"""
            <li class="element-item">
                <div class="element-header">
                    <span class="element-title">{element.get("title", "Untitled")}</span>
                    <span>
                        <span class="element-type">{element.get("type", "unknown")}</span>
                        <span class="uniqueness-score">{uniqueness_score:.0f}% unique</span>
                    </span>
                </div>
                
                <div class="text-comparison">
                    <div class="text-box original-text">
                        <h4>Original Text:</h4>
                        {element.get("text", "")}
                    </div>
                    <div class="text-box normalized-text">
                        <h4>Normalized Text:</h4>
                        {element.get("normalized_text", "")}
                    </div>
                </div>
        """
        
        if unique_phrases:
            html += """
                <div class="unique-phrases">
                    <h4>Unique Phrases:</h4>
            """
            
            for phrase in unique_phrases:
                html += f"""
                    <div class="phrase">{phrase}</div>
                """
            
            html += """
                </div>
            """
        
        html += """
            </li>
        """
    
    html += """
        </ul>
    </body>
    </html>
    """
    
    return html


def _create_visualization_taxonomy(policy_structure: Dict) -> Dict:
    """
    Create taxonomy data for visualization tools.
    
    Args:
        policy_structure: Complete policy structure
        
    Returns:
        Visualization-friendly taxonomy data
    """
    # This would typically extract taxonomy information from taxonomy_mappings
    # For external visualization tools like D3.js
    
    mappings = policy_structure.get("taxonomy_mappings", {})
    
    # Count elements per taxonomy code
    code_counts = {}
    for mapping in mappings.values():
        primary = mapping.get("primary_mapping", {})
        code = primary.get("code")
        
        if code:
            code_counts[code] = code_counts.get(code, 0) + 1
    
    # Create nodes and links
    nodes = []
    links = []
    
    # Build hierarchy
    hierarchy = {}
    for code in code_counts.keys():
        parts = code.split('.')
        
        # Add each level to hierarchy
        current_path = ""
        for i, part in enumerate(parts):
            parent_path = current_path
            current_path = (parent_path + "." + part) if parent_path else part
            
            if current_path not in hierarchy:
                hierarchy[current_path] = {
                    "id": current_path,
                    "name": part,
                    "count": code_counts.get(current_path, 0),
                    "parent": parent_path if parent_path else None
                }
    
    # Convert hierarchy to nodes and links
    for code, node_data in hierarchy.items():
        nodes.append({
            "id": node_data["id"],
            "name": node_data["name"],
            "count": node_data["count"]
        })
        
        if node_data["parent"]:
            links.append({
                "source": node_data["parent"],
                "target": node_data["id"],
                "value": 1
            })
    
    return {
        "nodes": nodes,
        "links": links
    }


def _create_visualization_elements(policy_structure: Dict) -> List[Dict]:
    """
    Create element data for visualization tools.
    
    Args:
        policy_structure: Complete policy structure
        
    Returns:
        Visualization-friendly element data
    """
    elements = policy_structure.get("elements", {})
    mappings = policy_structure.get("taxonomy_mappings", {})
    normalized = policy_structure.get("normalized_language", {})
    
    vis_elements = []
    
    for element_id, element in elements.items():
        # Get mapping info
        mapping = mappings.get(element_id, {})
        primary = mapping.get("primary_mapping", {})
        
        # Get normalization info
        norm = normalized.get(element_id, {})
        
        vis_elements.append({
            "id": element_id,
            "title": element.get("title", "Untitled"),
            "type": element.get("type", "unknown"),
            "taxonomy_code": primary.get("code"),
            "confidence": primary.get("confidence", 0),
            "is_unique": norm.get("uniqueness_analysis", {}).get("is_unique", False),
            "uniqueness_score": norm.get("uniqueness_analysis", {}).get("uniqueness_score", 0)
        })
    
    return vis_elements


def _create_visualization_relationships(policy_structure: Dict) -> List[Dict]:
    """
    Create relationship data for visualization tools.
    
    Args:
        policy_structure: Complete policy structure
        
    Returns:
        Visualization-friendly relationship data
    """
    relationships = policy_structure.get("relationships", {})
    
    vis_relationships = []
    
    for source_id, rel_list in relationships.items():
        for rel in rel_list:
            target_id = rel.get("target_id")
            if target_id:
                vis_relationships.append({
                    "source": source_id,
                    "target": target_id,
                    "type": rel.get("type", "unknown"),
                    "description": rel.get("description", "")
                })
    
    return vis_relationships


# Example usage
if __name__ == "__main__":
    # Load policy structure
    try:
        with open("policy_structure.json", 'r') as f:
            policy_structure = json.load(f)
    except FileNotFoundError:
        print("Policy structure file not found. Creating a sample structure.")
        
        # Create a sample structure for demonstration
        from policy_structure_builder import PolicyStructureBuilder
        
        builder = PolicyStructureBuilder()
        builder.set_policy_metadata({
            "policy_number": "CGL12345678",
            "insured_name": "ACME Corporation",
            "effective_date": "2023-01-01",
            "expiration_date": "2024-01-01",
            "policy_type": "Commercial General Liability"
        })
        
        # Add other data...
        
        policy_structure = builder.build_structure()
    
    # Create output directory
    os.makedirs("visualizations", exist_ok=True)
    
    # Generate visualizations
    visualizer = TaxonomyVisualizer()
    visualizer.generate_html_tree(policy_structure, "visualizations/taxonomy_tree.html")
    visualizer.generate_coverage_report(policy_structure, "visualizations/coverage_report.html")
    visualizer.generate_uniqueness_report(policy_structure, "visualizations/uniqueness_report.html")
    visualizer.generate_json_visualization(policy_structure, "visualizations/visualization_data.json")
    
    print("Visualizations generated in the 'visualizations' directory.")