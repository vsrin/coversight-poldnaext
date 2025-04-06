"""
Detailed Taxonomy Extensions for Insurance Policies

This module provides more detailed extensions to the base taxonomy framework,
adding comprehensive coverage details based on standard industry classifications.
"""

from src.taxonomy.taxonomy_framework import TaxonomyManager, TaxonomyNode, TaxonomyLevel

def extend_property_taxonomy(taxonomy: TaxonomyManager):
    """
    Extend the Property Insurance taxonomy branch with detailed subcategories.
    
    Args:
        taxonomy: The taxonomy manager to extend
    """
    # Property Building Coverage - Details
    taxonomy.add_node(TaxonomyNode(
        code="PROP.BLDG.DEBRISREM",
        name="Debris Removal",
        level=TaxonomyLevel.COVERAGE_DETAIL,
        description="Coverage for costs to remove debris after a covered loss",
        source="ISO",
        parent_code="PROP.BLDG"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="PROP.BLDG.ORDLAW",
        name="Ordinance or Law",
        level=TaxonomyLevel.COVERAGE_DETAIL,
        description="Coverage for increased costs due to building code compliance",
        source="ISO",
        parent_code="PROP.BLDG"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="PROP.BLDG.POLLCLEAN",
        name="Pollutant Cleanup",
        level=TaxonomyLevel.COVERAGE_DETAIL,
        description="Coverage for costs to clean up pollutants from land or water",
        source="ISO",
        parent_code="PROP.BLDG"
    ))
    
    # Business Personal Property - Details
    taxonomy.add_node(TaxonomyNode(
        code="PROP.BPP.STOCK",
        name="Stock",
        level=TaxonomyLevel.COVERAGE_DETAIL,
        description="Coverage for merchandise held for sale",
        source="ISO",
        parent_code="PROP.BPP"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="PROP.BPP.FF&E",
        name="Furniture, Fixtures & Equipment",
        level=TaxonomyLevel.COVERAGE_DETAIL,
        description="Coverage for business furniture, fixtures, and equipment",
        source="ISO",
        parent_code="PROP.BPP"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="PROP.BPP.TENIMPR",
        name="Tenant Improvements",
        level=TaxonomyLevel.COVERAGE_DETAIL,
        description="Coverage for improvements made by tenant to rented space",
        source="ISO",
        parent_code="PROP.BPP"
    ))
    
    # Business Interruption - Details
    taxonomy.add_node(TaxonomyNode(
        code="PROP.BI.EARNINGS",
        name="Business Income",
        level=TaxonomyLevel.COVERAGE_DETAIL,
        description="Coverage for lost net income and continuing expenses",
        source="ISO",
        parent_code="PROP.BI"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="PROP.BI.EXEXP",
        name="Extra Expense",
        level=TaxonomyLevel.COVERAGE_DETAIL,
        description="Coverage for additional costs to continue operations",
        source="ISO",
        parent_code="PROP.BI"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="PROP.BI.CIV",
        name="Civil Authority",
        level=TaxonomyLevel.COVERAGE_DETAIL,
        description="Coverage when access is prohibited by civil authority",
        source="ISO",
        parent_code="PROP.BI"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="PROP.BI.CONTCONT",
        name="Contingent Business Interruption",
        level=TaxonomyLevel.COVERAGE_DETAIL,
        description="Coverage for losses from damage to suppliers or customers",
        source="ISO",
        parent_code="PROP.BI"
    ))
    
    # Property Valuation Methods - Attributes
    taxonomy.add_node(TaxonomyNode(
        code="PROP.ATTR.VALACV",
        name="Actual Cash Value",
        level=TaxonomyLevel.COVERAGE_ATTRIBUTE,
        description="Valuation method: replacement cost minus depreciation",
        source="ISO",
        parent_code="PROP"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="PROP.ATTR.VALRC",
        name="Replacement Cost",
        level=TaxonomyLevel.COVERAGE_ATTRIBUTE,
        description="Valuation method: cost to replace with like kind and quality",
        source="ISO",
        parent_code="PROP"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="PROP.ATTR.VALFV",
        name="Functional Value",
        level=TaxonomyLevel.COVERAGE_ATTRIBUTE,
        description="Valuation method: cost to replace with functional equivalent",
        source="ISO",
        parent_code="PROP"
    ))
    
    # Property Causes of Loss - Attributes
    taxonomy.add_node(TaxonomyNode(
        code="PROP.ATTR.BASIC",
        name="Basic Form Perils",
        level=TaxonomyLevel.COVERAGE_ATTRIBUTE,
        description="Limited named perils coverage",
        source="ISO",
        parent_code="PROP"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="PROP.ATTR.BROAD",
        name="Broad Form Perils",
        level=TaxonomyLevel.COVERAGE_ATTRIBUTE,
        description="Extended named perils coverage",
        source="ISO",
        parent_code="PROP"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="PROP.ATTR.SPECIAL",
        name="Special Form Perils",
        level=TaxonomyLevel.COVERAGE_ATTRIBUTE,
        description="All-risk coverage with specified exclusions",
        source="ISO",
        parent_code="PROP"
    ))


