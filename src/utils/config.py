import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    TENANT_ID = os.getenv('TENANT_ID', 'common')
    REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:8000')
    SCOPE = os.getenv('SCOPE', 'Files.ReadWrite.All offline_access').split()
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'onedrive_uploader.log')
    
    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
    
    @classmethod
    def validate(cls):
        if not cls.CLIENT_ID:
            raise ValueError("CLIENT_ID is not set in environment variables")
        if not cls.CLIENT_SECRET:
            raise ValueError("CLIENT_SECRET is not set in environment variables")
        return True