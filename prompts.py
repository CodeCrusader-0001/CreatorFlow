"""
CreatorFlow Prompt Templates Module.
Stores structured system prompts and prompt builders for all generation engines.
"""

# ==============================================================================
# CONTENT STUDIO PROMPTS
# ==============================================================================

CONTENT_STUDIO_SYSTEM_PROMPT = """
You are an expert digital content strategist, viral copywriter, and creative producer.
Your goal is to analyze story and script concepts and create compelling, publication-ready promotional assets.
Always return responses strictly formatted as a valid JSON object matching the requested schema.
Do not wrap responses in conversational preamble.
"""

def build_content_studio_prompt(
    story_text: str,
    genre: str,
    audience: str,
    language: str,
    tone: str
) -> str:
    """Build prompt for generating titles, description, and hooks."""
    return f"""
Analyze the provided story/script and generate a high-performing content production bundle.

INPUT DETAILS:
- Story/Script Text:
\"\"\"{story_text}\"\"\"
- Genre: {genre}
- Target Audience: {audience}
- Language: {language}
- Tone: {tone}

REQUIREMENTS:
1. Exactly 5 catchy, high-CTR titles designed for digital storytelling platforms.
   For each title, provide the hook angle and why it appeals to {audience}.
2. Exactly 1 engaging, comprehensive synopsis/description (100–180 words) that hooks the reader, outlines the core premise, builds tension, and ends with a captivating call-to-action.
3. Exactly 3 distinct promotional hooks (short, punchy opening lines designed to stop the scroll in under 3 seconds).
   Specify the hook type (e.g., Curiosity Gap, High Stakes, Emotional Trigger).

Format your output STRICTLY as a JSON object with this exact structure:
{{
  "titles": [
    {{"title": "...", "angle": "Curiosity / Drama / etc.", "reasoning": "..."}},
    {{"title": "...", "angle": "...", "reasoning": "..."}},
    {{"title": "...", "angle": "...", "reasoning": "..."}},
    {{"title": "...", "angle": "...", "reasoning": "..."}},
    {{"title": "...", "angle": "...", "reasoning": "..."}}
  ],
  "description": {{
    "synopsis": "...",
    "key_themes": ["theme1", "theme2", "theme3"],
    "call_to_action": "..."
  }},
  "hooks": [
    {{"hook": "...", "type": "Curiosity Gap", "trigger": "..."}},
    {{"hook": "...", "type": "Emotional Stakes", "trigger": "..."}},
    {{"hook": "...", "type": "Provocative Question", "trigger": "..."}}
  ]
}}
"""


# ==============================================================================
# REPURPOSE STUDIO PROMPTS
# ==============================================================================

REPURPOSE_SYSTEM_PROMPT = """
You are a senior social media director and multi-platform content repurposing specialist.
You adapt narratives into native formats for specific social channels (Instagram, YouTube, Short Video scripts, WhatsApp).
Ensure the tone matches platform norms while staying true to the source material.
Always return responses strictly formatted as a valid JSON object matching the requested schema.
"""

def build_repurpose_prompt(
    story_text: str,
    target_format: str,
    tone: str
) -> str:
    """Build prompt for repurposing content into platform-specific format."""
    format_guidelines = {
        "repurpose_instagram": (
            "An Instagram caption: A punchy opening hook (line 1), a compelling micro-story breakdown with clean line breaks, "
            "a strong conversation-starting question or CTA, and 8-12 niche/trending relevant hashtags."
        ),
        "repurpose_youtube": (
            "A comprehensive YouTube video description: An SEO-optimized video title suggestion, a captivating 2-paragraph overview, "
            "structured chapter timestamp placeholders (e.g., 00:00 Intro, 01:30 The Turning Point), key takeaways, links placeholder, and 5-8 YouTube video tags."
        ),
        "repurpose_video_script": (
            "A high-retention 30-60 second Short Video script (TikTok / Instagram Reels / YouTube Shorts): "
            "A structured breakdown across scenes with [Visual Cue], [Voiceover / Audio], [On-Screen Text], and timing (seconds). "
            "Designed to maximize completion rate and shareability."
        ),
        "repurpose_whatsapp": (
            "A high-impact WhatsApp promotional broadcast message: Engaging greeting/headline with bolding (*headline*), "
            "emojis, quick 3-bullet core highlights, and an urgent, friendly forward/join call-to-action formatted for mobile messaging."
        )
    }

    guidelines = format_guidelines.get(target_format, "A tailored platform-specific promotional piece.")

    return f"""
Repurpose the following story/script into native content for: {target_format}

SOURCE CONTENT:
\"\"\"{story_text}\"\"\"

SPECIFICATIONS:
- Target Format: {target_format}
- Tone: {tone}
- Format Guidelines: {guidelines}

Format your output STRICTLY as a JSON object with this exact structure:
{{
  "format": "{target_format}",
  "headline_or_title": "A strong headline or title",
  "formatted_content": "The full, ready-to-copy platform-ready text formatted cleanly with line breaks, emojis, and styling appropriate for the channel",
  "components": {{
    "hook": "Opening hook or scene",
    "core_body": "Main narrative or script body",
    "call_to_action": "Target call-to-action",
    "extras": "Hashtags, SEO tags, or scene timings"
  }},
  "production_tips": "1-2 brief tactical tips for posting or recording this asset"
}}
"""