def extend_liability_taxonomy(taxonomy: TaxonomyManager):
    """
    Extend the Liability Insurance taxonomy branch with detailed subcategories.
    
    Args:
        taxonomy: The taxonomy manager to extend
    """
    # General Liability - Coverage Types
    taxonomy.add_node(TaxonomyNode(
        code="LIAB.GL.PREMOP",
        name="Premises and Operations",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Liability for incidents on premises or from operations",
        source="ISO",
        parent_code="LIAB.GL"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="LIAB.GL.PRODCOMP",
        name="Products and Completed Operations",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Liability for products and completed work",
        source="ISO",
        parent_code="LIAB.GL"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="LIAB.GL.PIADVINJURY",
        name="Personal and Advertising Injury",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Liability for offenses like defamation and invasion of privacy",
        source="ISO",
        parent_code="LIAB.GL"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="LIAB.GL.MEDPAY",
        name="Medical Payments",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Medical expenses regardless of fault",
        source="ISO",
        parent_code="LIAB.GL"
    ))
    
    # General Liability - Coverage Details
    taxonomy.add_node(TaxonomyNode(
        code="LIAB.GL.PREMOP.BODINJURY",
        name="Bodily Injury",
        level=TaxonomyLevel.COVERAGE_DETAIL,
        description="Coverage for physical injury to others",
        source="ISO",
        parent_code="LIAB.GL.PREMOP"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="LIAB.GL.PREMOP.PROPDMG",
        name="Property Damage",
        level=TaxonomyLevel.COVERAGE_DETAIL,
        description="Coverage for damage to others' property",
        source="ISO",
        parent_code="LIAB.GL.PREMOP"
    ))
    
    # Products Liability - Coverage Types
    taxonomy.add_node(TaxonomyNode(
        code="LIAB.PROD.MFGDEFECT",
        name="Manufacturing Defect",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Liability for defects in manufacturing",
        source="ISO",
        parent_code="LIAB.PROD"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="LIAB.PROD.DESIGN",
        name="Design Defect",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Liability for defects in product design",
        source="ISO",
        parent_code="LIAB.PROD"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="LIAB.PROD.WARNING",
        name="Failure to Warn",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Liability for inadequate warnings or instructions",
        source="ISO",
        parent_code="LIAB.PROD"
    ))
    
    # Liability Attributes
    taxonomy.add_node(TaxonomyNode(
        code="LIAB.ATTR.OCCURRENCE",
        name="Occurrence Trigger",
        level=TaxonomyLevel.COVERAGE_ATTRIBUTE,
        description="Coverage triggered by incidents during policy period",
        source="ISO",
        parent_code="LIAB"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="LIAB.ATTR.CLAIMSMADE",
        name="Claims-Made Trigger",
        level=TaxonomyLevel.COVERAGE_ATTRIBUTE,
        description="Coverage triggered by claims made during policy period",
        source="ISO",
        parent_code="LIAB"
    ))


