"""
CreatorFlow Gemini Service Module Proxy.
Re-exports the core service from services.gemini_service for backward compatibility.
"""

from services.gemini_service import (
    GeminiServiceException,
    GeminiConfigError,
    GeminiSSLError,
    GeminiConnectionError,
    GeminiQuotaError,
    GeminiModelUnavailableError,
    GeminiAPIError,
    GeminiResponseParsingError,
    get_effective_api_key,
    is_api_configured,
    extract_and_parse_json,
    get_genai_client,
    generate_content_studio,
    repurpose_content,
    translate_content,
    evaluate_content,
    ab_hook_test,
)