# ==============================================================================
# TRANSLATION STUDIO PROMPTS
# ==============================================================================

TRANSLATION_SYSTEM_PROMPT = """
You are a master literary transcreator and multilingual localization expert.
Your job is not literal word-for-word translation, but cultural adaptation and transcreation:
preserving emotional weight, narrative voice, dialogue cadence, character names, and suspense in the target language.
Do not claim to replace certified native human proofreading.
Always return responses strictly formatted as a valid JSON object matching the requested schema.
"""

def build_translation_prompt(
    text: str,
    target_language: str,
    source_language: str = "English"
) -> str:
    """Build prompt for transcreation / translation."""
    return f"""
Translate and transcreate the provided creative content from {source_language} into {target_language}.

SOURCE TEXT ({source_language}):
\"\"\"{text}\"\"\"

TRANSCREATION PRINCIPLES:
1. Preserve emotional resonance, dramatic rhythm, suspense, and character nuance.
2. Adapt cultural idioms or metaphors naturally into {target_language} without losing the original meaning.
3. Keep personal and geographical names consistent and phonetically natural.
4. Maintain modern, authentic conversational tone suitable for digital audiences.

Format your output STRICTLY as a JSON object with this exact structure:
{{
  "target_language": "{target_language}",
  "translated_text": "The full transcreated text in {target_language}",
  "pronunciation_or_transliteration_note": "Brief note on phonetics or script if applicable (or null)",
  "cultural_adaptation_notes": "1-2 sentences explaining how tone or metaphors were adapted for {target_language}",
  "disclaimer": "AI-generated translation preserving emotional nuance; human native review is recommended for formal publication."
}}
"""


# ==============================================================================
# CONTENT EVALUATOR PROMPTS
# ==============================================================================

EVALUATOR_SYSTEM_PROMPT = """
You are an editorial director and content analytics consultant.
You provide objective, rigorous evaluations of creative and promotional content using a standardized quality rubric.
Your scores reflect editorial quality benchmarks and structural craft, not guaranteed viral metrics.
Always return responses strictly formatted as a valid JSON object matching the requested schema.
"""

def build_evaluator_prompt(
    content_text: str,
    content_type: str = "General Content"
) -> str:
    """Build prompt for rubric-based content evaluation."""
    return f"""
Critique and evaluate the following content using our 5-pillar editorial rubric.

CONTENT TO EVALUATE ({content_type}):
\"\"\"{content_text}\"\"\"

EVALUATION RUBRIC (Score each criterion from 0 to 10 strictly based on craft):
1. Clarity (0–10): Is the message clear, easy to follow, and free of confusing clutter?
2. Emotional Appeal (0–10): Does it evoke curiosity, excitement, empathy, or dramatic tension?
3. Audience Relevance (0–10): Does it directly speak to target audience pain points, interests, or entertainment desires?
4. Originality (0–10): Does it avoid tired clichés and offer a fresh angle or distinctive voice?
5. Promotional Effectiveness (0–10): Will this drive desired action (clicks, reads, shares, follows)?

SCORING FORMULA:
Overall Score = (Clarity + Emotional Appeal + Audience Relevance + Originality + Promotional Effectiveness) * 2
The overall score must be an integer or single decimal from 0 to 100.

Format your output STRICTLY as a JSON object with this exact structure:
{{
  "overall_score": 84,
  "criteria_scores": {{
    "clarity": 8.5,
    "emotional_appeal": 9.0,
    "audience_relevance": 8.0,
    "originality": 8.0,
    "promotional_effectiveness": 8.5
  }},
  "score_tier": "High Performing / Strong / Developing / Needs Revision",
  "strengths": [
    "Specific craft strength 1",
    "Specific craft strength 2",
    "Specific craft strength 3"
  ],
  "weaknesses": [
    "Specific area of weakness 1",
    "Specific area of weakness 2"
  ],
  "actionable_suggestions": [
    "Tactical editorial adjustment 1",
    "Tactical editorial adjustment 2",
    "Tactical editorial adjustment 3"
  ],
  "disclaimer": "Scores are AI-generated heuristic estimates of craft quality, not guaranteed audience engagement predictions."
}}
"""