def extend_cyber_taxonomy(taxonomy: TaxonomyManager):
    """
    Extend the Cyber Insurance taxonomy branch with detailed subcategories.
    
    Args:
        taxonomy: The taxonomy manager to extend
    """
    # Data Breach Coverage - Types
    taxonomy.add_node(TaxonomyNode(
        code="CYBER.BREACH.NOTIFICATION",
        name="Breach Notification",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Costs to notify affected individuals",
        source="NAIC",
        parent_code="CYBER.BREACH"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="CYBER.BREACH.CREDITMON",
        name="Credit Monitoring",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Costs for credit monitoring services",
        source="NAIC",
        parent_code="CYBER.BREACH"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="CYBER.BREACH.FORENSIC",
        name="Forensic Investigation",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Costs for forensic analysis after breach",
        source="NAIC",
        parent_code="CYBER.BREACH"
    ))
    
    # Cyber Liability - Types
    taxonomy.add_node(TaxonomyNode(
        code="CYBER.LIAB.PRIVACY",
        name="Privacy Liability",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Liability for privacy breaches",
        source="NAIC",
        parent_code="CYBER.LIAB"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="CYBER.LIAB.NETWORK",
        name="Network Security Liability",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Liability for failures in network security",
        source="NAIC",
        parent_code="CYBER.LIAB"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="CYBER.LIAB.MEDIA",
        name="Media Liability",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Liability for digital content",
        source="NAIC",
        parent_code="CYBER.LIAB"
    ))
    
    # Additional Cyber coverages
    taxonomy.add_node(TaxonomyNode(
        code="CYBER.BUSINT",
        name="Cyber Business Interruption",
        level=TaxonomyLevel.COVERAGE_CATEGORY,
        description="Coverage for business interruption from cyber events",
        source="NAIC",
        parent_code="CYBER"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="CYBER.EXTORTION",
        name="Cyber Extortion",
        level=TaxonomyLevel.COVERAGE_CATEGORY,
        description="Coverage for ransomware and extortion demands",
        source="NAIC",
        parent_code="CYBER"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="CYBER.DATAREC",
        name="Data Recovery",
        level=TaxonomyLevel.COVERAGE_CATEGORY,
        description="Coverage for data restoration costs",
        source="NAIC",
        parent_code="CYBER"
    ))


def extend_auto_taxonomy(taxonomy: TaxonomyManager):
    """
    Extend the Auto Insurance taxonomy branch with detailed subcategories.
    
    Args:
        taxonomy: The taxonomy manager to extend
    """
    # Auto - Coverage Categories
    taxonomy.add_node(TaxonomyNode(
        code="AUTO.LIAB",
        name="Auto Liability",
        level=TaxonomyLevel.COVERAGE_CATEGORY,
        description="Liability coverage for auto incidents",
        source="ISO",
        parent_code="AUTO"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="AUTO.PHYS",
        name="Physical Damage",
        level=TaxonomyLevel.COVERAGE_CATEGORY,
        description="Coverage for damage to covered vehicles",
        source="ISO",
        parent_code="AUTO"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="AUTO.MEDPAY",
        name="Medical Payments",
        level=TaxonomyLevel.COVERAGE_CATEGORY,
        description="Medical coverage for vehicle occupants",
        source="ISO",
        parent_code="AUTO"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="AUTO.UM",
        name="Uninsured/Underinsured Motorist",
        level=TaxonomyLevel.COVERAGE_CATEGORY,
        description="Coverage for accidents with uninsured drivers",
        source="ISO",
        parent_code="AUTO"
    ))
    
    # Auto Liability - Types
    taxonomy.add_node(TaxonomyNode(
        code="AUTO.LIAB.BI",
        name="Bodily Injury Liability",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Liability for injuries to others",
        source="ISO",
        parent_code="AUTO.LIAB"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="AUTO.LIAB.PD",
        name="Property Damage Liability",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Liability for damage to others' property",
        source="ISO",
        parent_code="AUTO.LIAB"
    ))
    
    # Physical Damage - Types
    taxonomy.add_node(TaxonomyNode(
        code="AUTO.PHYS.COMP",
        name="Comprehensive",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Coverage for damage not from collision",
        source="ISO",
        parent_code="AUTO.PHYS"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="AUTO.PHYS.COLL",
        name="Collision",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Coverage for collision damage",
        source="ISO",
        parent_code="AUTO.PHYS"
    ))


