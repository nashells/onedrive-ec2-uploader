#!/usr/bin/env python3
"""
手動認証用サーバー（ブラウザが開かない環境用）
"""

import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import signal
import threading
import time

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.utils.config import Config
import msal

class ManualAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        auth_code = query_components.get('code', [None])[0]
        error = query_components.get('error', [None])[0]
        
        self.server.auth_code = auth_code
        self.server.error = error
        self.server.received = True
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        if error:
            message = f'''
            <html>
            <head><title>認証エラー</title></head>
            <body style="font-family: Arial, sans-serif; margin: 50px; text-align: center;">
                <h1 style="color: red;">認証エラー</h1>
                <p><strong>エラー:</strong> {error}</p>
                <p><strong>詳細:</strong> {query_components.get('error_description', [''])[0]}</p>
                <p>このウィンドウを閉じてください。</p>
            </body>
            </html>
            '''
        elif auth_code:
            message = '''
            <html>
            <head><title>認証成功</title></head>
            <body style="font-family: Arial, sans-serif; margin: 50px; text-align: center;">
                <h1 style="color: green;">✓ 認証成功</h1>
                <p>OneDriveへの認証が正常に完了しました！</p>
                <p>このウィンドウを閉じてください。</p>
                <p>ターミナルに戻って処理の続きをご確認ください。</p>
            </body>
            </html>
            '''
        else:
            message = '''
            <html>
            <head><title>認証待機中</title></head>
            <body style="font-family: Arial, sans-serif; margin: 50px; text-align: center;">
                <h1 style="color: blue;">認証待機中</h1>
                <p>認証が完了していません。</p>
                <p>認証URLから正しくリダイレクトされていることを確認してください。</p>
            </body>
            </html>
            '''
        
        self.wfile.write(message.encode('utf-8'))
    
    def log_message(self, format, *args):
        pass

def manual_auth_server():
    print("=== 手動認証サーバー ===")
    print()
    
    # MSALアプリケーションの作成
    app = msal.ConfidentialClientApplication(
        Config.CLIENT_ID,
        authority=Config.AUTHORITY,
        client_credential=Config.CLIENT_SECRET
    )
    
    # 認証URLの生成
    auth_url = app.get_authorization_request_url(
        scopes=Config.SCOPE,
        redirect_uri=Config.REDIRECT_URI
    )
    
    print("1. HTTPサーバーを localhost:8000 で起動しています...")
    
    server = HTTPServer(('localhost', 8000), ManualAuthHandler)
    server.auth_code = None
    server.error = None
    server.received = False
    
    print("✓ サーバーが起動しました")
    print()
    print("2. 以下のURLをブラウザで開いてください:")
    print("=" * 80)
    print(auth_url)
    print("=" * 80)
    print()
    print("3. 認証を完了してください...")
    print("4. Ctrl+C で終了できます")
    print()
    
    # サーバーを別スレッドで実行
    def run_server():
        while not server.received:
            server.handle_request()
    
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Ctrl+C のハンドリング
    def signal_handler(sig, frame):
        print("\n\nサーバーを停止します...")
        server.server_close()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # 認証コードを待機
        print("認証完了を待機中...")
        while not server.received:
            time.sleep(1)
        
        print("\n=== 認証結果 ===")
        
        if server.auth_code:
            print("✓ 認証コードを受信しました！")
            print(f"認証コード: {server.auth_code[:20]}...")
            
            # トークン取得
            print("\nアクセストークンを取得中...")
            result = app.acquire_token_by_authorization_code(
                code=server.auth_code,
                scopes=Config.SCOPE,
                redirect_uri=Config.REDIRECT_URI
            )
            
            if "access_token" in result:
                print("✓ アクセストークンの取得に成功しました！")
                
                # トークンキャッシュを保存
                from src.auth.authenticator import OneDriveAuthenticator
                auth = OneDriveAuthenticator()
                auth.app.token_cache.deserialize(result)
                auth._save_cache()
                
                print("✓ トークンキャッシュを保存しました")
                print("\n今後は 'python run.py' で自動ログインできます。")
                
            else:
                print("✗ アクセストークンの取得に失敗しました")
                print(f"エラー: {result}")
                
        elif server.error:
            print(f"✗ 認証エラー: {server.error}")
        else:
            print("✗ 認証コードが取得できませんでした")
    
    except KeyboardInterrupt:
        print("\n\nサーバーを停止しました")
    finally:
        server.server_close()

if __name__ == "__main__":
    manual_auth_server()