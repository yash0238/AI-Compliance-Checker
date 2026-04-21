# src/risk_engine/risk_engine.py

import json
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from src.llm.models import get_structured_llm
from src.llm.schemas import RiskAssessment

# Optional import for RAG
try:
    from src.rag.vector_store import VectorStoreManager
    vector_manager = VectorStoreManager()
    RAG_ENABLED = True
except Exception as e:
    print(f"RAG not available or failed to load: {e}")
    vector_manager = None
    RAG_ENABLED = False

load_dotenv()

SYSTEM_PROMPT = """You are a Senior Regulatory Compliance Officer specializing in Indian Constitutional and Contract Law.
Your task is to evaluate LEGAL RISK for each contract clause using the provided INDIAN LAW CONTEXT.

Rules:
- Prioritize the provided context over general training data.
- Evaluate clauses against the Constitution of India (Fundamental Rights, etc.).
- Be strict. If a clause restricts a fundamental right (like freedom of movement or equality), mark it as high risk.

CRITICAL OUTPUT FORMAT RULES (you MUST follow these exactly):
- `risk_factors`, `missing_controls`, and `regulation_violations` MUST always be JSON arrays (lists).
- If there are no items for a list field, return an EMPTY ARRAY: [] — NEVER return an empty string "" or null.
- Example of correct empty fields: "risk_factors": [], "missing_controls": [], "regulation_violations": []
- Example of correct non-empty fields: "risk_factors": ["Potential bias", "Unequal treatment"]"""

USER_PROMPT_TEMPLATE = """Evaluate the legal and regulatory risk of the following clause:

<CONTEXT_FROM_INDIAN_LAW>
{legal_context}
</CONTEXT_FROM_INDIAN_LAW>

<CLAUSE_TEXT>
{clause}
</CLAUSE_TEXT>"""

def get_context(clause_text: str) -> str:
    """Retrieves relevant legal context using RAG."""
    if RAG_ENABLED and vector_manager is not None:
        try:
            results = vector_manager.search_similar(clause_text, k=2)
            if results:
                return "\n\n---\n\n".join([r.page_content for r in results])
        except Exception as e:
            print(f"RAG retrieval error: {e}")
    return "No specific context retrieved."

def assess_clause_with_llm(clause_text: str):
    """
    Evaluates a single clause using LangChain LCEL with a RAG step before LLM prediction.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", USER_PROMPT_TEMPLATE)
    ])

    llm_with_structure = get_structured_llm(RiskAssessment, temperature=0.0)

    # LCEL Pipeline:
    # 1. Take 'clause' as input
    # 2. Assign 'legal_context' dynamically using the get_context function
    # 3. Format the prompt
    # 4. Invoke LLM and parse to RiskAssessment structure
    chain = (
        {"clause": RunnablePassthrough(), "legal_context": lambda x: get_context(x)}
        | prompt
        | llm_with_structure
    )

    response: RiskAssessment = chain.invoke(clause_text)

    # Standardize dictionary for downstream components
    risk = response.model_dump()

    # --- Guard: LLM sometimes returns "" instead of [] for array fields ---
    # Coerce any string value into a proper list to prevent schema errors
    _array_fields = ["risk_factors", "missing_controls", "regulation_violations"]
    for field in _array_fields:
        val = risk.get(field, [])
        if isinstance(val, str):
            # Split on comma if non-empty, else use empty list
            risk[field] = [v.strip() for v in val.split(",") if v.strip()] if val.strip() else []
    # --------------------------------------------------------------------------

    # Store context used for traceability
    risk["retrieved_legal_context"] = get_context(clause_text).split("\n\n---\n\n")

    # Add severity mapping
    risk_level = risk.get("risk_level", "medium").lower()
    if risk_level in ["low", "medium", "high"]:
        risk["severity"] = risk_level
    else:
        risk["severity"] = "medium"

    risk["risk_reason"] = risk.get("explanation", "").strip()

    return risk

def assess_clauses(clauses):
    """
    Evaluates a batch of clauses.
    """
    assessed = []

    for c in clauses:
        text = c.get("clause_text", "")
        clause_id = c.get("clause_id")

        print(f"\nEvaluating risk for clause: {clause_id} ...")
        risk = assess_clause_with_llm(text)

        c["risk"] = risk
        assessed.append(c)

    return assessed
