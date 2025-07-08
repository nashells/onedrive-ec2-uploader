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
        error = query_components.get('error', [None])[0]
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        if error:
            message = f'''
            <html>
            <head><title>認証エラー</title></head>
            <body style="font-family: Arial, sans-serif; margin: 50px; text-align: center;">
                <h1 style="color: red;">認証エラー</h1>
                <p>エラー: {error}</p>
                <p>エラーの詳細: {query_components.get('error_description', [''])[0]}</p>
                <p>このウィンドウを閉じて、もう一度お試しください。</p>
            </body>
            </html>
            '''
        elif self.server.auth_code:
            message = '''
            <html>
            <head><title>認証成功</title></head>
            <body style="font-family: Arial, sans-serif; margin: 50px; text-align: center;">
                <h1 style="color: green;">✓ 認証成功</h1>
                <p>OneDriveへの認証が正常に完了しました。</p>
                <p>このウィンドウを閉じてください。</p>
                <p>ターミナルに戻って処理の続きをご確認ください。</p>
            </body>
            </html>
            '''
        else:
            message = '''
            <html>
            <head><title>認証失敗</title></head>
            <body style="font-family: Arial, sans-serif; margin: 50px; text-align: center;">
                <h1 style="color: orange;">認証失敗</h1>
                <p>認証コードが取得できませんでした。</p>
                <p>このウィンドウを閉じて、もう一度お試しください。</p>
            </body>
            </html>
            '''
        
        self.wfile.write(message.encode('utf-8'))
    
    def log_message(self, format, *args):
        # サーバーのログ出力を無効化
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
        
        # EC2環境用にPublicClientApplicationを使用（デバイスコードフロー）
        app = msal.PublicClientApplication(
            self.config.CLIENT_ID,
            authority=self.config.AUTHORITY,
            token_cache=cache
        )
        return app
    
    def _save_cache(self):
        try:
            # MSALのバージョンに応じてキャッシュを保存
            if hasattr(self.app.token_cache, 'has_state_changed') and self.app.token_cache.has_state_changed:
                with open(self.token_cache_file, 'w') as f:
                    if hasattr(self.app.token_cache, 'serialize'):
                        f.write(self.app.token_cache.serialize())
                    else:
                        import json
                        json.dump(self.app.token_cache._cache, f)
            elif not hasattr(self.app.token_cache, 'has_state_changed'):
                # 古いバージョンの場合は常に保存
                with open(self.token_cache_file, 'w') as f:
                    import json
                    json.dump(self.app.token_cache._cache, f)
        except Exception as e:
            print(f"⚠️ トークンキャッシュの保存に失敗: {e}")
            print("認証は成功していますが、次回は再認証が必要になる可能性があります")
    
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
        # デバイスコードフローを使用（EC2環境に最適）
        print("認証を開始します...")
        print("デバイスコードフローを使用します（EC2/サーバー環境用）")
        
        flow = self.app.initiate_device_flow(scopes=self.config.SCOPE)
        
        if "user_code" not in flow:
            raise Exception("デバイスフローの初期化に失敗しました")
        
        print("\n" + "="*60)
        print("🔐 Microsoft OneDrive 認証")
        print("="*60)
        print(f"1. 任意のデバイスのブラウザで以下のURLを開いてください:")
        print(f"   {flow['verification_uri']}")
        print(f"")
        print(f"2. 表示された画面で以下のコードを入力してください:")
        print(f"   📋 コード: {flow['user_code']}")
        print(f"")
        print(f"3. Microsoftアカウントでログインしてください")
        print(f"")
        print(f"⏳ 認証完了を待機中... (最大 {flow.get('expires_in', 900)} 秒)")
        print("="*60)
        
        result = self.app.acquire_token_by_device_flow(flow)
        
        if "error" in result:
            raise Exception(f"トークン取得エラー: {result.get('error_description', result.get('error'))}")
        
        print("✅ 認証が正常に完了しました!")
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