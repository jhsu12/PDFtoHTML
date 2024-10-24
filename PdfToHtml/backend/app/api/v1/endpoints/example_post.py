import json
import logging
import os
import subprocess
from datetime import datetime
from typing import Callable

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ValidationError

from app.services.get_html import get_html

router = APIRouter()
logger = logging.getLogger(__name__)

class ExampleRequest(BaseModel):
    need: str  # This captures the user's need
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "need": "I want a simple HTML style"
                }
            ]
        }
    }

async def stream_response(request_data: str, func: Callable[[str], dict]):
    logger.info("Received request with data: %s", request_data)
    try:
        # Call the func and stream chunks
        async for chunk in func(request_data):
            yield f"data: {chunk}\n\n"
    except Exception as e:
        logger.error("Error during processing: %s", str(e))
        yield json.dumps({"error": str(e)}) + "\n"

async def handle_request(req: ExampleRequest, func: Callable[[str], dict]):
    logger.info("Received request with need: %s", req.need)
    try:
        if not req.need:
            logger.warning("Need cannot be empty")
            raise HTTPException(status_code=400, detail="Need cannot be empty")
        
        result = func(req.need)
        return {"results": result, "original": req.need}
    except ValidationError as e:
        logger.error("Validation error: %s", str(e))
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error("Error during processing: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/get-html/")
async def get_html_endpoint(
    need: str = Form(...),  # Accept need as form data
    file: UploadFile = File(...)
):
    logger.info(f"Received PDF file: {file.filename}")

    # Check the content type to ensure it's a PDF
    if not file.content_type == 'application/pdf':
        raise HTTPException(status_code=400, detail="File must be a PDF.")

   # Get current timestamp and format it
    current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Set the file name with the timestamp
    file_name = f"{current_timestamp}_{file.filename}"
    
    # Define the file path where the file will be saved
    file_path = f"./uploads/{file_name}"
    
    # Create the uploads directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Read the file contents and save it to the file path
    with open(file_path, "wb") as f:
        file_content = await file.read()
        f.write(file_content)
    
    logger.info(f"File saved as {file_path}")

    # Create an ExampleRequest object using the need parameter
    req = ExampleRequest(need=need)
    
    # Process the file content and the user's need (you may need to adjust get_html to accept the file path)
    result = await handle_request(req, lambda need: get_html(file_path, need))
    
    return result

@router.post("/deploy-hosting/")
async def deploy_hosting():
    # The directory where your Firebase project is located
    #project_dir = os.path.expanduser("~")

    try:
        # Change to the specified directory
        #os.chdir(project_dir)

        # Run the "firebase deploy --only hosting" command
        result = subprocess.run(["firebase", "deploy", "--only", "hosting"], capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode == 0:
            return {"message": "Deployment successful", "output": result.stdout}
        else:
            raise HTTPException(status_code=500, detail=f"Deployment failed: {result.stderr}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")
