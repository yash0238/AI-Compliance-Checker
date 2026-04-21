# src/clause_engine/clause_extractor.py

import json
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from src.llm.models import get_structured_llm
from src.llm.schemas import ClauseExtractionBox

load_dotenv()

SYSTEM_PROMPT = """You are a senior legal analyst AI. 
Your task is to extract ALL meaningful legal clauses from a contract.

Extract the clauses accurately according to the structured output schema provided."""

USER_PROMPT = """Extract all clauses from the following contract text:

<CONTRACT_TEXT>
{contract}
</CONTRACT_TEXT>"""

def extract_clauses(contract_text: str):
    """
    Extracts clauses using LangChain LCEL and Pydantic structured output.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", USER_PROMPT)
    ])

    llm_with_structure = get_structured_llm(ClauseExtractionBox, temperature=0.0)
    
    chain = prompt | llm_with_structure
    
    response: ClauseExtractionBox = chain.invoke({"contract": contract_text})
    
    clauses = []
    
    # Add metadata and convert to dict for backwards compatibility with run.py currently
    for idx, clause_obj in enumerate(response.data, start=1):
        clause_dict = clause_obj.model_dump()
        clause_dict["clause_id"] = str(idx)
        clause_dict["_llm_used"] = "langchain-structured"
        clauses.append(clause_dict)

    return clauses
