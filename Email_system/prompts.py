

REGION_GUIDELINES = {
    "UAE": {
        "tone": "Formal, highly respectful, relationship-first. Extreme politeness. Never pushy.",
        "cta": "If this aligns with your current priorities, I’d be glad to share a brief perspective at a time that suits you."
    },
    "US": {
        "tone": "Direct, action-oriented, clear, concise, confident. Outcome-focused pacing. Executive brevity.",
        "cta": "Would you be open to a brief 10-minute call to explore this further?"
    },
    "UK": {
        "tone": "Polite, understated, subtle. Slightly indirect. Subtle persuasion. No aggression or hype.",
        "cta": "If this sounds relevant, I’d be happy to share a bit more detail."
    },
    "India": {
        "tone": "Professional, respectful, slightly warm. A balanced mix between direct and polite.",
        "cta": "Please let me know if you’d be open to a brief discussion."
    },
    "Global": {
        "tone": "Professional, clear, standard executive B2B tone. Neutral and focused.",
        "cta": "Are you open to a brief conversation?"
    }
}

PERSONA_GUIDELINES = {
    "CFO": "Focus intensely on financial metrics: ROI, forecasting accuracy, reporting visibility, and cost-reduction.",
    "Head of Operations": "Focus intensely on efficiency: process optimization, bridging bottlenecks, and logistics streamlining.",
    "Founder": "Focus intensely on growth: scaling efficiently, long-term strategic positioning, and revenue acceleration.",
    "Other (General)": "Focus on high-level efficiency, time-savings, and systemic problem-solving."
}


# ──────────────────────────────────────────────
# 1. PERSONALISED OPENING LINE
# ──────────────────────────────────────────────
PERSONALISATION_PROMPT = """
You are a top 1% enterprise B2B sales researcher writing hyper-personalised email openers for COLD outreach.

RECIPIENT DETAILS:
- Name: {name}
- Role: {role} 
- Persona: {persona} (MANDATORY STRATEGY: {persona_guideline})
- Company: {company_type}
- Location: {location}
- Context/Notes: {linkedin_notes}

PRODUCT: {product}
CAMPAIGN REGION: {region}
REGIONAL TONE REQUIREMENTS: {region_tone}

CRITICAL ANTI-HALLUCINATION RULES:
- This is a FIRST-TIME COLD OUTREACH. NEVER invent prior relationships.
- ABSOLUTELY BAN: "our previous discussion", "following up", "as discussed". 

REGION VS LOCATION RULE:
- If Recipient Location ({location}) differs from Campaign Region ({region}), DO NOT explicitly mention the country. Use neutral phrasing like "in your market".

CONSTRAINTS:
- Write ONE genuinely personalised opening sentence (maximum 2 short sentences).
- Keep it sharp, neutral, and highly concise. Do NOT overload the sentence.
- Use their FIRST NAME only natively.

OUTPUT FORMAT:
Return a valid JSON object matching exactly this structure:
{{
  "personalization": "Your sharp, bespoke opening line here"
}}
"""

# ──────────────────────────────────────────────
# 2. COLD EMAIL GENERATION
# ──────────────────────────────────────────────
EMAIL_GENERATION_PROMPT = """
You are a senior enterprise B2B sales strategist communicating with C-Suite executives.

INPUTS:
- Product: {product}
- Campaign Region: {region}
- Recipient Name: {name}
- Recipient Role: {role}
- Persona: {persona} (MANDATORY STRATEGY: {persona_guideline})
- Company: {company_type}
- Recipient Location: {location}
- PRE-WRITTEN OPENER: "{opener}"

CRITICAL ANTI-HALLUCINATION RULES:
- This is COLD outreach. Do not use "following up," "our previous discussion".

REGION VS LOCATION RULE:
- If Recipient Location ({location}) differs from Campaign Region ({region}), DO NOT explicitly say "{region} companies". Use neutral phrasing.

ELITE STRUCTURE MANDATES:
1. Start EXACTLY with the PRE-WRITTEN OPENER: "{opener}". It must be sentence #1.
2. Context-aware insight: Bridge their context into a systemic problem tied directly to the specified Persona mechanism ({persona_guideline}).
3. Subtle value positioning: State how you solve it carefully for their specific Persona.
4. Mandatory CTA: End EXACTLY with: "{region_cta}"

CONSTRAINTS:
- Length: 4-6 lines MAXIMUM. Executive brevity is critical. 
- Tone: {region_tone}. No hype language.
- DO NOT add a subject line.

OUTPUT FORMAT:
Return a valid JSON object matching exactly this structure:
{{
  "email": "Your naturally human, persona-targeted email body here"
}}
"""

