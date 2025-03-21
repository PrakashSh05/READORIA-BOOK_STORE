import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGODB_URI") 
    
    # Flask Configuration
    # Use a strong, consistent secret key for JWT tokens
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key") 
    DEBUG = os.getenv("DEBUG", "False").lower() == "true" 
    
    # File Upload Configuration
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size 

    APP_NAME = os.getenv("APP_NAME", "Readoria")
    APP_ENV = os.getenv("APP_ENV", "production")