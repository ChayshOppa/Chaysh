import json
import os
from datetime import datetime
from pathlib import Path

class LocalStorage:
    def __init__(self):
        self.data_dir = Path("data")
        self.search_history_file = self.data_dir / "search_history.json"
        self.chat_history_file = self.data_dir / "chat_history.json"
        self.user_preferences_file = self.data_dir / "user_preferences.json"
        self._ensure_data_directory()
        self._initialize_files()

    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        self.data_dir.mkdir(exist_ok=True)

    def _initialize_files(self):
        """Initialize storage files with default structure if they don't exist"""
        if not self.search_history_file.exists():
            self._save_json(self.search_history_file, {"searches": []})
        
        if not self.chat_history_file.exists():
            self._save_json(self.chat_history_file, {"chats": []})
        
        if not self.user_preferences_file.exists():
            self._save_json(self.user_preferences_file, {
                "theme": "light",
                "language": "en",
                "recent_searches": [],
                "favorite_results": []
            })

    def _load_json(self, file_path):
        """Load JSON data from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_json(self, file_path, data):
        """Save JSON data to file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_search(self, query, results, language="en"):
        """Save a search query and its results"""
        data = self._load_json(self.search_history_file)
        search_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "language": language,
            "results_count": len(results),
            "results": results
        }
        data["searches"].append(search_entry)
        # Keep only last 100 searches
        data["searches"] = data["searches"][-100:]
        self._save_json(self.search_history_file, data)

    def save_chat(self, message, response, language="en"):
        """Save a chat message and response"""
        data = self._load_json(self.chat_history_file)
        chat_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": response,
            "language": language
        }
        data["chats"].append(chat_entry)
        # Keep only last 100 chats
        data["chats"] = data["chats"][-100:]
        self._save_json(self.chat_history_file, data)

    def update_preferences(self, preferences):
        """Update user preferences"""
        data = self._load_json(self.user_preferences_file)
        data.update(preferences)
        self._save_json(self.user_preferences_file, data)

    def get_preferences(self):
        """Get user preferences"""
        return self._load_json(self.user_preferences_file)

    def add_favorite_result(self, result):
        """Add a search result to favorites"""
        data = self._load_json(self.user_preferences_file)
        if "favorite_results" not in data:
            data["favorite_results"] = []
        data["favorite_results"].append({
            "timestamp": datetime.now().isoformat(),
            "result": result
        })
        # Keep only last 50 favorites
        data["favorite_results"] = data["favorite_results"][-50:]
        self._save_json(self.user_preferences_file, data)

    def get_search_history(self, limit=10):
        """Get recent search history"""
        data = self._load_json(self.search_history_file)
        return data.get("searches", [])[-limit:]

    def get_chat_history(self, limit=10):
        """Get recent chat history"""
        data = self._load_json(self.chat_history_file)
        return data.get("chats", [])[-limit:]

    def get_favorite_results(self):
        """Get favorite results"""
        data = self._load_json(self.user_preferences_file)
        return data.get("favorite_results", []) 