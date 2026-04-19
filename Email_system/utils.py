

from typing import Tuple, Dict, Any
from datetime import datetime

def validate_inputs(inputs: dict) -> Tuple[bool, str]:
    required_fields = ["product", "audience", "region", "name", "role", "persona", "company_type", "location", "linkedin_notes"]
    for field in required_fields:
        if not inputs.get(field) or not str(inputs[field]).strip():
            return False, f"Please fill out the '{field.replace('_', ' ').title()}' field."
    return True, ""


def word_count(text: str) -> int:
    return len(str(text).split())


def score_to_emoji(score: int) -> str:
    """Map a score out of 10 to a visual indicator."""
    try:
        score = int(score)
        if score >= 9:
            return "🔥"
        elif score >= 7:
            return "✅"
        elif score >= 5:
            return "⚠️"
        else:
            return "❌"
    except:
        return "❓"


def highlight_diff_note(before: str, after: str) -> str:
    """Minimal visual helper for UI notes if needed."""
    return f"**Before:** {len(before.split())} words  →  **After:** {len(after.split())} words"


def build_export_text(inputs: dict, results: dict) -> str:
    """Constructs the strictly formatted Export file mapping all core outputs exactly to user requirements."""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Safely extract score list mapping
    subjects = results.get("subjects", [])
    subject_lines = []
    for i, s in enumerate(subjects, 1):
        subj = s.get("subject", "N/A")
        score = s.get("score", 0)
        reason = s.get("reasoning", "N/A")
        subject_lines.append(f"{i}. {subj}\n   Score: {score}/10  |  {reason}\n")
    
    subjects_block = "\n".join(subject_lines)
    best_subject = results.get("best_subject", {}).get("subject", "N/A")
    
    # Safely extract A/B test simulation
    ab = results.get("ab_test_result", {})
    ab_winner = ab.get("winner", "N/A")
    ab_reason = ab.get("reason", "N/A")
    ab_comparison = ab.get("comparison", "N/A")
    
    # Safely extract Auto Improvement block
    auto_improved = results.get("auto_improved_email", "")
    
    # Safely extract iteration dict
    iteration = results.get("iteration", {})
    changes = iteration.get("what_changed", [])
    changes_str = "\n".join([f"- {c}" for c in changes]) if changes else "N/A"
    
    # Safely extract evaluate dict
    score = results.get("score_data", {})
    strengths = score.get("strengths", [])
    strengths_str = "\n".join([f"- {s}" for s in strengths]) if strengths else "N/A"
    improvements = score.get("improvements", [])
    improvements_str = "\n".join([f"- {i}" for i in improvements]) if improvements else "N/A"
    
    # Safely extract why this works array
    why = results.get("why_works", [])
    why_str = "\n".join([f"- {w}" for w in why]) if why else "N/A"

    export_text = f"""COLD EMAIL SYSTEM EXPORT — {timestamp}
============================================================

INPUTS
------------------------------
Product       : {inputs.get('product', 'N/A')}
Audience      : {inputs.get('audience', 'N/A')}
Region        : {inputs.get('region', 'N/A')}
Persona Focus : {inputs.get('persona', 'N/A')}
Recipient     : {inputs.get('name', 'N/A')} — {inputs.get('role', 'N/A')}
Company       : {inputs.get('company_type', 'N/A')}, {inputs.get('location', 'N/A')}

============================================================
1. GENERATED COLD EMAIL
------------------------------
{results.get('email', 'N/A')}

============================================================
2. SUBJECT LINES
------------------------------
{subjects_block}
🏆 Best Subject Line:
{best_subject}

============================================================
3. REGIONAL ADAPTED VERSION
------------------------------
{results.get('regional_email', 'N/A')}

============================================================
4. PERSONALISED OPENING LINE
------------------------------
{results.get('opener', 'N/A')}

============================================================
5. IMPROVED EMAIL (Iteration)
------------------------------
DIAGNOSIS:
{iteration.get('diagnosis', 'N/A')}

IMPROVED EMAIL:
{iteration.get('improved_email', 'N/A')}

WHAT CHANGED:
{changes_str}

WHY IT WILL IMPROVE REPLIES:
{iteration.get('why_better', 'N/A')}

============================================================
6. EMAIL SCORE + REPLY PROBABILITY
------------------------------
Clarity: {score.get('clarity', 'N/A')}/10
Personalization: {score.get('personalization', 'N/A')}/10
Relevance: {score.get('relevance', 'N/A')}/10
CTA Strength: {score.get('cta', 'N/A')}/10
Overall Score: {score.get('overall', 'N/A')}/10
Reply Probability: {score.get('reply_probability', 'N/A')}/10

Strengths:
{strengths_str}

Improvements:
{improvements_str}

============================================================
7. WHY THIS WORKS
------------------------------
{why_str}

============================================================
8. A/B TEST RESULT
------------------------------
Winner: {ab_winner}
Reason: {ab_reason}
Comparison: {ab_comparison}

============================================================
9. AUTO IMPROVED EMAIL
------------------------------
{auto_improved if auto_improved else "Not Generated."}

============================================================
"""
    return export_text
