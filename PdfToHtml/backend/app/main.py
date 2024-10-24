import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router  # Import the combined router from router.py
from app.configs.config import get_config
from app.configs.logging_config import setup_logging

# Load environment variables from the .env file
load_dotenv()

# Configure logging
setup_logging()

# Get the configuration based on the environment
config = get_config()
ALLOW_ORIGINS = f"\"{config.ALLOW_ORIGINS}\""



# Create FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,  # Adjust this to specify allowed origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Adjust this to specify allowed methods
    allow_headers=["*"],  # Adjust this to specify allowed headers
)

# Include the API router with a prefix
app.include_router(api_router, prefix="/api/v1")

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=config.DEBUG)
