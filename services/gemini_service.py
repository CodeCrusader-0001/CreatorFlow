"""
CreatorFlow Gemini Service Module.
Encapsulates all Google Gemini API interactions using the official google-genai SDK.
Handles authentication, request configuration, timeout settings, structured JSON parsing,
exponential backoff retries, and comprehensive error categorization.
"""

import json
import re
import os
import time
import ssl
from typing import Dict, Any, Optional
import httpx
from google import genai
from google.genai import types
from google.genai import errors

import config
import prompts


# ==============================================================================
# CUSTOM EXCEPTIONS
# ==============================================================================

class GeminiServiceException(Exception):
    """Base exception for CreatorFlow Gemini operations."""
    pass


class GeminiConfigError(GeminiServiceException):
    """Raised when the Gemini API key is missing or invalid."""
    pass


class GeminiSSLError(GeminiServiceException):
    """Raised when an SSL handshake or certificate verification fails."""
    pass


class GeminiConnectionError(GeminiServiceException):
    """Raised when network connectivity, DNS, or socket connection fails."""
    pass


class GeminiQuotaError(GeminiServiceException):
    """Raised when the Gemini API rate limit or quota has been reached."""
    pass


class GeminiModelUnavailableError(GeminiServiceException):
    """Raised when the requested model name is deprecated or unavailable."""
    pass


class GeminiAPIError(GeminiServiceException):
    """Raised for other unexpected API errors."""
    pass


class GeminiResponseParsingError(GeminiServiceException):
    """Raised when Gemini returns malformed or non-JSON content."""
    pass


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_effective_api_key(override_key: Optional[str] = None) -> str:
    """Retrieve the effective API key from override, config, or env."""
    key = (override_key or "").strip()
    if not key:
        key = (config.GEMINI_API_KEY or "").strip()
    if not key:
        key = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
    return key


def is_api_configured(override_key: Optional[str] = None) -> bool:
    """Check whether a non-empty API key is available."""
    return bool(get_effective_api_key(override_key))


def extract_and_parse_json(raw_text: str) -> Dict[str, Any]:
    """
    Safely extract and parse JSON from model output.
    Handles markdown code fences (```json ... ```) and leading/trailing whitespace.
    """
    if not raw_text or not raw_text.strip():
        raise GeminiResponseParsingError("Model returned an empty response.")

    cleaned = raw_text.strip()

    # If wrapped in markdown code blocks, extract inner content
    code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if code_block_match:
        cleaned = code_block_match.group(1).strip()

    # Sometimes models return JSON with a leading bracket/brace after introductory text
    if not (cleaned.startswith("{") or cleaned.startswith("[")):
        start_idx = cleaned.find("{")
        end_idx = cleaned.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            cleaned = cleaned[start_idx:end_idx + 1]

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise GeminiResponseParsingError(
            f"Failed to parse JSON response from Gemini: {e}\nRaw excerpt: {raw_text[:200]}"
        ) from e


def get_genai_client(api_key: Optional[str] = None) -> genai.Client:
    """
    Instantiate a genai.Client with verified timeout settings and retry options.
    Note: In google-genai SDK, HttpOptions.timeout is in milliseconds!
    """
    effective_key = get_effective_api_key(api_key)
    if not effective_key:
        raise GeminiConfigError(
            "Gemini API key is not configured. Please add GEMINI_API_KEY in your .env file or enter it in the sidebar."
        )

    # Ensure timeout is in milliseconds (minimum 60,000 ms = 60s)
    raw_timeout = int(config.GEMINI_REQUEST_TIMEOUT)
    timeout_ms = raw_timeout * 1000 if raw_timeout < 1000 else raw_timeout
    timeout_sec = float(timeout_ms) / 1000.0

    # Custom httpx timeout with 25s connect/SSL handshake window
    httpx_timeout = httpx.Timeout(
        connect=25.0,
        read=timeout_sec,
        write=30.0,
        pool=10.0,
    )

    retry_opts = types.HttpRetryOptions(
        attempts=3,
        initial_delay=1.0,
        max_delay=8.0,
        exp_base=2.0,
    )

    http_opts = types.HttpOptions(
        timeout=timeout_ms,
        client_args={"timeout": httpx_timeout},
        retry_options=retry_opts,
    )

    try:
        return genai.Client(api_key=effective_key, http_options=http_opts)
    except Exception as e:
        raise GeminiConfigError(f"Failed to initialize Gemini client: {e}") from e


