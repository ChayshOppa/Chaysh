import sqlite3
from typing import List, Dict, Optional
import json
from datetime import datetime
import logging

class Database:
    def __init__(self, db_path: str = "data/chaysh.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create search history table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            timestamp TIMESTAMP,
            results_count INTEGER,
            selected_result_url TEXT,
            ai_chat_initiated BOOLEAN DEFAULT 0
        )
        ''')

        # Create user interactions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_id INTEGER,
            action_type TEXT,
            target_url TEXT,
            timestamp TIMESTAMP,
            FOREIGN KEY (search_id) REFERENCES search_history (id)
        )
        ''')

        conn.commit()
        conn.close()

    def log_search(self, query: str, results_count: int) -> int:
        """Log a search query and return its ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
            INSERT INTO search_history (query, timestamp, results_count)
            VALUES (?, ?, ?)
            ''', (query, datetime.utcnow().isoformat(), results_count))

            search_id = cursor.lastrowid
            conn.commit()
            return search_id
        except Exception as e:
            logging.error(f"Error logging search: {str(e)}")
            return -1
        finally:
            conn.close()

    def log_interaction(self, search_id: int, action_type: str, target_url: str) -> bool:
        """Log a user interaction with a search result"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
            INSERT INTO user_interactions (search_id, action_type, target_url, timestamp)
            VALUES (?, ?, ?, ?)
            ''', (search_id, action_type, target_url, datetime.utcnow().isoformat()))

            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Error logging interaction: {str(e)}")
            return False
        finally:
            conn.close()

    def get_search_stats(self) -> Dict:
        """Get search statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get total searches
            cursor.execute('SELECT COUNT(*) FROM search_history')
            total_searches = cursor.fetchone()[0]

            # Get most common queries
            cursor.execute('''
            SELECT query, COUNT(*) as count 
            FROM search_history 
            GROUP BY query 
            ORDER BY count DESC 
            LIMIT 5
            ''')
            top_queries = [{'query': row[0], 'count': row[1]} for row in cursor.fetchall()]

            # Get AI chat conversion rate
            cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN ai_chat_initiated THEN 1 ELSE 0 END) as ai_chats
            FROM search_history
            ''')
            total, ai_chats = cursor.fetchone()
            ai_conversion_rate = (ai_chats / total * 100) if total > 0 else 0

            return {
                'total_searches': total_searches,
                'top_queries': top_queries,
                'ai_conversion_rate': ai_conversion_rate
            }
        except Exception as e:
            logging.error(f"Error getting search stats: {str(e)}")
            return {
                'total_searches': 0,
                'top_queries': [],
                'ai_conversion_rate': 0
            }
        finally:
            conn.close() 