from fastapi import FastAPI, HTTPException, Response
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import uvicorn
import os
import logging
import base64
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
from openai import OpenAI
import uuid
import json
from datetime import datetime

# /backend 
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# OpenAI client setup
openai_api_key = os.environ.get('OPENAI_API_KEY')
openai_client = OpenAI(api_key=openai_api_key)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create directory for storing generated images
IMAGES_DIR = ROOT_DIR / "generated_images"
IMAGES_DIR.mkdir(exist_ok=True)

class LogoRequest(BaseModel):
    prompt: str
    size: Optional[str] = "1024x1024"  # Default size

@app.get("/api")
async def root():
    return {"message": "Logo Creator API"}

@app.post("/api/generate-logo")
async def generate_logo(request: LogoRequest):
    try:
        logger.info(f"Generating logo with prompt: {request.prompt}")
        
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        # Call OpenAI API to generate image
        try:
            result = openai_client.images.generate(
                model="gpt-image-1",
                prompt=request.prompt,
                n=1,
                size=request.size
            )
            logger.info("OpenAI API call successful")
        except Exception as api_error:
            logger.error(f"OpenAI API error: {str(api_error)}")
            raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(api_error)}")
        
        # Get base64 encoded image directly
        image_base64 = result.data[0].b64_json
        logger.info("Base64 image data received successfully")
        
        # Convert to bytes
        image_bytes = base64.b64decode(image_base64)
        
        # Generate a unique filename
        filename = f"{uuid.uuid4()}.png"
        filepath = IMAGES_DIR / filename
        
        # Save the image to a file
        with open(filepath, "wb") as f:
            f.write(image_bytes)
        
        logger.info(f"Logo generated and saved as {filename}")
        
        # Store the reference in MongoDB
        await db.logos.insert_one({
            "id": str(uuid.uuid4()),
            "prompt": request.prompt,
            "filename": filename,
            "created_at": str(datetime.now())
        })
        
        # Return the base64 encoded image and filename
        return {
            "success": True,
            "image": image_base64,
            "filename": filename
        }
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error generating logo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/image/{filename}")
async def get_image(filename: str):
    filepath = IMAGES_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    with open(filepath, "rb") as f:
        image_bytes = f.read()
    
    return Response(content=image_bytes, media_type="image/png")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)
