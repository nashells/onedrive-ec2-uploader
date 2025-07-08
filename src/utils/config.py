import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    CLIENT_ID = os.getenv('CLIENT_ID')
    # デバイスコードフローではクライアントシークレットは不要
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')  # 互換性のため残す
    TENANT_ID = os.getenv('TENANT_ID', 'common')
    # デバイスコードフローではリダイレクトURIは不要
    REDIRECT_URI = None
    
    # EC2/サーバー環境用のスコープ設定（簡略化）
    SCOPE = ["Files.ReadWrite.All"]
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'onedrive_uploader.log')
    
    # 個人用アカウント向けのエンドポイントを使用
    AUTHORITY = "https://login.microsoftonline.com/consumers"
    GRAPH_API_ENDPOINT = "https://graph.microsoft.com/v1.0"
    
    @classmethod
    def validate(cls):
        if not cls.CLIENT_ID:
            raise ValueError("CLIENT_ID is not set in environment variables")
        if not cls.CLIENT_SECRET:
            raise ValueError("CLIENT_SECRET is not set in environment variables")
        return True