

import json
from typing import Dict, Any, List
from groq import Groq, GroqError

from prompts import (
    REGION_GUIDELINES,
    PERSONA_GUIDELINES,
    EMAIL_GENERATION_PROMPT,
    SUBJECT_LINE_PROMPT,
    SUBJECT_AB_TEST_PROMPT,
    REGION_REWRITE_PROMPT,
    PERSONALISATION_PROMPT,
    EMAIL_IMPROVEMENT_PROMPT,
    AUTO_IMPROVE_PROMPT,
    EVALUATE_EMAIL_PROMPT,
    WHY_THIS_WORKS_PROMPT,
    FULL_PIPELINE_SYSTEM_PROMPT,
)

# ── 1. Configuration ───────────────────────────────────────────────────────────
MODEL_NAME = "llama-3.3-70b-versatile"


def get_client(api_key: str) -> Groq:
    if not api_key or not str(api_key).strip():
        raise ValueError("Groq API key cannot be empty.")
    return Groq(api_key=str(api_key).strip())


def _chat_json(client: Groq, system: str, user: str, temperature: float = 0.7) -> Dict[str, Any]:
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=temperature,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        content = response.choices[0].message.content.strip()
        try:
            val = json.loads(content)
            if not isinstance(val, dict):
                return {}
            return val
        except json.JSONDecodeError:
            return {}
    except GroqError as e:
        raise Exception(f"Groq API Error: {str(e)}")
    except Exception as e:
        raise Exception(str(e))


# ── 2. Independent Modular Tasks ───────────────────────────────────────────────

def personalise_opening(client: Groq, name: str, role: str, company_type: str,
                         location: str, linkedin_notes: str, product: str, region: str, persona: str) -> str:
    rules = REGION_GUIDELINES.get(region, REGION_GUIDELINES["Global"])
    persona_rule = PERSONA_GUIDELINES.get(persona, PERSONA_GUIDELINES["Other (General)"])
    
    user_prompt = PERSONALISATION_PROMPT.format(
        name=name, role=role, company_type=company_type, location=location,
        linkedin_notes=linkedin_notes, product=product, region=region, persona=persona,
        region_tone=rules["tone"], persona_guideline=persona_rule
    )
    result = _chat_json(client, FULL_PIPELINE_SYSTEM_PROMPT, user_prompt, temperature=0.75)
    return result.get("personalization", "Error: LLM did not return 'personalization' field.")


def generate_email(client: Groq, product: str, audience: str, region: str,
                   name: str, role: str, company_type: str, location: str, opener: str, persona: str) -> str:
    rules = REGION_GUIDELINES.get(region, REGION_GUIDELINES["Global"])
    persona_rule = PERSONA_GUIDELINES.get(persona, PERSONA_GUIDELINES["Other (General)"])
    
    user_prompt = EMAIL_GENERATION_PROMPT.format(
        product=product, audience=audience, region=region,
        name=name, role=role, company_type=company_type, 
        location=location, opener=opener, persona=persona,
        region_tone=rules["tone"], region_cta=rules["cta"], persona_guideline=persona_rule
    )
    result = _chat_json(client, FULL_PIPELINE_SYSTEM_PROMPT, user_prompt, temperature=0.7)
    return result.get("email", "Error: LLM did not return an 'email' field.")


def generate_subject_lines(client: Groq, product: str, audience: str, email_body: str, 
                           name: str, role: str, company_type: str, region: str, location: str, persona: str) -> List[Dict]:
    rules = REGION_GUIDELINES.get(region, REGION_GUIDELINES["Global"])
    persona_rule = PERSONA_GUIDELINES.get(persona, PERSONA_GUIDELINES["Other (General)"])
    
    user_prompt = SUBJECT_LINE_PROMPT.format(
        product=product, audience=audience, email_body=email_body,
        name=name, role=role, company_type=company_type, location=location,
        region=region, region_tone=rules["tone"], persona=persona, persona_guideline=persona_rule
    )
    result = _chat_json(client, FULL_PIPELINE_SYSTEM_PROMPT, user_prompt, temperature=0.75)
    return result.get("subject_lines", [])


