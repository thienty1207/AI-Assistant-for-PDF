from fastapi import HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable is not set")

# Define API key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    """Validate API key from request header"""
    if not api_key_header:
        raise HTTPException(
            status_code=401,
            detail="Missing API Key",
        )
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API Key",
        )
    return api_key_header 