def _execute_prompt(
    client: genai.Client,
    model_name: str,
    system_instruction: str,
    prompt: str,
    temperature: float = 0.7,
) -> str:
    """
    Execute generate_content with JSON response mode, retry logic with exponential backoff (max 3 attempts),
    and separate handling for SSL, connection, quota, model availability, and auth errors.
    """
    gen_config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=temperature,
        response_mime_type="application/json",
    )

    max_attempts = 3
    base_delay = 1.5

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=gen_config,
            )

            if not response or not response.text:
                raise GeminiAPIError("No text returned by Gemini API.")

            return response.text

        except errors.ClientError as e:
            err_msg = str(e)
            code = getattr(e, "code", None)
            if code in (401, 403) or "API_KEY_INVALID" in err_msg:
                raise GeminiConfigError(
                    "Invalid or unauthorized Gemini API key. Please check your GEMINI_API_KEY."
                ) from e
            elif code == 404 or "NOT_FOUND" in err_msg:
                raise GeminiModelUnavailableError(
                    f"Model '{model_name}' is unavailable or deprecated. Please select an active model (e.g. gemini-3.8-flash)."
                ) from e
            elif code == 429 or "RESOURCE_EXHAUSTED" in err_msg or "quota" in err_msg.lower():
                if attempt < max_attempts:
                    time.sleep(base_delay * (2 ** (attempt - 1)))
                    continue
                raise GeminiQuotaError(
                    "Gemini API rate limit or quota exceeded. Please check your Google AI Studio plan."
                ) from e
            else:
                raise GeminiAPIError(f"Gemini API client error (Code: {code}): {err_msg}") from e

        except errors.ServerError as e:
            # 500, 502, 503, 504 server errors -> retry with backoff
            if attempt < max_attempts:
                time.sleep(base_delay * (2 ** (attempt - 1)))
                continue
            raise GeminiAPIError(f"Google Gemini server temporarily unavailable (5xx): {e}") from e

        except (httpx.ConnectTimeout, ssl.SSLError) as e:
            err_str = str(e)
            # SSL Handshake Timeout or SSL verification issue
            if attempt < max_attempts:
                time.sleep(base_delay * (2 ** (attempt - 1)))
                continue
            raise GeminiSSLError(
                f"SSL Handshake / Connection timed out to Google Gemini servers ({err_str}). "
                "Check network firewall, VPN, or corporate proxy settings."
            ) from e

        except (httpx.ConnectError, httpx.NetworkError) as e:
            if attempt < max_attempts:
                time.sleep(base_delay * (2 ** (attempt - 1)))
                continue
            raise GeminiConnectionError(
                f"Network connection failure: {e}. Please check your internet connection."
            ) from e

        except Exception as e:
            err_str = str(e)
            if "handshake" in err_str.lower() or "ssl" in err_str.lower():
                if attempt < max_attempts:
                    time.sleep(base_delay * (2 ** (attempt - 1)))
                    continue
                raise GeminiSSLError(f"SSL error: {err_str}") from e
            if attempt < max_attempts and ("timeout" in err_str.lower() or "reset" in err_str.lower()):
                time.sleep(base_delay * (2 ** (attempt - 1)))
                continue
            raise GeminiAPIError(f"Unexpected error communicating with Gemini API: {e}") from e

    raise GeminiAPIError("Failed to receive response from Gemini after 3 attempts.")


# ==============================================================================
# PUBLIC SERVICE API
# ==============================================================================

