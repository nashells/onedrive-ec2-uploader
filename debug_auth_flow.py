#!/usr/bin/env python3
"""
認証フローのデバッグ用スクリプト
"""

import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.utils.config import Config
import msal

class DebugAuthCodeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"\n=== HTTPリクエスト受信 ===")
        print(f"パス: {self.path}")
        
        query_components = parse_qs(urlparse(self.path).query)
        print(f"クエリパラメータ: {query_components}")
        
        auth_code = query_components.get('code', [None])[0]
        error = query_components.get('error', [None])[0]
        
        print(f"認証コード: {auth_code}")
        print(f"エラー: {error}")
        
        if error:
            print(f"エラーの詳細: {query_components.get('error_description', [''])}")
        
        self.server.auth_code = auth_code
        self.server.error = error
        self.server.query_params = query_components
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        if error:
            message = f'''
            <html>
            <head><title>認証エラー - デバッグ情報</title></head>
            <body style="font-family: Arial, sans-serif; margin: 50px;">
                <h1 style="color: red;">認証エラー</h1>
                <p><strong>エラー:</strong> {error}</p>
                <p><strong>詳細:</strong> {query_components.get('error_description', [''])[0]}</p>
                <h2>デバッグ情報</h2>
                <p><strong>完全なURL:</strong> {self.path}</p>
                <p><strong>クエリパラメータ:</strong> {query_components}</p>
                <p>このウィンドウを閉じて、ターミナルのデバッグ情報を確認してください。</p>
            </body>
            </html>
            '''
        elif auth_code:
            message = f'''
            <html>
            <head><title>認証成功 - デバッグ情報</title></head>
            <body style="font-family: Arial, sans-serif; margin: 50px;">
                <h1 style="color: green;">✓ 認証成功</h1>
                <p><strong>認証コード:</strong> {auth_code}</p>
                <h2>デバッグ情報</h2>
                <p><strong>完全なURL:</strong> {self.path}</p>
                <p><strong>クエリパラメータ:</strong> {query_components}</p>
                <p>このウィンドウを閉じてください。処理を続行します。</p>
            </body>
            </html>
            '''
        else:
            message = f'''
            <html>
            <head><title>認証失敗 - デバッグ情報</title></head>
            <body style="font-family: Arial, sans-serif; margin: 50px;">
                <h1 style="color: orange;">認証失敗</h1>
                <p>認証コードが取得できませんでした。</p>
                <h2>デバッグ情報</h2>
                <p><strong>完全なURL:</strong> {self.path}</p>
                <p><strong>クエリパラメータ:</strong> {query_components}</p>
                <p>このウィンドウを閉じて、ターミナルのデバッグ情報を確認してください。</p>
            </body>
            </html>
            '''
        
        self.wfile.write(message.encode('utf-8'))
    
    def log_message(self, format, *args):
        # ログは表示する
        print(f"HTTPサーバーログ: {format % args}")

def debug_auth_flow():
    print("=== 認証フローデバッグ ===")
    print()
    
    # 設定情報の表示
    print(f"CLIENT_ID: {Config.CLIENT_ID}")
    print(f"AUTHORITY: {Config.AUTHORITY}")
    print(f"REDIRECT_URI: {Config.REDIRECT_URI}")
    print(f"SCOPE: {Config.SCOPE}")
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
    
    print(f"認証URL: {auth_url}")
    print()
    
    print("1. HTTPサーバーを localhost:8000 で起動します...")
    
    try:
        server = HTTPServer(('localhost', 8000), DebugAuthCodeHandler)
        server.auth_code = None
        server.error = None
        server.query_params = {}
        
        print("✓ HTTPサーバーが起動しました")
        print()
        
        print("2. ブラウザで認証ページを開きます...")
        webbrowser.open(auth_url)
        
        print("3. 認証コードの受信を待機中...")
        print("   ブラウザで認証を完了してください...")
        
        # リクエストを待機
        server.handle_request()
        
        print(f"\n=== 受信結果 ===")
        print(f"認証コード: {server.auth_code}")
        print(f"エラー: {server.error}")
        print(f"クエリパラメータ: {server.query_params}")
        
        if server.auth_code:
            print("\n✓ 認証コードの取得に成功しました！")
            
            # トークン取得を試行
            print("\n4. アクセストークンの取得を試行...")
            result = app.acquire_token_by_authorization_code(
                code=server.auth_code,
                scopes=Config.SCOPE,
                redirect_uri=Config.REDIRECT_URI
            )
            
            print(f"トークン取得結果: {result}")
            
            if "access_token" in result:
                print("✓ アクセストークンの取得に成功しました！")
            else:
                print("✗ アクセストークンの取得に失敗しました")
                
        elif server.error:
            print(f"\n✗ 認証エラーが発生しました: {server.error}")
        else:
            print("\n✗ 認証コードが取得できませんでした")
            
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_auth_flow()