import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from src.llm.schemas import ClauseExtractionBox, RiskAssessment

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

def get_primary_llm(temperature=0.0):
    """Returns the primary Groq LLM instance."""
    if GROQ_API_KEY:
        return ChatGroq(
            api_key=GROQ_API_KEY, 
            model=GROQ_MODEL, 
            temperature=temperature
        )
    else:
        # Fallback to Gemini if Groq not configured
        return ChatGoogleGenerativeAI(
            api_key=GEMINI_API_KEY,
            model="gemini-1.5-flash", 
            temperature=temperature
        )

def get_fallback_llm(temperature=0.0):
    """Returns the fallback Gemini LLM instance."""
    if GEMINI_API_KEY:
        return ChatGoogleGenerativeAI(
            api_key=GEMINI_API_KEY,
            model="gemini-1.5-flash", 
            temperature=temperature
        )
    return None

def get_structured_llm(pydantic_schema, temperature=0.0):
    """
    Returns an LLM bound with structured output targeting the provided Pydantic schema.
    Uses ChatGroq first, falls back to Gemini if needed.
    """
    primary = get_primary_llm(temperature=temperature)
    try:
        if primary:
            return primary.with_structured_output(pydantic_schema)
    except Exception as e:
        print(f"Failed to bind structured output to primary LLM: {e}")
        
    fallback = get_fallback_llm(temperature=temperature)
    if fallback:
        return fallback.with_structured_output(pydantic_schema)
        
    # Standard raise if nothing works
    raise RuntimeError("No LLM configured for structured output.")
