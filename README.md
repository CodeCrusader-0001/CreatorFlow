# CreatorFlow – AI-Powered Content Production & Optimization Platform

**CreatorFlow** is an enterprise-grade AI production assistant engineered for content creators, marketing teams, and digital storytelling businesses. It solves the realistic operational problem of repetitive manual repackaging, localization, and quality assurance by harnessing Google Gemini models to generate high-converting titles, descriptions, scroll-stopping hooks, multi-platform social repurposing, cultural transcreation, and objective rubric-based content evaluations.

---

## 1. Problem Statement & Business Objective

Modern digital storytelling and content marketing teams face immense operational drag:
- **Repetitive Platform Adaptation:** Manually reformatting a single narrative into native formats for Instagram, YouTube, short video scripts, and messaging channels takes hours.
- **Subjective Quality Control:** Teams lack a standardized, repeatable rubric to evaluate opening lines, emotional tension, clarity, and conversion potential before publishing.
- **Superficial Localization:** Standard automated translations produce robotic, literal phrasing that breaks narrative cadence, mistranslates cultural idioms, and destroys dramatic suspense.
- **Fragmented Asset Storage:** Generated titles, descriptions, and hooks are often lost across scattered notes and documents instead of being tracked in a structured production library.

**CreatorFlow solves this** with a unified, database-backed production platform driven directly by the official Google Gemini API SDK (`google-genai`).

---

## 2. Key Features

### 📊 1. Executive Content Dashboard
- **Live SQLite Analytics:** Dynamic metric cards for total generated assets, curated saved items, average quality score, and active platform formats.
- **Asset Distribution Chart:** Visual bar chart depicting breakdown of content types in your production catalog.
- **Recent Production Feed:** Chronological audit trail of recent generation runs with quality score badges.
- **⚡ Quick Launchers:** One-click shortcuts to seamlessly switch between studios.

### 🎨 2. Content Studio
- **Input Controls:** Narrative story/script text, genre, target audience, language, and tone.
- **Sample Scenario Loader:** 1-click loading of realistic sci-fi, business, and drama scenarios.
- **Triple Output Generation:**
  - **5 Catchy Titles:** Accompanied by strategic angle tags and target audience rationales.
  - **1 Engaging Description:** Comprehensive synopsis with key theme tags and targeted Call to Action.
  - **3 Promotional Hooks:** Scroll-stopping opening lines with psychological trigger classifications (Curiosity Gap, High Stakes, Provocative Question).
- **Individual Asset Controls:** Quick-copy code blocks and individual "Save to Library" actions, plus full bundle saving.

### 🔄 3. Repurpose Studio
- **Native Social Adaptations:**
  - **Instagram Caption:** Opening hook line, formatted micro-story, conversation starter, and 8-12 niche/trending hashtags.
  - **YouTube Description:** SEO-optimized video title, 2-paragraph overview, chapter timestamp placeholders, and search tags.
  - **Short Video Script (Reels / TikTok / Shorts):** Structured 30–60 second script broken down into `[Visual Cue]`, `[Voiceover / Audio]`, `[On-Screen Text]`, and pacing.
  - **WhatsApp Broadcast:** Formatted mobile message utilizing markdown bolding (`*headline*`), emojis, bulleted takeaways, and forwardable CTA.
- **Omnichannel Mode:** Option to generate single channel or batch all 4 formats simultaneously.
- **Tactical Production Tips:** Platform-specific recommendations for recording and scheduling.

### 🌐 4. Translation & Localization Studio
- **Supported Languages:** Hindi, English, Tamil, Telugu, Bengali, and Spanish.
- **Cultural Transcreation:** Preserves emotional cadence, narrative tension, character names, and cultural idioms rather than literal machine translation.
- **Transparent Disclaimer:** Clear advisory that outputs are heuristic transcreations and have not been verified by a certified human native speaker.
- **Regional Indian Bundle:** Option to generate Hindi, Tamil, Telugu, and Bengali in a single click.

### 📈 5. Content Evaluator & Quality Rubric
- **5-Pillar Standardized Rubric (0–10 each):**
  1. *Clarity & Readability*
  2. *Emotional Appeal & Tension*
  3. *Audience Relevance & Value*
  4. *Originality & Distinctive Voice*
  5. *Promotional / Conversion Pull*
- **Scoring Engine:** Calculates a balanced overall score from 0 to 100 with performance tier badges (*Exceptional*, *Strong Performer*, *Good Baseline*, *Needs Polish*).
- **In-Depth Qualitative Report:** Categorized strengths, areas of weakness, and numbered actionable editorial adjustments.
- **Algorithmic Notice:** Explains that scores are heuristic quality estimates, not guaranteed viral audience engagement predictions.

### ⚔️ 6. A/B Hook Testing Studio
- **Multi-Framework Generation:** Crafts 3 distinct hooks using competing psychological angles (Curiosity Gap vs. High Emotional Stakes vs. Provocative Agitation).
- **Competitive Rubric Benchmarking:** Evaluates all 3 candidates across all 5 criteria side-by-side.
- **Winner Spotlight:** Identifies the strongest candidate with structural rationale.
- **Comparative Scorecard:** Clean tabular matrix comparing candidate performance.
- **CTR Disclaimer:** Clearly notes that real-world engagement also relies on thumbnail design, distribution algorithms, and audience mood.

