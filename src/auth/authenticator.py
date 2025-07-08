import os
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import msal
import sys

# プロジェクトルートをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.config import Config


class AuthCodeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        self.server.auth_code = query_components.get('code', [None])[0]
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        if self.server.auth_code:
            message = '<h1>認証成功</h1><p>このウィンドウを閉じてください。</p>'
        else:
            message = '<h1>認証失敗</h1><p>認証コードが取得できませんでした。</p>'
        
        self.wfile.write(message.encode())
    
    def log_message(self, format, *args):
        pass


class OneDriveAuthenticator:
    def __init__(self):
        self.config = Config
        self.token_cache_file = "token_cache.json"
        self.app = self._create_msal_app()
    
    def _create_msal_app(self):
        cache = msal.SerializableTokenCache()
        if os.path.exists(self.token_cache_file):
            with open(self.token_cache_file, 'r') as f:
                cache.deserialize(f.read())
        
        # 個人用アカウント用のConfidentialClientApplicationを使用
        app = msal.ConfidentialClientApplication(
            self.config.CLIENT_ID,
            authority=self.config.AUTHORITY,
            client_credential=self.config.CLIENT_SECRET,
            token_cache=cache
        )
        return app
    
    def _save_cache(self):
        if self.app.token_cache.has_state_changed:
            with open(self.token_cache_file, 'w') as f:
                f.write(self.app.token_cache.serialize())
    
    def get_token(self):
        accounts = self.app.get_accounts()
        
        if accounts:
            result = self.app.acquire_token_silent(
                scopes=self.config.SCOPE,
                account=accounts[0]
            )
            if result and "access_token" in result:
                self._save_cache()
                return result
        
        return self._get_token_interactive()
    
    def _get_token_interactive(self):
        auth_url = self.app.get_authorization_request_url(
            scopes=self.config.SCOPE,
            redirect_uri=self.config.REDIRECT_URI
        )
        
        print(f"ブラウザで以下のURLを開いて認証してください:\n{auth_url}")
        webbrowser.open(auth_url)
        
        server = HTTPServer(('localhost', 8000), AuthCodeHandler)
        server.auth_code = None
        server.handle_request()
        
        if not server.auth_code:
            raise Exception("認証コードの取得に失敗しました")
        
        result = self.app.acquire_token_by_authorization_code(
            code=server.auth_code,
            scopes=self.config.SCOPE,
            redirect_uri=self.config.REDIRECT_URI
        )
        
        if "error" in result:
            raise Exception(f"トークン取得エラー: {result.get('error_description', result.get('error'))}")
        
        self._save_cache()
        return result
    
    def refresh_token(self):
        accounts = self.app.get_accounts()
        if not accounts:
            return self._get_token_interactive()
        
        result = self.app.acquire_token_silent(
            scopes=self.config.SCOPE,
            account=accounts[0]
        )
        
        if result and "access_token" in result:
            self._save_cache()
            return result
        
        return self._get_token_interactive()