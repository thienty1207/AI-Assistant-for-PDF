import streamlit as st
import time
import os
from dotenv import load_dotenv
from ui_helpers import upload_pdf, send_message, get_chat_history, get_all_sessions, display_message, reload_session

# Load environment variables
load_dotenv()

# Check if API key is set
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    st.error("API_KEY environment variable is not set. Please configure your .env file.")
    st.stop()

st.set_page_config(
    page_title="Ho Thien Ty AI Assistant",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = None

# App title
st.title("Ho Thien Ty AI Assistant")

# Sidebar for PDF upload and session management
with st.sidebar:
    st.header("Upload PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        if st.button("Process PDF"):
            result = upload_pdf(uploaded_file)
            if result:
                st.success(f"PDF processed successfully!")
                st.session_state.messages = []  # Clear messages for new PDF
                
                # Add summary as first message
                st.session_state.messages.append({"role": "assistant", "content": f"PDF Summary: {result['summary']}"})
    
    st.divider()
    
    # Session management
    st.header("Previous Sessions")
    
    # Get sessions (will use cache if available)
    sessions = get_all_sessions()
    
    if sessions:
        selected_session = st.selectbox(
            "Select a previous session",
            options=[f"{s['pdf_name']} ({s['session_id'][:8]}...)" for s in sessions],
            format_func=lambda x: x
        )
        
        if st.button("Load Session"):
            # Extract session_id from the selected option
            selected_idx = [f"{s['pdf_name']} ({s['session_id'][:8]}...)" for s in sessions].index(selected_session)
            session_id = sessions[selected_idx]["session_id"]
            
            # Reload session on backend
            if reload_session(session_id):
                # Set session_id and load messages
                st.session_state.session_id = session_id
                history = get_chat_history(session_id)
                st.session_state.messages = history
                st.success(f"Loaded session: {sessions[selected_idx]['pdf_name']}")
                st.rerun()

# Main chat interface
st.subheader("Chat")

# Display chat messages
for message in st.session_state.messages:
    display_message(message["role"], message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Get AI response
    response = send_message(user_input)
    
    if response:
        # Add AI response to chat
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()  # Rerun to display the new messages

# Footer
st.divider()
st.caption("Ho Thien Ty AI Assistant using FastAPI, LangChain, and Ollama") 