### 🗄️ 7. Content Library
- **SQLite-Backed Persistence:** Automatically stores `content_id`, `original_input`, `generated_output`, `content_type`, `language`, `evaluation_score`, `metadata_json`, and timestamps.
- **Full-Text Keyword Search:** Live query filtering across input text, output text, and metadata.
- **Multi-Dimensional Filters:** Filter by content type, target language, and saved status.
- **Deep Inspection Drawer:** Expand any item to inspect source input, generated output, metadata, or send directly to the Content Evaluator.
- **Data Export:** Instant download of filtered items as **CSV** (for spreadsheet analysis) or **TXT** (for production documentation).
- **Item Deletion:** Clean removal with confirmation feedback.

---

## 3. Technology Stack & Architecture

- **Web Frontend:** [Streamlit](https://streamlit.io/) (with custom CSS for modern enterprise dark navy SaaS aesthetic)
- **AI Core:** [Google Gemini API](https://ai.google.dev/) via the official `google-genai` SDK (`from google import genai`)
- **Database:** SQLite with Write-Ahead Logging (`PRAGMA journal_mode=WAL;`), parameterized queries, and indexing
- **Configuration:** Python `python-dotenv`
- **Data Processing:** Pandas (for analytics, tables, and CSV exports)

### Directory Structure

```text
CreatorFlow/
├── .env.example              # Template with environment placeholders
├── .gitignore                # Excludes secrets, databases, caches
├── requirements.txt          # Python dependencies
├── README.md                 # Complete documentation
├── app.py                    # Main Streamlit application entrypoint & routing
├── config.py                 # System configuration, constants, and options
├── database.py               # SQLite schema, migrations, and CRUD operations
├── prompts.py                # Structured system prompts and prompt builders
├── gemini_service.py         # Google GenAI client, timeouts, JSON parsing, errors
├── ui/
│   ├── __init__.py
│   ├── theme.py              # Dark navy SaaS CSS styling
│   ├── dashboard.py          # Dashboard view with stats and charts
│   ├── content_studio.py     # Titles, description, and hooks studio
│   ├── repurpose_studio.py   # Multi-platform repurposing studio
│   ├── translation_studio.py # Multilingual transcreation studio
│   ├── evaluator.py          # 5-Pillar rubric scoring view
│   ├── ab_testing.py         # Competitive A/B hook comparison view
│   └── library.py            # SQLite content library, search, export
└── tests/
    └── test_creatorflow.py   # Automated unit tests
```

---

## 4. Installation & Setup

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13
- Git

### Step 1: Clone or Navigate to the Repository
```bash
cd CreatorFlow
```

### Step 2: Create and Activate a Virtual Environment
**On Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 5. Google Gemini API Configuration

1. Obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/).
2. Create your `.env` configuration by copying `.env.example`:
   ```bash
   cp .env.example .env
   ```
   *(On Windows Command Prompt: `copy .env.example .env`)*
3. Open `.env` in any text editor and supply your key:
   ```ini
   GEMINI_API_KEY=AIzaSyYourActualKeyHere
   GEMINI_MODEL=gemini-2.5-flash
   GEMINI_REQUEST_TIMEOUT=60
   DATABASE_FILE=creatorflow.db
   ```

> **Note on Security & Fallback:** If the `GEMINI_API_KEY` is not present in `.env`, the application will still launch smoothly. You can enter an API key securely into the sidebar expander during the session. Keys are never logged, displayed in plain text, or committed to Git.

---

## 6. Execution Instructions

Launch the Streamlit dashboard by running:

```bash
streamlit run app.py
```

The application will automatically:
1. Initialize the SQLite database (`creatorflow.db`) with tables and indexes if not already present.
2. Load environment variables.
3. Apply the dark navy visual theme.
4. Launch the web interface at `http://localhost:8501`.

---

## 7. Running the Automated Test Suite

To verify database schema creation, CRUD operations, prompt engineering templates, JSON parsers, and error handling, run:

```bash
python -m unittest tests/test_creatorflow.py
```

---

## 8. Deployment Guidelines

### Option A: Streamlit Community Cloud
1. Push your repository to GitHub (ensure `.env` and `*.db` are in `.gitignore`).
2. Go to [share.streamlit.io](https://share.streamlit.io/) and select your repository.
3. In **App Settings > Secrets**, add:
   ```toml
   GEMINI_API_KEY = "AIzaSy..."
   GEMINI_MODEL = "gemini-2.5-flash"
   ```
4. Deploy the application.

### Option B: Docker Container
Create a `Dockerfile` in the project root:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```
Build and run:
```bash
docker build -t creatorflow .
docker run -p 8501:8501 -e GEMINI_API_KEY="your-key" creatorflow
```

---

## 9. Future Roadmap & Improvements

- [ ] **Direct Social Publishing:** OAuth integration with YouTube Data API and Instagram Graph API to publish approved drafts directly.
- [ ] **Voice Synthesis Preview:** Audio preview generation for short video scripts using Google Cloud Text-to-Speech.
- [ ] **Custom Rubric Builder:** Allow enterprise organizations to customize the 5-pillar evaluation rubric with proprietary company voice guidelines.
- [ ] **Team Workspaces & RBAC:** Multi-user authentication with team-based library sharing.

---

## 10. License

Developed for high-velocity creative and marketing teams. Built with Google Gemini and Streamlit.