def generate_content_studio(
    story_text: str,
    genre: str,
    audience: str,
    language: str,
    tone: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate 5 catchy titles, 1 description, and 3 hooks for a story/script."""
    if not story_text or not story_text.strip():
        raise ValueError("Story/script text cannot be empty.")

    client = get_genai_client(api_key)
    model_name = model or config.GEMINI_MODEL
    prompt = prompts.build_content_studio_prompt(
        story_text=story_text,
        genre=genre,
        audience=audience,
        language=language,
        tone=tone,
    )

    raw_response = _execute_prompt(
        client=client,
        model_name=model_name,
        system_instruction=prompts.CONTENT_STUDIO_SYSTEM_PROMPT,
        prompt=prompt,
        temperature=0.75,
    )

    parsed = extract_and_parse_json(raw_response)
    if "titles" not in parsed or not isinstance(parsed["titles"], list):
        parsed["titles"] = []
    if "description" not in parsed or not isinstance(parsed["description"], dict):
        parsed["description"] = {
            "synopsis": "Synopsis generated.",
            "key_themes": [],
            "call_to_action": "Read more.",
        }
    if "hooks" not in parsed or not isinstance(parsed["hooks"], list):
        parsed["hooks"] = []

    return parsed


def repurpose_content(
    story_text: str,
    target_format: str,
    tone: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Repurpose a story/script into native social formats."""
    if not story_text or not story_text.strip():
        raise ValueError("Story/script text cannot be empty.")

    client = get_genai_client(api_key)
    model_name = model or config.GEMINI_MODEL
    prompt = prompts.build_repurpose_prompt(
        story_text=story_text,
        target_format=target_format,
        tone=tone,
    )

    raw_response = _execute_prompt(
        client=client,
        model_name=model_name,
        system_instruction=prompts.REPURPOSE_SYSTEM_PROMPT,
        prompt=prompt,
        temperature=0.7,
    )

    parsed = extract_and_parse_json(raw_response)
    if "formatted_content" not in parsed:
        parsed["formatted_content"] = "Repurposed content unavailable."
    if "headline_or_title" not in parsed:
        parsed["headline_or_title"] = f"Repurposed for {target_format}"
    if "components" not in parsed:
        parsed["components"] = {}

    return parsed


def translate_content(
    text: str,
    target_language: str,
    source_language: str = "English",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Translate and transcreate text into one of the supported regional/global languages."""
    if not text or not text.strip():
        raise ValueError("Content text cannot be empty for translation.")

    client = get_genai_client(api_key)
    model_name = model or config.GEMINI_MODEL
    prompt = prompts.build_translation_prompt(
        text=text,
        target_language=target_language,
        source_language=source_language,
    )

    raw_response = _execute_prompt(
        client=client,
        model_name=model_name,
        system_instruction=prompts.TRANSLATION_SYSTEM_PROMPT,
        prompt=prompt,
        temperature=0.5,
    )

    parsed = extract_and_parse_json(raw_response)
    if "translated_text" not in parsed:
        parsed["translated_text"] = "Translation unavailable."
    if "target_language" not in parsed:
        parsed["target_language"] = target_language
    if "disclaimer" not in parsed:
        parsed["disclaimer"] = (
            "AI-generated translation preserving emotional nuance; human native review is recommended for formal publication."
        )

    return parsed


def evaluate_content(
    content_text: str,
    content_type: str = "General Content",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Evaluate content using standardized 5-pillar rubric (0-10 each, 0-100 overall)."""
    if not content_text or not content_text.strip():
        raise ValueError("Content text cannot be empty for evaluation.")

    client = get_genai_client(api_key)
    model_name = model or config.GEMINI_MODEL
    prompt = prompts.build_evaluator_prompt(
        content_text=content_text,
        content_type=content_type,
    )

    raw_response = _execute_prompt(
        client=client,
        model_name=model_name,
        system_instruction=prompts.EVALUATOR_SYSTEM_PROMPT,
        prompt=prompt,
        temperature=0.3,
    )

    parsed = extract_and_parse_json(raw_response)
    criteria = parsed.get("criteria_scores", {})
    clarity = float(criteria.get("clarity", 7.0))
    emotional = float(criteria.get("emotional_appeal", 7.0))
    relevance = float(criteria.get("audience_relevance", 7.0))
    originality = float(criteria.get("originality", 7.0))
    promo = float(criteria.get("promotional_effectiveness", 7.0))

    clarity = max(0.0, min(10.0, clarity))
    emotional = max(0.0, min(10.0, emotional))
    relevance = max(0.0, min(10.0, relevance))
    originality = max(0.0, min(10.0, originality))
    promo = max(0.0, min(10.0, promo))

    parsed["criteria_scores"] = {
        "clarity": clarity,
        "emotional_appeal": emotional,
        "audience_relevance": relevance,
        "originality": originality,
        "promotional_effectiveness": promo,
    }

    calculated_overall = round((clarity + emotional + relevance + originality + promo) * 2, 1)
    if "overall_score" not in parsed or not (0 <= float(parsed["overall_score"]) <= 100):
        parsed["overall_score"] = calculated_overall
    else:
        parsed["overall_score"] = round(float(parsed["overall_score"]), 1)

    if "strengths" not in parsed or not isinstance(parsed["strengths"], list):
        parsed["strengths"] = ["Strong thematic foundation."]
    if "weaknesses" not in parsed or not isinstance(parsed["weaknesses"], list):
        parsed["weaknesses"] = ["Could strengthen audience hook."]
    if "actionable_suggestions" not in parsed or not isinstance(parsed["actionable_suggestions"], list):
        parsed["actionable_suggestions"] = ["Sharpen the opening sentence to stop scrolling."]

    parsed["disclaimer"] = (
        "Scores are AI-generated heuristic estimates of craft quality, not guaranteed audience engagement predictions."
    )

    return parsed


def ab_hook_test(
    story_text: str,
    genre: str = "General",
    audience: str = "General Audience",
    tone: str = "Engaging",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate 3 distinct promotional hooks and evaluate them competitively."""
    if not story_text or not story_text.strip():
        raise ValueError("Story/script text cannot be empty.")

    client = get_genai_client(api_key)
    model_name = model or config.GEMINI_MODEL
    prompt = prompts.build_ab_hook_prompt(
        story_text=story_text,
        genre=genre,
        audience=audience,
        tone=tone,
    )

    raw_response = _execute_prompt(
        client=client,
        model_name=model_name,
        system_instruction=prompts.AB_HOOK_SYSTEM_PROMPT,
        prompt=prompt,
        temperature=0.7,
    )

    parsed = extract_and_parse_json(raw_response)
    hooks = parsed.get("hooks", [])
    if not isinstance(hooks, list):
        hooks = []

    for hook in hooks:
        scores = hook.get("scores", {})
        c = float(scores.get("clarity", 7.0))
        e = float(scores.get("emotional_appeal", 7.0))
        r = float(scores.get("audience_relevance", 7.0))
        o = float(scores.get("originality", 7.0))
        p = float(scores.get("promotional_effectiveness", 7.0))
        calc_score = round((c + e + r + o + p) * 2, 1)
        if "overall_score" not in hook or not hook["overall_score"]:
            hook["overall_score"] = calc_score
        else:
            hook["overall_score"] = round(float(hook["overall_score"]), 1)

    parsed["hooks"] = hooks

    if "winner" not in parsed or not parsed["winner"]:
        if hooks:
            best_hook = max(hooks, key=lambda h: h.get("overall_score", 0))
            parsed["winner"] = {
                "hook_id": best_hook.get("id", "A"),
                "hook_text": best_hook.get("hook_text", ""),
                "framework": best_hook.get("framework", "Curiosity"),
                "overall_score": best_hook.get("overall_score", 0),
                "winning_reason": "Highest cumulative score across rubric dimensions.",
            }

    parsed["disclaimer"] = (
        "Evaluations are algorithmic estimates based on structural craft benchmarks. "
        "Real-world click-through rates will vary by distribution channel and audience mood."
    )

    return parsed
