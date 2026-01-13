import os
import json
import time
import re
from dotenv import load_dotenv

# -------------------------
# Groq
# -------------------------
from groq import Groq
from groq import RateLimitError as GroqRateLimitError
from openai import OpenAI

# -------------------------
# Gemini
# -------------------------
try:
    from google import genai
except Exception:
    genai = None

load_dotenv()

# =====================================================
# CONFIG
# =====================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile" # Default Groq LLM model
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# =====================================================
# CLIENTS
# =====================================================
# Initialize Groq client only if available
try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception:
    groq_client = None

# Initialize Gemini client only if genai is available
if genai is not None:
    try:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception:
        gemini_client = None
else:
    gemini_client = None

# Initialize OpenRouter client
try:
    openrouter_client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )
except Exception:
    openrouter_client = None

# =====================================================
# CORE ROUTER
# =====================================================
def chat_completion(system_prompt, user_prompt, temperature=0.2):
    # -------------------------
    # 1. Try Groq (PRIMARY)
    # -------------------------
    if groq_client is not None:
        try:
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )

            return {
                "llm_used": "groq",
                "content": response.choices[0].message.content
            }

        except GroqRateLimitError:
            print("⚠ Groq rate limit hit. Falling back to Gemini...")
            time.sleep(1)

        except Exception as e:
            print("⚠ Groq error:", str(e))
    else:
        # Safe notice when Groq client is unavailable
        print("⚠ Groq client not available; skipping Groq and attempting Gemini fallback")


    # -------------------------
    # 2. OpenRouter Fallback (FREE LLaMA)
    # -------------------------
    if openrouter_client is not None:
        try:
            response = openrouter_client.chat.completions.create(
                model="meta-llama/llama-3.1-8b-instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )

            return {
                "llm_used": "openrouter-llama",
                "content": response.choices[0].message.content
            }

        except Exception as e:
            print("⚠ OpenRouter failed:", str(e))
    else:
        print("⚠ OpenRouter client not available; using hard fallback")



    # -------------------------
    # 3. HARD FALLBACK (NEVER CRASH)
    # -------------------------
    return {
        "llm_used": "none",
        "content": json.dumps({
            "risk_level": "UNKNOWN",
            "explanation": "LLM unavailable. Manual compliance review required.",
            "regulation": "N/A"
        })
    }

# =====================================================
# JSON SAFE HELPER
# =====================================================
def chat_completion_json(system_prompt, user_prompt, temperature=0.2):
    result = chat_completion(system_prompt, user_prompt, temperature)
    content = result["content"]

    try:
        parsed = json.loads(content)

        if isinstance(parsed, list):
            return {
                "data": parsed,
                "_llm_used": result["llm_used"]
            }

        parsed["_llm_used"] = result["llm_used"]
        return parsed

    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.S)
        if match:
            try:
                parsed = json.loads(match.group(0))
                parsed["_llm_used"] = result["llm_used"]
                return parsed
            except Exception:
                pass

        # FINAL SAFE RETURN (DO NOT CRASH PIPELINE)
        return {
            "risk_level": "UNKNOWN",
            "explanation": "Invalid JSON from LLM. Manual review required.",
            "regulation": "N/A",
            "_llm_used": result["llm_used"]
        }