def simulate_ab_test(client: Groq, subjects_data: List[Dict]) -> Dict[str, Any]:
    """Generates an explicit A/B test simulation parsing the generated subject lines output."""
    if not subjects_data:
        return {"winner": "N/A", "reason": "No subjects generated to test.", "comparison": "N/A"}
    
    user_prompt = SUBJECT_AB_TEST_PROMPT.format(subjects_data=json.dumps(subjects_data, indent=2))
    result = _chat_json(client, FULL_PIPELINE_SYSTEM_PROMPT, user_prompt, temperature=0.6)
    return {
        "winner": result.get("winner", "N/A"),
        "reason": result.get("reason", "N/A"),
        "comparison": result.get("comparison", "N/A"),
    }


def rewrite_for_region(client: Groq, email_body: str, name: str, role: str, company_type: str, region: str, location: str) -> str:
    rules = REGION_GUIDELINES.get(region, REGION_GUIDELINES["Global"])
    user_prompt = REGION_REWRITE_PROMPT.format(
        email_body=email_body, name=name, region=region, region_tone=rules["tone"], region_cta=rules["cta"]
    )
    result = _chat_json(client, FULL_PIPELINE_SYSTEM_PROMPT, user_prompt, temperature=0.6)
    return result.get("regional_version", "Error: LLM did not return 'regional_version' field.")


def improve_email(client: Groq, email_body: str, role: str, region: str, name: str, company_type: str, location: str, persona: str) -> Dict[str, Any]:
    rules = REGION_GUIDELINES.get(region, REGION_GUIDELINES["Global"])
    persona_rule = PERSONA_GUIDELINES.get(persona, PERSONA_GUIDELINES["Other (General)"])

    user_prompt = EMAIL_IMPROVEMENT_PROMPT.format(
        email_body=email_body, role=role, region=region, 
        name=name, company_type=company_type, location=location, persona=persona,
        region_tone=rules["tone"], region_cta=rules["cta"], persona_guideline=persona_rule
    )
    result = _chat_json(client, FULL_PIPELINE_SYSTEM_PROMPT, user_prompt, temperature=0.7)
    return {
        "diagnosis": result.get("diagnosis", "Data unavailable"),
        "improved_email": result.get("improved_email", "Data unavailable"),
        "what_changed": result.get("what_changed", []),
        "why_better": result.get("why_better", "Data unavailable"),
    }


def get_reply_score(client: Groq, email_body: str) -> Dict[str, Any]:
    """Evaluates the email out of 10 and provides probability parameters."""
    user_prompt = EVALUATE_EMAIL_PROMPT.format(email_body=email_body)
    result = _chat_json(client, FULL_PIPELINE_SYSTEM_PROMPT, user_prompt, temperature=0.5)
    return {
        "clarity": result.get("clarity", 0),
        "personalization": result.get("personalization", 0),
        "relevance": result.get("relevance", 0),
        "cta": result.get("cta", 0),
        "overall": result.get("overall", 0),
        "reply_probability": result.get("reply_probability", 0),
        "strengths": result.get("strengths", []),
        "improvements": result.get("improvements", [])
    }


def auto_improve_using_feedback(client: Groq, email_body: str, improvements: List[str], region: str, persona: str) -> str:
    """Takes explicit criticism from the evaluation engine and strictly re-factors the email autonomously."""
    if not improvements:
        return email_body
    
    rules = REGION_GUIDELINES.get(region, REGION_GUIDELINES["Global"])
    persona_rule = PERSONA_GUIDELINES.get(persona, PERSONA_GUIDELINES["Other (General)"])
    
    user_prompt = AUTO_IMPROVE_PROMPT.format(
        email_body=email_body, improvements=json.dumps(improvements),
        region_tone=rules["tone"], region_cta=rules["cta"], persona=persona, persona_guideline=persona_rule
    )
    result = _chat_json(client, FULL_PIPELINE_SYSTEM_PROMPT, user_prompt, temperature=0.7)
    return result.get("auto_improved_email", email_body)


def get_why_this_works(client: Groq, email_body: str) -> List[str]:
    """Generates 2 short bullet points explaining why the copy is effective."""
    user_prompt = WHY_THIS_WORKS_PROMPT.format(email_body=email_body)
    result = _chat_json(client, FULL_PIPELINE_SYSTEM_PROMPT, user_prompt, temperature=0.6)
    return result.get("why_this_works", [])


def get_best_subject(subjects: List[Dict]) -> Dict:
    """Identify the best subject line structurally derived from the JSON generation block."""
    if not subjects:
        return {}
    try:
        return max(subjects, key=lambda x: int(x.get("score", 0)))
    except Exception:
        return subjects[0]
