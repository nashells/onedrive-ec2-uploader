#!/usr/bin/env python3
"""
シンプルな認証サーバー
"""

import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import socketserver

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.utils.config import Config
import msal

class SimpleAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"リクエスト受信: {self.path}")
        
        query_components = parse_qs(urlparse(self.path).query)
        auth_code = query_components.get('code', [None])[0]
        error = query_components.get('error', [None])[0]
        
        print(f"認証コード: {auth_code}")
        print(f"エラー: {error}")
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        if auth_code:
            message = '''
            <html>
            <head><title>認証成功!</title></head>
            <body style="font-family: Arial, sans-serif; margin: 50px; text-align: center; background-color: #f0f8ff;">
                <h1 style="color: green;">🎉 認証成功!</h1>
                <p style="font-size: 18px;">OneDriveへの認証が正常に完了しました!</p>
                <p>このウィンドウを閉じて、ターミナルに戻ってください。</p>
                <div style="margin-top: 30px; padding: 20px; background-color: #e8f5e8; border-radius: 10px;">
                    <p><strong>次の手順:</strong></p>
                    <p>1. このブラウザタブを閉じる</p>
                    <p>2. ターミナルでプロセスを完了する</p>
                </div>
            </body>
            </html>
            '''
            
            # トークン取得を試行
            print("\nアクセストークンを取得中...")
            
            app = msal.ConfidentialClientApplication(
                Config.CLIENT_ID,
                authority=Config.AUTHORITY,
                client_credential=Config.CLIENT_SECRET
            )
            
            result = app.acquire_token_by_authorization_code(
                code=auth_code,
                scopes=Config.SCOPE,
                redirect_uri=Config.REDIRECT_URI
            )
            
            if "access_token" in result:
                print("✅ アクセストークンの取得に成功!")
                
                # トークンキャッシュを保存
                import json
                with open('token_cache.json', 'w') as f:
                    json.dump(app.token_cache.serialize(), f)
                
                print("✅ トークンキャッシュを保存しました")
                print("\n🎉 認証完了! 今後は自動ログインできます。")
                print("このサーバーを停止するには Ctrl+C を押してください。")
                
            else:
                print("❌ アクセストークンの取得に失敗")
                print(f"エラー: {result}")
                
        elif error:
            message = f'''
            <html>
            <head><title>認証エラー</title></head>
            <body style="font-family: Arial, sans-serif; margin: 50px; text-align: center; background-color: #fff8f8;">
                <h1 style="color: red;">❌ 認証エラー</h1>
                <p><strong>エラー:</strong> {error}</p>
                <p><strong>詳細:</strong> {query_components.get('error_description', [''])[0]}</p>
                <p>このウィンドウを閉じて、もう一度お試しください。</p>
            </body>
            </html>
            '''
            print(f"❌ 認証エラー: {error}")
            
        else:
            message = '''
            <html>
            <head><title>OneDrive認証サーバー</title></head>
            <body style="font-family: Arial, sans-serif; margin: 50px; text-align: center;">
                <h1>OneDrive認証サーバー</h1>
                <p>このサーバーは認証用です。</p>
                <p>認証URLから正しくリダイレクトされると、認証コードを受信します。</p>
            </body>
            </html>
            '''
        
        self.wfile.write(message.encode('utf-8'))
    
    def log_message(self, format, *args):
        return  # ログを無効化

def start_auth_server():
    print("🚀 OneDrive認証サーバーを起動しています...")
    print()
    
    # 認証URLを生成
    app = msal.ConfidentialClientApplication(
        Config.CLIENT_ID,
        authority=Config.AUTHORITY,
        client_credential=Config.CLIENT_SECRET
    )
    
    auth_url = app.get_authorization_request_url(
        scopes=Config.SCOPE,
        redirect_uri=Config.REDIRECT_URI
    )
    
    print("✅ サーバーが http://localhost:8000 で起動しました")
    print()
    print("📋 以下のURLをブラウザで開いて認証を完了してください:")
    print("=" * 100)
    print(auth_url)
    print("=" * 100)
    print()
    print("⏳ 認証完了を待機中... (Ctrl+C で停止)")
    print()
    
    try:
        with HTTPServer(('localhost', 8000), SimpleAuthHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 サーバーを停止しました")

if __name__ == "__main__":
    start_auth_server()