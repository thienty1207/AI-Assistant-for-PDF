import sqlite3
import os
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ChatDatabase:
    def __init__(self, db_path=None):
        # Use environment variable for database path if not specified
        self.db_path = db_path or os.getenv("DATABASE_PATH", "chat_history.db")
        self._create_tables()
    
    def _create_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create sessions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            pdf_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create messages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (session_id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_session(self, session_id: str, pdf_name: Optional[str] = None) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sessions (session_id, pdf_name) VALUES (?, ?)",
                (session_id, pdf_name)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Session already exists
            return False
    
    def add_message(self, session_id: str, role: str, content: str) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding message: {e}")
            return False
    
    def get_session_messages(self, session_id: str) -> List[dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp",
            (session_id,)
        )
        
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return messages
    
    def get_all_sessions(self) -> List[dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT session_id, pdf_name, created_at FROM sessions ORDER BY created_at DESC"
        )
        
        sessions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return sessions 