# ==============================================================================
# A/B HOOK TESTING PROMPTS
# ==============================================================================

AB_HOOK_SYSTEM_PROMPT = """
You are a viral growth strategist and headline optimization specialist.
You construct distinct psychological hooks and evaluate them competitively under rigorous editorial rubrics.
Always return responses strictly formatted as a valid JSON object matching the requested schema.
"""

def build_ab_hook_prompt(
    story_text: str,
    genre: str = "General",
    audience: str = "General Audience",
    tone: str = "Engaging"
) -> str:
    """Build prompt for A/B hook generation and competitive rubric evaluation."""
    return f"""
Given the story/script below, develop 3 distinct promotional hooks using three different psychological frameworks.
Then, evaluate all 3 candidates against the 5-criterion rubric and declare the strongest candidate.

INPUT:
- Story/Script: \"\"\"{story_text}\"\"\"
- Genre: {genre}
- Target Audience: {audience}
- Tone: {tone}

FRAMEWORKS:
- Hook A: Curiosity Gap / Deep Mystery (leaves an irresistible unanswered question)
- Hook B: High Emotional Stakes / Vulnerability (taps into human fear, triumph, or relational intensity)
- Hook C: Provocative / Contrarian Agitation (challenges common assumptions or makes a bold claim)

RUBRIC CRITERIA FOR EACH HOOK (0–10 each):
- Clarity
- Emotional Appeal
- Audience Relevance
- Originality
- Promotional Effectiveness
Overall Score = (Clarity + Emotional Appeal + Audience Relevance + Originality + Promotional Effectiveness) * 2 (0-100)

Format your output STRICTLY as a JSON object with this exact structure:
{{
  "hooks": [
    {{
      "id": "A",
      "framework": "Curiosity Gap",
      "hook_text": "...",
      "rationale": "Why this angle works...",
      "scores": {{
        "clarity": 8.5,
        "emotional_appeal": 9.0,
        "audience_relevance": 8.0,
        "originality": 8.5,
        "promotional_effectiveness": 9.0
      }},
      "overall_score": 86.0
    }},
    {{
      "id": "B",
      "framework": "High Emotional Stakes",
      "hook_text": "...",
      "rationale": "...",
      "scores": {{
        "clarity": 8.0,
        "emotional_appeal": 9.5,
        "audience_relevance": 8.5,
        "originality": 7.5,
        "promotional_effectiveness": 8.5
      }},
      "overall_score": 84.0
    }},
    {{
      "id": "C",
      "framework": "Provocative Agitation",
      "hook_text": "...",
      "rationale": "...",
      "scores": {{
        "clarity": 9.0,
        "emotional_appeal": 8.0,
        "audience_relevance": 8.5,
        "originality": 9.0,
        "promotional_effectiveness": 8.5
      }},
      "overall_score": 86.0
    }}
  ],
  "winner": {{
    "hook_id": "A",
    "hook_text": "...",
    "framework": "Curiosity Gap",
    "overall_score": 86.0,
    "winning_reason": "Detailed justification based on rubric metrics..."
  }},
  "comparison_summary": "1-2 sentence takeaway comparing the candidate strengths.",
  "disclaimer": "Evaluations are algorithmic estimates based on structural craft benchmarks. Real-world click-through rates will vary by distribution channel and audience mood."
}}
"""

