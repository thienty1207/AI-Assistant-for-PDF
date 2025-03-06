import io
import PyPDF2
from langchain.llms import Ollama
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from typing import List, Dict, Any

class PDFSummarizer:
    def __init__(self, model_name="llama3.2:3b"):
        self.llm = Ollama(model=model_name)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text from PDF content"""
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    
    def split_text(self, text: str) -> List[Document]:
        """Split text into manageable chunks"""
        texts = self.text_splitter.split_text(text)
        return [Document(page_content=t) for t in texts]
    
    def summarize(self, pdf_content: bytes) -> str:
        """Generate a summary from PDF content"""
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_content)
        
        # Split text into chunks
        docs = self.split_text(text)
        
        # Load summarize chain
        chain = load_summarize_chain(self.llm, chain_type="map_reduce")
        
        # Generate summary
        summary = chain.run(docs)
        
        return summary
    
    def chat(self, query: str, context: str, chat_history: List[Dict[str, Any]]) -> str:
        """Generate a response to a query based on context and chat history"""
        # Format chat history
        formatted_history = ""
        for msg in chat_history:
            formatted_history += f"{msg['role']}: {msg['content']}\n"
        
        # Create prompt
        prompt = f"""
        You are a helpful assistant that answers questions about PDF documents.
        
        CONTEXT:
        {context}
        
        CHAT HISTORY:
        {formatted_history}
        
        USER QUERY:
        {query}
        
        Please provide a helpful, accurate, and concise response based on the context provided.
        """
        
        # Generate response
        response = self.llm.invoke(prompt)
        
        return response 