# ──────────────────────────────────────────────
# 3. SUBJECT LINE GENERATION
# ──────────────────────────────────────────────
SUBJECT_LINE_PROMPT = """
You are a top 1% cold email subject line expert.

CONTEXT:
- Recipient Info: {name}, {role} at a {company_type} in {location}
- Persona: {persona} (STRATEGY: {persona_guideline})
- Regional Tone Constraint: {region_tone}
- Email Reference:
{email_body}

TASK:
Generate exactly 5 highly realistic, benefit-driven subject lines optimized specifically for the {persona} Persona. Do not send generic business subjects.

RULES:
- FORMAT RETURNED MUST USE 'subject' FOR TEXT KEY.
- VARIETY: Use their name in some, but NOT all. Avoid repetitive formats.
- Proper Sentence Capitalization: Capitalize the first letter and proper nouns ONLY. Do NOT use Title Case.
- MUST INCLUDE CLEAR BENEFIT aligned heavily with {persona_guideline}.
- Keep them under 7 words.

OUTPUT FORMAT:
Return a valid JSON object matching exactly this structure:
{{
  "subject_lines": [
    {{
      "subject": "John, aligning reporting across operations",
      "score": 9,
      "reasoning": "Why it reads as highly human and drives professional execution curiosity."
    }}
  ]
}}
"""

# ──────────────────────────────────────────────
# 4. A/B TEST SIMULATION
# ──────────────────────────────────────────────
SUBJECT_AB_TEST_PROMPT = """
You are a top 1% email marketing analyst running an A/B test simulation.

CONTEXT:
We generated the following subject lines and scores for a cold email campaign:
{subjects_data}

TASK:
Simulate an A/B test to determine the definitive winner that will yield the highest open rate.
Evaluate based on curiosity, personalization, psychological friction, and relevance to executive-level buyers.

OUTPUT FORMAT:
Return a valid JSON object matching exactly this structure:
{{
  "winner": "The exact text of the winning subject line",
  "reason": "Why this specific subject line wins out over the others (focus on executive psychology).",
  "comparison": "A short summary of why the other concepts failed to capture the same immediate attention."
}}
"""


# ──────────────────────────────────────────────
# 5. REGIONAL CULTURAL REWRITE
# ──────────────────────────────────────────────
REGION_REWRITE_PROMPT = """
You are an executive advisor specialising in {region} corporate communications.

CONTEXT:
- Recipient Name: {name}
- Target Region: {region}

ORIGINAL EMAIL:
{email_body}

YOUR TASK:
Rewrite this email perfectly to align with {region} B2B communication business culture.

MANDATORY RULES:
1. USE THEIR ACTUAL NAME
2. REGIONAL TONE ADAPTATION: Follow this strictly: {region_tone}
3. HUMAN & SHORTER: Keep it highly natural, respectful, but concise (4-6 lines). 
4. MANDATORY CTA: Conclude with EXACTLY this CTA: "{region_cta}"

OUTPUT FORMAT:
Return a valid JSON object:
{{
  "regional_version": "Your sharply polished, naturally respectful regional email here"
}}
"""

