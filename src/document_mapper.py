"""
Document mapper module for creating navigable document maps from classified sections.
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

class DocumentMapper:
    """Creates navigable document maps from classified sections."""
    
    def create_document_map(self, document_info: Dict, classified_sections: List[Dict]) -> Dict:
        """
        Create a structured document map from classified sections.
        
        Args:
            document_info: Original document information
            classified_sections: List of classified document sections
            
        Returns:
            A structured document map
        """
        # Generate a unique document ID
        document_id = str(uuid.uuid4())
        
        # Extract basic document metadata
        metadata = self._extract_metadata(document_info)
        
        # Create a hierarchical section tree
        section_tree = self._organize_sections(classified_sections)
        
        # Create navigation indices
        navigation = self._create_navigation(classified_sections)
        
        # Create the complete document map
        document_map = {
            'document_id': document_id,
            'created_at': datetime.now().isoformat(),
            'metadata': metadata,
            'sections': section_tree,
            'navigation': navigation,
            'section_counts': self._count_section_types(classified_sections)
        }
        
        return document_map
    
    def _extract_metadata(self, document_info: Dict) -> Dict:
        """
        Extract document metadata.
        
        Args:
            document_info: Document information
            
        Returns:
            Document metadata
        """
        metadata = {
            'file_path': document_info.get('file_path', ''),
            'file_type': document_info.get('file_type', ''),
            'total_pages': len(document_info.get('pages', [])),
            'extraction_date': datetime.now().isoformat()
        }
        
        # Add any document metadata from the original file
        if 'metadata' in document_info:
            metadata.update(document_info['metadata'])
            
        return metadata
    
    def _organize_sections(self, classified_sections: List[Dict]) -> List[Dict]:
        """
        Organize sections into a hierarchical structure.
        
        Args:
            classified_sections: List of classified sections
            
        Returns:
            Hierarchical section structure
        """
        # First pass: Create a mapping of section IDs to sections
        section_map = {}
        for section in classified_sections:
            section_id = section.get('id')
            if section_id:
                section_map[section_id] = section.copy()
                # Initialize children array
                section_map[section_id]['children'] = []
        
        # Second pass: Build parent-child relationships
        root_sections = []
        
        for section in classified_sections:
            section_id = section.get('id')
            parent_id = section.get('parent_id')
            
            if not section_id:
                continue
                
            if parent_id and parent_id in section_map:
                # Add this section as a child of its parent
                section_map[parent_id]['children'].append(section_map[section_id])
            elif not parent_id or parent_id not in section_map:
                # This is a root section
                root_sections.append(section_map[section_id])
        
        # Sort root sections by their level and position
        root_sections.sort(key=lambda s: (s.get('level', 999), s.get('id', '')))
        
        return root_sections
    
    def _create_navigation(self, classified_sections: List[Dict]) -> Dict:
        """
        Create navigation indices for the document.
        
        Args:
            classified_sections: List of classified sections
            
        Returns:
            Navigation indices
        """
        # Create type-based navigation
        nav_by_type = {}
        
        for section in classified_sections:
            classification = section.get('classification', {})
            section_type = classification.get('classification', 'OTHER')
            
            if section_type not in nav_by_type:
                nav_by_type[section_type] = []
                
            nav_by_type[section_type].append({
                'id': section.get('id', ''),
                'title': section.get('title', ''),
                'confidence': classification.get('confidence', 0.0)
            })
        
        # Create cross-reference navigation
        cross_refs = {}
        
        for section in classified_sections:
            section_id = section.get('id', '')
            refs = section.get('cross_references', [])
            
            if refs:
                cross_refs[section_id] = refs
        
        return {
            'by_type': nav_by_type,
            'cross_references': cross_refs
        }
    
    def _count_section_types(self, classified_sections: List[Dict]) -> Dict:
        """
        Count the number of sections by type.
        
        Args:
            classified_sections: List of classified sections
            
        Returns:
            Section counts by type
        """
        counts = {}
        
        for section in classified_sections:
            classification = section.get('classification', {})
            section_type = classification.get('classification', 'OTHER')
            
            if section_type not in counts:
                counts[section_type] = 0
                
            counts[section_type] += 1
            
        # Add total count
        counts['TOTAL'] = len(classified_sections)
        
        return counts