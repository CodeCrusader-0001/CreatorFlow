"""
CreatorFlow Configuration Module.
Handles environment variables, default constants, and system settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
GEMINI_REQUEST_TIMEOUT = int(os.getenv("GEMINI_REQUEST_TIMEOUT", "60000"))

# Database Configuration
DATABASE_FILE = os.getenv("DATABASE_FILE", str(BASE_DIR / "creatorflow.db"))

# Application Metadata
APP_NAME = "CreatorFlow"
APP_TAGLINE = "AI-Powered Content Production & Optimization Platform"
APP_VERSION = "1.0.0"

# Supported Options
SUPPORTED_LANGUAGES = [
    "English",
    "Hindi",
    "Tamil",
    "Telugu",
    "Bengali",
    "Spanish",
]

GENRES = [
    "Tech & Innovation",
    "Business & Finance",
    "Digital Storytelling",
    "Fiction & Drama",
    "Thriller & Mystery",
    "Comedy & Satire",
    "True Crime",
    "Self-Improvement & Productivity",
    "Documentary & Culture",
    "Lifestyle & Travel",
]

AUDIENCES = [
    "Content Creators & Influencers",
    "Marketing & Growth Teams",
    "Working Professionals",
    "Tech Enthusiasts & Developers",
    "Gen Z & Trend Followers",
    "Entrepreneurs & Founders",
    "General Public / Mass Audience",
]

TONES = [
    "Dramatic & High-Stakes",
    "Inspiring & Motivational",
    "Casual & Conversational",
    "Authoritative & Educational",
    "Humorous & Witty",
    "Suspenseful & Intriguing",
    "Urgent & Direct",
    "Empathetic & Warm",
]

REPURPOSE_FORMATS = {
    "Instagram Caption": "repurpose_instagram",
    "YouTube Description": "repurpose_youtube",
    "Short Video Script (Reels/TikTok/Shorts)": "repurpose_video_script",
    "WhatsApp Promotional Message": "repurpose_whatsapp",
}

CONTENT_TYPES = [
    "All",
    "content_studio_bundle",
    "title",
    "description",
    "hook",
    "repurpose_instagram",
    "repurpose_youtube",
    "repurpose_video_script",
    "repurpose_whatsapp",
    "translation",
    "evaluation",
    "ab_hook_test",
]

