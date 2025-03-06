import streamlit as st
import requests
import json
import os
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

def upload_pdf(file) -> Dict[str, Any]:
    """Upload and summarize a PDF file"""
    if file is None:
        st.error("Please upload a PDF file")
        return None
    
    files = {"file": file}
    session_id = st.session_state.get("session_id", None)
    
    data = {}
    if session_id:
        data["session_id"] = session_id
    
    with st.spinner("Uploading and summarizing PDF..."):
        response = requests.post(
            f"{API_URL}/summarize",
            files=files,
            data=data,
            headers=HEADERS
        )
    
    if response.status_code == 200:
        result = response.json()
        st.session_state["session_id"] = result["session_id"]
        return result
    elif response.status_code in [401, 403]:
        st.error("Authentication failed. Invalid API key.")
        return None
    else:
        st.error(f"Error: {response.text}")
        return None

def send_message(message: str) -> Optional[str]:
    """Send a message to the chatbot and get a response"""
    session_id = st.session_state.get("session_id", None)
    
    if not session_id:
        st.error("No active session. Please upload a PDF first.")
        return None
    
    data = {
        "session_id": session_id,
        "message": message
    }
    
    with st.spinner("Thinking..."):
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
        st.error(f"Error: {response.text}")
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
    """Get all chat sessions"""
    response = requests.get(
        f"{API_URL}/sessions",
        headers=HEADERS
    )
    
    if response.status_code == 200:
        return response.json()["sessions"]
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