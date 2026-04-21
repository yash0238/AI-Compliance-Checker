import re
import os
from typing import Dict, Any, List

from langgraph.graph import StateGraph, END
from src.pipeline.state import ContractState

from src.utils.pdf_extract import extract_pdf
from src.utils.cleaner import normalize_text, chunk_text
from src.clause_engine.clause_extractor import extract_clauses
from src.risk_engine.risk_engine import assess_clauses
from src.regulatory.gdpr_live_tracker import detect_gdpr_changes
from src.regulatory.hipaa_live_tracker import detect_hipaa_changes
from src.contract_modification.gap_analyzer import identify_high_risk_clauses
from src.contract_modification.amendment_generator import generate_amendment

def extract_text_node(state: ContractState) -> Dict:
    print("Graph Node: Extracting Text...")
    raw_text = extract_pdf(state["pdf_path"])
    clean_text = normalize_text(raw_text)
    
    original_header = clean_text.split("\n\n")[0].strip() if clean_text else ""
    return {
        "raw_text": raw_text, 
        "clean_text": clean_text, 
        "original_header": original_header,
        "current_step": "Text Extraction Completed",
        "progress_percentage": 20,
        "iteration_count": 0,
        "max_iterations": 2 # Default max 2 self-correction cycles
    }

def extract_clauses_node(state: ContractState) -> Dict:
    print("Graph Node: Extracting Clauses...")
    clean_text = state["clean_text"]
    MAX_LENGTH = 45000
    clauses = []
    
    if len(clean_text) > MAX_LENGTH:
        chunks = chunk_text(clean_text, max_tokens=1500)
        for idx, chunk in enumerate(chunks):
            extracted = extract_clauses(chunk)
            for c in extracted:
                c["clause_id"] = f"chunk{idx}_{c.get('clause_id', 'c')}"
            clauses.extend(extracted)
    else:
        clauses = extract_clauses(clean_text)
        
    return {
        "clauses": clauses,
        "current_step": "Clauses Extracted",
        "progress_percentage": 40
    }

def assess_risk_node(state: ContractState) -> Dict:
    print(f"Graph Node: Assessing Risk (Iter {state.get('iteration_count', 0)}) ...")
    
    # In a loop, we evaluate the 'clauses' which might have been updated by 'apply_amendments_node'
    assessed = assess_clauses(state["clauses"])
    
    return {
        "assessed_clauses": assessed,
        "current_step": f"Risk Assessment Completed (Iteration {state.get('iteration_count', 0)})",
        "progress_percentage": 60 + (state.get("iteration_count", 0) * 5)
    }

def fetch_regulations_node(state: ContractState) -> Dict:
    # Only fetch once in the first iteration
    if state.get("iteration_count", 0) > 0:
        return {"current_step": "Regulatory Context Maintained"}
        
    print("Graph Node: Fetching Live Regulations...")
    gdpr = detect_gdpr_changes()
    hipaa = detect_hipaa_changes()
    
    return {
        "regulatory_updates": {"gdpr": gdpr, "hipaa": hipaa},
        "current_step": "Regulatory Updates Fetched",
        "progress_percentage": 70
    }

def decide_amendment(state: ContractState) -> str:
    """
    Conditional routing logic for the self-correction loop.
    """
    assessed = state.get("assessed_clauses", [])
    high_risk = identify_high_risk_clauses(assessed)
    
    iters = state.get("iteration_count", 0)
    max_iters = state.get("max_iterations", 2)

    if not high_risk:
        print("Decision: No High Risk Clauses -> Finalizing.")
        return "finalize_contract_node"
    
    if iters >= max_iters:
        print(f"Decision: Max Iterations ({max_iters}) reached -> Finalizing with remaining risks.")
        return "finalize_contract_node"
        
    print(f"Decision: {len(high_risk)} High Risk Clauses found -> Routing to Amendment Node (Iteration {iters + 1})")
    return "amend_clauses_node"

def amend_clauses_node(state: ContractState) -> Dict:
    print(f"Graph Node: Generating Amendments (Correction Cycle {state.get('iteration_count', 0) + 1}) ...")
    high_risk = identify_high_risk_clauses(state.get("assessed_clauses", []))
    amendments = state.get("amendments", {}).copy() 
    
    new_amendments_count = 0
    for clause in high_risk:
        risk = clause.get("risk", {})
        if risk.get("severity") != "high":
            continue
            
        risk_reason = risk.get("risk_reason") or risk.get("explanation")
        if not risk_reason:
            continue
            
        cid = clause["clause_id"]
        amended_body = generate_amendment(
            original_clause=clause["clause_text"],
            reason=risk_reason,
            regulation=risk.get("regulation_violations", "General Compliance")
        )
        
        heading = clause["clause_text"].split("\n", 1)[0].strip()
        amendments[cid] = f"{heading}\n{amended_body}"
        new_amendments_count += 1
        
    return {
        "amendments": amendments,
        "current_step": f"Generated {new_amendments_count} corrections",
        "progress_percentage": 80
    }

