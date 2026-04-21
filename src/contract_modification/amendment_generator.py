# src/contract_modification/amendment_generator.py

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.llm.models import get_primary_llm

load_dotenv()

SYSTEM_PROMPT_AMEND = """You are a senior contract and compliance lawyer.

Rewrite ONLY the clause provided to resolve the identified HIGH RISK.
Do NOT add new obligations beyond what is necessary to fix the risk.
Do NOT introduce new clauses, headings, or definitions.
Preserve the original structure, numbering, and legal tone.

Return ONLY the rewritten clause text."""

USER_PROMPT_AMEND = """Original Clause:
{original_clause}

Issue:
{reason}

Regulatory Context:
{regulation}"""


SYSTEM_PROMPT_NEW = """You are a senior compliance lawyer.
Draft a legally sound contract clause."""

USER_PROMPT_NEW = """Draft a '{clause_name}' clause required under {regulation}.
The clause must be clear, enforceable, and enterprise-ready."""

def generate_amendment(original_clause, reason, regulation=None):
    """Generates an amendment for an existing clause using LangChain LCEL."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT_AMEND),
        ("user", USER_PROMPT_AMEND)
    ])
    
    llm = get_primary_llm(temperature=0.0)
    chain = prompt | llm | StrOutputParser()
    
    amended_clause = chain.invoke({
        "original_clause": original_clause,
        "reason": reason,
        "regulation": regulation if regulation else "General Compliance"
    })

    return amended_clause.strip()

def generate_compliance_clause(clause_name, regulation):
    """Generates a net-new compliance clause."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT_NEW),
        ("user", USER_PROMPT_NEW)
    ])
    
    llm = get_primary_llm(temperature=0.0)
    chain = prompt | llm | StrOutputParser()
    
    result = chain.invoke({
        "clause_name": clause_name,
        "regulation": regulation
    })
    
    return result.strip()