def extend_professional_liability_taxonomy(taxonomy: TaxonomyManager):
    """
    Extend the Professional Liability taxonomy branch with detailed subcategories.
    
    Args:
        taxonomy: The taxonomy manager to extend
    """
    # Professional Liability - Categories
    taxonomy.add_node(TaxonomyNode(
        code="PROF.E&O",
        name="Errors & Omissions",
        level=TaxonomyLevel.COVERAGE_CATEGORY,
        description="Coverage for errors and omissions in professional services",
        source="ISO",
        parent_code="PROF"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="PROF.MPL",
        name="Medical Professional Liability",
        level=TaxonomyLevel.COVERAGE_CATEGORY,
        description="Coverage for medical professionals",
        source="ISO",
        parent_code="PROF"
    ))
    
    # E&O by Profession
    taxonomy.add_node(TaxonomyNode(
        code="PROF.E&O.LEGAL",
        name="Legal Professional Liability",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Coverage for legal professionals",
        source="ISO",
        parent_code="PROF.E&O"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="PROF.E&O.TECH",
        name="Technology E&O",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Coverage for technology service providers",
        source="ISO",
        parent_code="PROF.E&O"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="PROF.E&O.FIN",
        name="Financial Professional Liability",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Coverage for financial professionals",
        source="ISO",
        parent_code="PROF.E&O"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="PROF.E&O.REALEST",
        name="Real Estate Professional Liability",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Coverage for real estate professionals",
        source="ISO",
        parent_code="PROF.E&O"
    ))
    
    # Medical Professional Liability - Types
    taxonomy.add_node(TaxonomyNode(
        code="PROF.MPL.PHYS",
        name="Physicians Professional Liability",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Coverage for physicians",
        source="ISO",
        parent_code="PROF.MPL"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="PROF.MPL.HOSP",
        name="Hospital Professional Liability",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Coverage for hospitals",
        source="ISO",
        parent_code="PROF.MPL"
    ))


def extend_workers_comp_taxonomy(taxonomy: TaxonomyManager):
    """
    Extend the Workers Compensation taxonomy branch with detailed subcategories.
    
    Args:
        taxonomy: The taxonomy manager to extend
    """
    # Workers Comp - Categories
    taxonomy.add_node(TaxonomyNode(
        code="WC.STATUTORY",
        name="Statutory Coverage",
        level=TaxonomyLevel.COVERAGE_CATEGORY,
        description="Required workers comp benefits by law",
        source="NAIC",
        parent_code="WC"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="WC.EL",
        name="Employers Liability",
        level=TaxonomyLevel.COVERAGE_CATEGORY,
        description="Coverage for employee lawsuits",
        source="NAIC",
        parent_code="WC"
    ))
    
    # Statutory Benefits - Types
    taxonomy.add_node(TaxonomyNode(
        code="WC.STATUTORY.MED",
        name="Medical Benefits",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Coverage for medical treatment",
        source="NAIC",
        parent_code="WC.STATUTORY"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="WC.STATUTORY.DISABILITY",
        name="Disability Benefits",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Income replacement for disabled workers",
        source="NAIC",
        parent_code="WC.STATUTORY"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="WC.STATUTORY.REHAB",
        name="Rehabilitation Benefits",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Coverage for rehabilitation services",
        source="NAIC",
        parent_code="WC.STATUTORY"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="WC.STATUTORY.DEATH",
        name="Death Benefits",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Benefits for work-related deaths",
        source="NAIC",
        parent_code="WC.STATUTORY"
    ))


def extend_marine_taxonomy(taxonomy: TaxonomyManager):
    """
    Extend the Marine Insurance taxonomy branch with detailed subcategories.
    
    Args:
        taxonomy: The taxonomy manager to extend
    """
    # Marine - Categories
    taxonomy.add_node(TaxonomyNode(
        code="MARINE.OCEAN",
        name="Ocean Marine",
        level=TaxonomyLevel.COVERAGE_CATEGORY,
        description="Coverage for ocean-going vessels and cargo",
        source="ISO",
        parent_code="MARINE"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="MARINE.INLAND",
        name="Inland Marine",
        level=TaxonomyLevel.COVERAGE_CATEGORY,
        description="Coverage for property in transit on land",
        source="ISO",
        parent_code="MARINE"
    ))
    
    # Ocean Marine - Types
    taxonomy.add_node(TaxonomyNode(
        code="MARINE.OCEAN.HULL",
        name="Hull Insurance",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Coverage for vessel damage",
        source="ISO",
        parent_code="MARINE.OCEAN"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="MARINE.OCEAN.CARGO",
        name="Cargo Insurance",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Coverage for transported goods",
        source="ISO",
        parent_code="MARINE.OCEAN"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="MARINE.OCEAN.P&I",
        name="Protection & Indemnity",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Liability coverage for vessels",
        source="ISO",
        parent_code="MARINE.OCEAN"
    ))
    
    # Inland Marine - Types
    taxonomy.add_node(TaxonomyNode(
        code="MARINE.INLAND.TRANSIT",
        name="Transit Coverage",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Coverage for goods in transit",
        source="ISO",
        parent_code="MARINE.INLAND"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="MARINE.INLAND.BAILEE",
        name="Bailee Coverage",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Coverage for property of others in your care",
        source="ISO",
        parent_code="MARINE.INLAND"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="MARINE.INLAND.INSTALL",
        name="Installation Floater",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Coverage for property during installation",
        source="ISO",
        parent_code="MARINE.INLAND"
    ))