def apply_amendments_to_state_node(state: ContractState) -> Dict:
    """
    Updates the active 'clauses' list with the text from 'amendments'
    so the next 'assess_risk_node' can verify the improvements.
    """
    print("Graph Node: Applying Amendments to active state for re-evaluation...")
    updated_clauses = [c.copy() for c in state["clauses"]]
    amendments = state.get("amendments", {})
    
    for clause in updated_clauses:
        cid = clause.get("clause_id")
        if cid in amendments:
            # We preserve the ID and rationale but update the text for the LLM to re-evaluate
            clause["clause_text"] = amendments[cid]
            
    return {
        "clauses": updated_clauses,
        "iteration_count": state.get("iteration_count", 0) + 1,
        "current_step": "Preparing for re-evaluation loop"
    }

def finalize_contract_node(state: ContractState) -> Dict:
    print("Graph Node: Finalizing Contract...")
    clean_text = state["clean_text"]
    amendments = state.get("amendments", {})
    updated_text = clean_text
    
    # We apply all amendments to the very original text for the final output
    for clause_id, amended_clause in amendments.items():
        # This matches the clause heading or ID to replace the block
        pattern = rf"(^|\n){re.escape(clause_id)}\.?\s+.*?(?=\n\d+(?:\.\d+)*\.?\s|\Z)"
        updated_text, _ = re.subn(pattern, f"\n{amended_clause.strip()}", updated_text, flags=re.DOTALL)
        
    assessed_clauses = state.get("assessed_clauses", [])
    issues = []
    for c in assessed_clauses:
        severity = c.get("risk", {}).get("severity", "medium")
        if severity in ["high", "critical"]:
            issues.append({
                "regulation": c.get("risk", {}).get("regulation_violations", ["General"])[0] if isinstance(c.get("risk", {}).get("regulation_violations"), list) and c.get("risk", {}).get("regulation_violations") else "General",
                "issue_type": "high_risk_clause",
                "clause_id": c["clause_id"],
                "clause_type": c.get("risk", {}).get("clause_type", "Unknown"),
                "severity": severity,
                "explanation": c.get("risk", {}).get("explanation", ""),
                "source": "risk_engine"
            })
    
    overall_status = "NON-COMPLIANT" if issues else "COMPLIANT"
    
    compliance_report = {
        "total_clauses_analyzed": len(assessed_clauses),
        "total_issues_detected": len(issues),
        "issues": issues,
        "overall_status": overall_status,
        "self_correction_cycles": state.get("iteration_count", 0)
    }
    
    return {
        "updated_contract_text": updated_text,
        "compliance_report": compliance_report,
        "current_step": "Pipeline Completed",
        "progress_percentage": 100
    }

def create_workflow():
    workflow = StateGraph(ContractState)
    
    workflow.add_node("extract_text_node", extract_text_node)
    workflow.add_node("extract_clauses_node", extract_clauses_node)
    workflow.add_node("assess_risk_node", assess_risk_node)
    workflow.add_node("fetch_regulations_node", fetch_regulations_node)
    workflow.add_node("amend_clauses_node", amend_clauses_node)
    workflow.add_node("apply_amendments_node", apply_amendments_to_state_node)
    workflow.add_node("finalize_contract_node", finalize_contract_node)
    
    workflow.set_entry_point("extract_text_node")
    workflow.add_edge("extract_text_node", "extract_clauses_node")
    workflow.add_edge("extract_clauses_node", "assess_risk_node")
    workflow.add_edge("assess_risk_node", "fetch_regulations_node")
    
    # Conditional edge to handle loops or finalization
    workflow.add_conditional_edges(
        "fetch_regulations_node",
        decide_amendment,
        {
            "amend_clauses_node": "amend_clauses_node",
            "finalize_contract_node": "finalize_contract_node"
        }
    )
    
    # Self-Correction Loop: Amend -> Apply -> Assess Again
    workflow.add_edge("amend_clauses_node", "apply_amendments_node")
    workflow.add_edge("apply_amendments_node", "assess_risk_node")
    
    workflow.add_edge("finalize_contract_node", END)
    
    return workflow

# Expose compiled graph for LangGraph Studio (compiled without checkpointer for Studio use)
graph = create_workflow().compile()
