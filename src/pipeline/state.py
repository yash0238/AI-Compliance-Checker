from typing import TypedDict, List, Dict, Any

class ContractState(TypedDict):
    """
    Represents the state of the contract compliance pipeline graph.
    """
    pdf_path: str
    raw_text: str
    clean_text: str
    original_header: str
    
    clauses: List[Dict[str, Any]]
    assessed_clauses: List[Dict[str, Any]]
    
    # Track the regulatory updates fetched
    regulatory_updates: Dict[str, Any]
    
    # Store generated amendments: clause_id -> amendment text
    amendments: Dict[str, str]
    
    # Final generated contract text
    updated_contract_text: str
    
    # Final compliance report data
    compliance_report: Dict[str, Any]
    
    # Status metrics and progress tracking
    current_step: str
    progress_percentage: int
    
    # Iteration tracking for self-correction loops
    iteration_count: int
    max_iterations: int
