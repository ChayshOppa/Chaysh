# Chaysh Project Przypominajka (Backup/Reminder)

**This is a private backup and progress log for Chaysh. Update this file after every major, stable milestone. Use it as a reminder and rollback point if new changes break the project.**

---

## Current State (as of March 2024)

- **OpenRouter Integration**: Successfully integrated with OpenRouter API for AI-powered responses
- **Language Support**: Full bilingual support (English/Polish) implemented across:
  - AI responses
  - UI elements
  - Suggestions
  - Error messages
- **Response Format**: Standardized JSON structure for all responses:
  ```json
  {
    "name": "query",
    "description": [
      "basic_info",
      "detailed_info",
      "product_info",
      "summary"
    ],
    "source_info": "source information",
    "suggestions": [
      {"text": "suggestion text", "category": "category"},
      ...
    ],
    "actions": [
      {"type": "chat", "label": "Chaysh Assistant", "query": "query"}
    ]
  }
  ```
- **Error Handling**: Robust error handling for:
  - API key issues
  - Network problems
  - Invalid responses
  - JSON parsing errors
- **Logging**: Comprehensive logging system for:
  - API requests/responses
  - Error tracking
  - Debug information
  - User interactions

---

## Core Components

### 1. OpenRouter Integration (`src/core/crawler.py`)
- Structured prompts for consistent responses
- Language-aware response generation
- Character limits and formatting rules
- Error handling and fallbacks

### 2. Language Support
- Dynamic language switching
- Bilingual suggestions
- Translated UI elements
- Language-specific error messages

### 3. Response Processing
- JSON validation
- Response formatting
- Error recovery
- Fallback responses

---

## How to Use This File
- Update after every major, stable change
- Use as reference for last known good state
- Revert to this state if new changes break functionality
- Only update when new state is verified stable

---

## Backup Instructions
1. Keep a copy of all core files:
   - `src/core/crawler.py`
   - `src/core/assistant.py`
   - `src/core/config.py`
   - `src/templates/home.html`
   - `.env` (with API keys)
2. Document any API key changes
3. Test language switching after updates
4. Verify response format consistency

---

## [2024-05] AI Assistant Milestone
- OpenRouter-powered AI assistant fully operational.
- Bilingual (EN/PL) support for UI, suggestions, and AI answers.
- Unified, validated JSON response structure for all assistant replies.
- Error handling covers API key, network, and response format issues.
- Modern, responsive chat UI with persistent language switching.
- All legacy/manual/manual scraping code removed; AI-only logic.
- Light/dark mode UI separation for chat area in progress.

**Next time you say 'update przypominajka', I will add a new entry here with the latest stable progress.** 