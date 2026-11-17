"""
CreatorFlow Comprehensive Automated Test Suite.
Validates database schema, CRUD operations, prompt construction,
Gemini JSON extraction, error handling, and component imports.
"""

import unittest
from unittest import mock
import os
import tempfile
import json
import sqlite3

# Test imports
import config
import database
import prompts
import gemini_service


class TestCreatorFlow(unittest.TestCase):
    def setUp(self):
        """Set up an isolated temporary database for tests."""
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        database.DATABASE_FILE = self.temp_db_path
        database.init_db()

    def tearDown(self):
        """Clean up temporary database."""
        try:
            os.close(self.temp_db_fd)
            if os.path.exists(self.temp_db_path):
                os.remove(self.temp_db_path)
        except Exception:
            pass

    # ==========================================
    # 1. Database & CRUD Tests
    # ==========================================

    def test_database_initialization(self):
        """Verify database tables and indexes are created properly."""
        with database.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='content_items';"
            )
            table = cursor.fetchone()
            self.assertIsNotNone(table)
            self.assertEqual(table["name"], "content_items")

    def test_save_and_retrieve_content(self):
        """Verify saving and retrieving content records with parameterized queries."""
        cid = database.save_content(
            original_input="A story about an undercover detective.",
            generated_output="Title: The Phantom Shadow",
            content_type="title",
            language="English",
            evaluation_score=88.5,
            metadata={"angle": "Mystery"},
            is_saved=1,
        )
        self.assertTrue(cid.startswith("cf_"))

        item = database.get_content_by_id(cid)
        self.assertIsNotNone(item)
        self.assertEqual(item["content_id"], cid)
        self.assertEqual(item["content_type"], "title")
        self.assertEqual(item["evaluation_score"], 88.5)
        self.assertEqual(item["metadata"].get("angle"), "Mystery")

    def test_filter_and_search_content(self):
        """Verify search query and type filters."""
        database.save_content("Cyberpunk AI script", "Sci-Fi Hook 1", "hook", "English")
        database.save_content("Romantic comedy script", "Rom-Com Title", "title", "English")
        database.save_content("Hindi translated story", "कहानी अनुवाद", "translation", "Hindi")

        # Search by keyword
        res_search = database.get_content_items(search_query="Cyberpunk")
        self.assertEqual(len(res_search), 1)
        self.assertEqual(res_search[0]["content_type"], "hook")

        # Filter by content_type
        res_type = database.get_content_items(content_type="title")
        self.assertEqual(len(res_type), 1)

        # Filter by language
        res_lang = database.get_content_items(language="Hindi")
        self.assertEqual(len(res_lang), 1)

    def test_delete_content(self):
        """Verify deleting content items."""
        cid = database.save_content("Short script", "Video script", "repurpose_video_script")
        self.assertIsNotNone(database.get_content_by_id(cid))

        deleted = database.delete_content(cid)
        self.assertTrue(deleted)
        self.assertIsNone(database.get_content_by_id(cid))

    def test_dashboard_metrics(self):
        """Verify aggregate dashboard metrics come directly from SQLite."""
        database.save_content("Input 1", "Output 1", "title", "English", evaluation_score=90.0, is_saved=1)
        database.save_content("Input 2", "Output 2", "hook", "English", evaluation_score=80.0, is_saved=1)
        database.save_content("Input 3", "Output 3", "description", "Spanish", is_saved=0)

        metrics = database.get_dashboard_metrics()
        self.assertEqual(metrics["total_generated"], 3)
        self.assertEqual(metrics["total_saved"], 2)
        self.assertEqual(metrics["avg_evaluation_score"], 85.0)
        self.assertTrue(len(metrics["type_distribution"]) >= 3)
        self.assertTrue(len(metrics["recent_items"]) == 3)

    # ==========================================
    # 2. Prompt Builder Tests
    # ==========================================

    def test_prompt_builders(self):
        """Verify prompt templates correctly format input parameters."""
        p_studio = prompts.build_content_studio_prompt("My story", "Sci-Fi", "Gen Z", "English", "Dramatic")
        self.assertIn("My story", p_studio)
        self.assertIn("Sci-Fi", p_studio)
        self.assertIn("5 catchy, high-CTR titles", p_studio)

        p_repurpose = prompts.build_repurpose_prompt("My story", "repurpose_instagram", "Casual")
        self.assertIn("repurpose_instagram", p_repurpose)
        self.assertIn("Instagram caption", p_repurpose)

        p_trans = prompts.build_translation_prompt("Hello world", "Hindi")
        self.assertIn("Hindi", p_trans)
        self.assertIn("transcreate", p_trans.lower())

        p_eval = prompts.build_evaluator_prompt("Content to score", "Promotional Hook")
        self.assertIn("Clarity", p_eval)
        self.assertIn("Emotional Appeal", p_eval)

        p_ab = prompts.build_ab_hook_prompt("My story", "Thriller", "Creators", "Urgent")
        self.assertIn("Hook A", p_ab)
        self.assertIn("Hook B", p_ab)
        self.assertIn("Hook C", p_ab)

    # ==========================================
    # 3. Gemini Service Parsing & Error Tests
    # ==========================================

    def test_json_extraction_standard(self):
        """Verify standard JSON string parses correctly."""
        raw = '{"status": "ok", "count": 5}'
        parsed = gemini_service.extract_and_parse_json(raw)
        self.assertEqual(parsed["status"], "ok")
        self.assertEqual(parsed["count"], 5)

    def test_json_extraction_markdown_fences(self):
        """Verify extraction from markdown fenced code blocks."""
        raw = '```json\n{"titles": ["Title 1", "Title 2"]}\n```'
        parsed = gemini_service.extract_and_parse_json(raw)
        self.assertIn("titles", parsed)
        self.assertEqual(len(parsed["titles"]), 2)

    def test_missing_api_key_exception(self):
        """Verify GeminiConfigError is raised when no API key is provided."""
        old_config_key = config.GEMINI_API_KEY
        try:
            config.GEMINI_API_KEY = ""
            with unittest.mock.patch.dict(os.environ, {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""}, clear=True):
                with self.assertRaises(gemini_service.GeminiConfigError):
                    gemini_service.get_genai_client(api_key="")
        finally:
            config.GEMINI_API_KEY = old_config_key


if __name__ == "__main__":
    unittest.main()

