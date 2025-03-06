from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
import base64
import uuid
import os
import time
from typing import Optional, Dict
from dotenv import load_dotenv

from db import ChatDatabase
from models import ChatHistory, SummarizeRequest, ChatRequest
from summarizer import PDFSummarizer
from auth import get_api_key

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database and summarizer
db = ChatDatabase()
summarizer = PDFSummarizer()

# Store PDF summaries in memory for quick access
pdf_summaries = {}

# Simple in-memory cache for sessions endpoint
sessions_cache = {
    "data": None,
    "timestamp": 0
}
CACHE_TIMEOUT = 5  # 5 seconds

@app.post("/summarize")
async def summarize_pdf(
    file: UploadFile = File(...), 
    session_id: Optional[str] = Form(None),
    api_key: str = Depends(get_api_key)
):
    """
    Upload and summarize a PDF file
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Read file content
    content = await file.read()
    
    # Generate session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Create session in database
    db.create_session(session_id, file.filename)
    
    try:
        # Generate summary
        summary = summarizer.summarize(content)
        
        # Store summary for future reference
        pdf_summaries[session_id] = {
            "text": summarizer.extract_text_from_pdf(content),
            "summary": summary
        }
        
        # Add summary as first message in chat
        db.add_message(session_id, "assistant", f"PDF Summary: {summary}")
        
        return {
            "session_id": session_id,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/chat")
async def chat(
    request: ChatRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Chat with the bot about a previously uploaded PDF
    """
    session_id = request.session_id
    user_message = request.message
    
    # Check if session exists
    if session_id not in pdf_summaries:
        raise HTTPException(status_code=404, detail="Session not found. Please upload a PDF first.")
    
    # Add user message to history
    db.add_message(session_id, "user", user_message)
    
    # Get chat history
    chat_history = db.get_session_messages(session_id)
    
    # Generate response
    context = pdf_summaries[session_id]["text"]
    response = summarizer.chat(user_message, context, chat_history)
    
    # Add assistant response to history
    db.add_message(session_id, "assistant", response)
    
    return {
        "response": response
    }

@app.get("/sessions")
async def get_sessions(api_key: str = Depends(get_api_key), request: Request = None):
    """
    Get all chat sessions with caching to reduce database load
    """
    current_time = time.time()
    
    # Return cached data if it's still fresh
    if sessions_cache["data"] and current_time - sessions_cache["timestamp"] < CACHE_TIMEOUT:
        return sessions_cache["data"]
    
    # Otherwise, fetch from database
    sessions = db.get_all_sessions()
    result = {"sessions": sessions}
    
    # Update cache
    sessions_cache["data"] = result
    sessions_cache["timestamp"] = current_time
    
    return result

@app.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    api_key: str = Depends(get_api_key)
):
    """
    Get chat history for a specific session
    """
    messages = db.get_session_messages(session_id)
    return {"session_id": session_id, "messages": messages}

@app.get("/reload_session/{session_id}")
async def reload_session(
    session_id: str,
    api_key: str = Depends(get_api_key)
):
    """
    Reload a session's PDF data into memory
    """
    # Check if session exists in database
    sessions = db.get_all_sessions()
    session = next((s for s in sessions if s["session_id"] == session_id), None)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found in database")
    
    # Get chat history to find the summary
    messages = db.get_session_messages(session_id)
    
    # Find the summary message (first assistant message)
    summary = None
    for msg in messages:
        if msg["role"] == "assistant" and "PDF Summary:" in msg["content"]:
            summary = msg["content"].replace("PDF Summary: ", "")
            break
    
    if not summary:
        raise HTTPException(status_code=404, detail="Could not find PDF summary in chat history")
    
    # Add to pdf_summaries with empty text (we don't have the original text anymore)
    # This is enough to allow chat to work
    pdf_summaries[session_id] = {
        "text": "PDF text not available for reloaded sessions",
        "summary": summary
    }
    
    return {"success": True, "session_id": session_id} 