def extend_directors_officers_taxonomy(taxonomy: TaxonomyManager):
    """
    Extend the Directors & Officers Liability taxonomy branch with detailed subcategories.
    
    Args:
        taxonomy: The taxonomy manager to extend
    """
    # D&O - Coverage Categories
    taxonomy.add_node(TaxonomyNode(
        code="DO.SIDEA",
        name="Side A Coverage",
        level=TaxonomyLevel.COVERAGE_CATEGORY,
        description="Coverage for non-indemnified losses",
        source="ISO",
        parent_code="DO"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="DO.SIDEB",
        name="Side B Coverage",
        level=TaxonomyLevel.COVERAGE_CATEGORY,
        description="Reimbursement for indemnified losses",
        source="ISO",
        parent_code="DO"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="DO.SIDEC",
        name="Side C Coverage",
        level=TaxonomyLevel.COVERAGE_CATEGORY,
        description="Entity coverage for securities claims",
        source="ISO",
        parent_code="DO"
    ))
    
    # Side A - Types
    taxonomy.add_node(TaxonomyNode(
        code="DO.SIDEA.DIF",
        name="Difference in Conditions",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Broader coverage when primary policy doesn't respond",
        source="ISO",
        parent_code="DO.SIDEA"
    ))


def extend_epl_taxonomy(taxonomy: TaxonomyManager):
    """
    Extend the Employment Practices Liability taxonomy branch with detailed subcategories.
    
    Args:
        taxonomy: The taxonomy manager to extend
    """
    # EPL - Coverage Types
    taxonomy.add_node(TaxonomyNode(
        code="EPL.WRONGTERM",
        name="Wrongful Termination",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Coverage for improper employment termination",
        source="ISO",
        parent_code="EPL"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="EPL.DISCRIM",
        name="Discrimination",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Coverage for workplace discrimination claims",
        source="ISO",
        parent_code="EPL"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="EPL.HARASS",
        name="Harassment",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Coverage for workplace harassment claims",
        source="ISO",
        parent_code="EPL"
    ))
    
    taxonomy.add_node(TaxonomyNode(
        code="EPL.RETALIATION",
        name="Retaliation",
        level=TaxonomyLevel.COVERAGE_TYPE,
        description="Coverage for workplace retaliation claims",
        source="ISO",
        parent_code="EPL"
    ))


def create_extended_taxonomy():
    """
    Create a fully extended taxonomy with all detailed categories.
    
    Returns:
        TaxonomyManager: A fully populated taxonomy manager
    """
    taxonomy = TaxonomyManager()
    
    # Extend each line of business with detailed categories
    extend_property_taxonomy(taxonomy)
    extend_liability_taxonomy(taxonomy)
    extend_cyber_taxonomy(taxonomy)
    extend_auto_taxonomy(taxonomy)
    extend_professional_liability_taxonomy(taxonomy)
    extend_workers_comp_taxonomy(taxonomy)
    extend_marine_taxonomy(taxonomy)
    extend_directors_officers_taxonomy(taxonomy)
    extend_epl_taxonomy(taxonomy)
    
    return taxonomy


# Example usage
if __name__ == "__main__":
    # Create fully extended taxonomy
    extended_taxonomy = create_extended_taxonomy()
    
    # Print the full extended taxonomy
    print("Extended Insurance Policy Taxonomy Hierarchy:")
    extended_taxonomy.print_hierarchy()
    
    # Save the extended taxonomy to a file
    extended_taxonomy.save_taxonomy("extended_taxonomy.json")
    
    # Print specific branches
    print("\nExtended Cyber Insurance Branch:")
    extended_taxonomy.print_hierarchy("CYBER")