import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB Configuration
    MONGO_URI = "mongodb+srv://Prakash:prakash12345@prakash.ezlz0.mongodb.net/Readoria"
    
    # Flask Configuration
    # Use a strong, consistent secret key for JWT tokens
    SECRET_KEY = 'readoria-jwt-secret-key-f8e7d6c5b4a3'
    DEBUG = True
    
    # File Upload Configuration
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size 