# ──────────────────────────────────────────────
# 6. ELITE EVALUATION & SCORING
# ──────────────────────────────────────────────
EVALUATE_EMAIL_PROMPT = """
You are a top 1% enterprise B2B sales conversion expert.

TASK:
Deeply analyze this cold email and estimate the likelihood of reply.

EMAIL:
{email_body}

RULES:
- Be objective and strict.
- Provide scores entirely as integers between 1 and 10.

OUTPUT FORMAT:
Return a valid JSON object matching exactly this structure:
{{
  "clarity": 8,
  "personalization": 9,
  "relevance": 7,
  "cta": 8,
  "overall": 8,
  "reply_probability": 7,
  "strengths": ["Clear opener", "Soft CTA"],
  "improvements": ["Slightly generic middle", "Could be shorter"]
}}
"""

# ──────────────────────────────────────────────
# 7. WHY THIS WORKS EXPLANATION
# ──────────────────────────────────────────────
WHY_THIS_WORKS_PROMPT = """
You are a senior B2B sales strategist.

TASK:
Analyze the following cold email and explain precisely why it is effective.
Focus on personalization, tone, and CTA effectiveness.

EMAIL:
{email_body}

OUTPUT FORMAT:
Return a valid JSON object matching exactly this structure:
{{
  "why_this_works": [
    "Personalized opening increases relevance by highlighting their supply chain expansion naturally.",
    "Soft CTA reduces peer friction and matches executive thresholds."
  ]
}}
"""

# ──────────────────────────────────────────────
# 8. EMAIL IMPROVEMENT (ITERATION LOOP)
# ──────────────────────────────────────────────
EMAIL_IMPROVEMENT_PROMPT = """
You are a top 1% cold email conversion expert refining B2B outreach.

CONTEXT:
An email drafted for {name} ({role} at {company_type}) has structural flaws requiring rewrite.
Persona Focus strategy: {persona_guideline}

ORIGINAL EMAIL:
{email_body}

TASK:
Diagnose why it failed and rewrite it into an elite, smarter iteration. Focus on the core {persona} persona metrics.

MANDATORY REGION RULES:
- TONE: {region_tone}
- CTA: Conclude exactly with "{region_cta}"

RULES FOR REWRITE:
- RETENTION OF PERSONALIZATION: Retain {name} and contextual hook cleanly.
- Keep it 4-5 lines max. Natural, elite brevity.

OUTPUT FORMAT:
Return a valid JSON object matching exactly this structure:
{{
  "diagnosis": "Short structural diagnosis of what failed.",
  "improved_email": "Your rewritten, shorter, highly professional iteration preserving personalization and focused on {persona_guideline}.",
  "what_changed": [
    "Bullet 1 mapping shifts",
    "Bullet 2 mapping specific structural deletion"
  ],
  "why_better": "Why this completely removes psychological friction."
}}
"""

# ──────────────────────────────────────────────
# 9. AUTO IMPROVE USING FEEDBACK
# ──────────────────────────────────────────────
AUTO_IMPROVE_PROMPT = """
You are an elite B2B sales copywriter utilizing strict structural feedback to dynamically improve cold copy autonomously.

ORIGINAL EMAIL:
{email_body}

STRUCTURAL WEAKNESSES IDENTIFIED:
{improvements}

MANDATORY STRATEGY PARAMETERS:
- Persona: {persona} ({persona_guideline})
- TONE: {region_tone}
- CTA: Conclude exactly with "{region_cta}"

YOUR TASK:
Fix the explicit weaknesses documented above while explicitly injecting the proper wording for the {persona} metrics. Keep extreme brevity.

OUTPUT FORMAT:
Return a valid JSON object matching exactly this structure:
{{
  "auto_improved_email": "Your ruthlessly optimized, structurally superior email solving the specific weaknesses."
}}
"""

FULL_PIPELINE_SYSTEM_PROMPT = """
You are an advanced AI pipeline processor. Follow all user instructions strictly.
Always output purely valid, parseable JSON text without any markdown wrappers.
"""
