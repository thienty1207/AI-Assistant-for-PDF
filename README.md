# AI-Assistant-for-PDF
Sumarization and chat with AI through PDF we provided



## Overview 
This document describes the development of a chatbot capable of summarizing PDF files after they are 
uploaded. The chatbot will maintain conversation history and utilize various frameworks and models to 
provide efficient responses. 

## Technology Stack 
• Backend: FastAPI (for API development) 
• Database: SQLite (to store chat history) 
• LLM Framework: LangChain (to manage interactions with the language model) 
• Model: Ollama (running locally) using deepseek-r1:8b 
• Frontend: Streamlit (for user interaction and file upload) 

## Project Structure 
project_root/ 
│-- backend/ 
│   │-- main.py  # FastAPI application 
│   │-- db.py  # SQLite database setup 
│   │-- summarizer.py  # PDF processing and summarization logic 
│   │-- models.py  # Database models and schemas 
│   └-- requirements.txt  # Backend dependencies 
│ 
│-- frontend/ 
│   │-- app.py  # Streamlit application 
│   │-- ui_helpers.py  # Helper functions for UI components 
│   └-- requirements.txt  # Frontend dependencies 
│ 
└-- README.md  # Project documentation 

## Functionality 
1. Upload a PDF File  
o The user uploads a PDF file via the Streamlit frontend. 
o The file is sent to the backend for processing. 
2. Summarization  
o The backend extracts text from the PDF. 
o LangChain interacts with deepseek-r1:8b (via Ollama) to generate a summary. 
3. Chat with History  
o Users can ask questions about the uploaded document. 
o The chatbot maintains conversation history using SQLite. 
4. User Interface  
o Streamlit provides an intuitive UI for file uploads and chat interactions. 

## Next Steps 
• Implement backend API with FastAPI to handle file uploads and processing. 
• Integrate LangChain with deepseek-r1:8b via Ollama. 
• Develop frontend using Streamlit for seamless user experience. 
• Store and retrieve chat history using SQLite. 
This project aims to provide an efficient and locally hosted chatbot that can summarize PDFs and 
maintain conversation history using cutting-edge AI models and frameworks. 