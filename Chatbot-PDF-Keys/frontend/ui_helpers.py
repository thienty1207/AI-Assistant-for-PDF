import streamlit as st
import requests
import json
import os
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    st.error("API_KEY environment variable is not set")

# Headers for API requests
HEADERS = {"X-API-Key": API_KEY}

# Cache timeout in seconds
CACHE_TIMEOUT = 5  # 5 seconds

def upload_pdf(file) -> Dict[str, Any]:
    """Upload and summarize a PDF file"""
    files = {"file": file}
    
    response = requests.post(
        f"{API_URL}/summarize",
        files=files,
        headers=HEADERS
    )
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code in [401, 403]:
        st.error("Authentication failed. Invalid API key.")
        return None
    else:
        st.error(f"Error processing PDF: {response.text}")
        return None

def send_message(message: str) -> Optional[str]:
    """Send a message to the chatbot and get a response"""
    session_id = st.session_state.session_id
    
    if not session_id:
        st.error("No active session. Please upload a PDF first.")
        return None
    
    data = {
        "session_id": session_id,
        "message": message
    }
    
    response = requests.post(
        f"{API_URL}/chat",
        json=data,
        headers=HEADERS
    )
    
    if response.status_code == 200:
        return response.json()["response"]
    elif response.status_code in [401, 403]:
        st.error("Authentication failed. Invalid API key.")
        return None
    else:
        st.error(f"Error sending message: {response.text}")
        return None

def get_chat_history(session_id: str) -> List[Dict[str, Any]]:
    """Get chat history for a session"""
    response = requests.get(
        f"{API_URL}/history/{session_id}",
        headers=HEADERS
    )
    
    if response.status_code == 200:
        return response.json()["messages"]
    elif response.status_code in [401, 403]:
        st.error("Authentication failed. Invalid API key.")
        return []
    else:
        st.error(f"Error fetching chat history: {response.text}")
        return []

def get_all_sessions() -> List[Dict[str, Any]]:
    """Get all chat sessions with caching to reduce API calls"""
    # Initialize cache in session state if not already present
    if "sessions_cache" not in st.session_state:
        st.session_state.sessions_cache = None
    
    if "last_sessions_fetch" not in st.session_state:
        st.session_state.last_sessions_fetch = 0
    
    current_time = time.time()
    
    # Use cached data if available and not expired
    if (st.session_state.sessions_cache is not None and 
        current_time - st.session_state.last_sessions_fetch < CACHE_TIMEOUT):
        return st.session_state.sessions_cache
    
    # Otherwise, fetch new data
    response = requests.get(
        f"{API_URL}/sessions",
        headers=HEADERS
    )
    
    if response.status_code == 200:
        sessions = response.json()["sessions"]
        # Update cache
        st.session_state.sessions_cache = sessions
        st.session_state.last_sessions_fetch = current_time
        return sessions
    elif response.status_code in [401, 403]:
        st.error("Authentication failed. Invalid API key.")
        return []
    else:
        st.error(f"Error fetching sessions: {response.text}")
        return []

def display_message(role: str, content: str):
    """Display a chat message with appropriate styling"""
    if role == "user":
        st.markdown(f"**You:** {content}")
    else:
        st.markdown(f"**Assistant:** {content}") 