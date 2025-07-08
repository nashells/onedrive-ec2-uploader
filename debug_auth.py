#!/usr/bin/env python3
"""
認証の詳細デバッグ用スクリプト
"""

import os
import sys

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.utils.config import Config
import msal

def debug_auth():
    print("=== 認証設定デバッグ ===")
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
    
    print("=== 複数の認証方式を試行 ===")
    
    # 方法1: consumers エンドポイント
    print("\n1. consumers エンドポイント:")
    auth_url_consumers = app.get_authorization_request_url(
        scopes=Config.SCOPE,
        redirect_uri=Config.REDIRECT_URI
    )
    print(auth_url_consumers)
    
    # 方法2: common エンドポイント
    print("\n2. common エンドポイントを試行:")
    app_common = msal.ConfidentialClientApplication(
        Config.CLIENT_ID,
        authority="https://login.microsoftonline.com/common",
        client_credential=Config.CLIENT_SECRET
    )
    auth_url_common = app_common.get_authorization_request_url(
        scopes=Config.SCOPE,
        redirect_uri=Config.REDIRECT_URI
    )
    print(auth_url_common)
    
    # 方法3: 簡略化されたスコープ
    print("\n3. 簡略化されたスコープを試行:")
    simple_scopes = ["Files.ReadWrite.All"]
    auth_url_simple = app.get_authorization_request_url(
        scopes=simple_scopes,
        redirect_uri=Config.REDIRECT_URI
    )
    print(auth_url_simple)
    
    # 方法4: PublicClientApplication
    print("\n4. PublicClientApplication を試行:")
    try:
        public_app = msal.PublicClientApplication(
            Config.CLIENT_ID,
            authority=Config.AUTHORITY
        )
        
        # デバイスフローを試行
        device_flow = public_app.initiate_device_flow(scopes=Config.SCOPE)
        if "user_code" in device_flow:
            print(f"デバイスコード認証:")
            print(f"URL: {device_flow['verification_uri']}")
            print(f"コード: {device_flow['user_code']}")
        else:
            print("デバイスフロー初期化失敗")
    except Exception as e:
        print(f"PublicClientApplication エラー: {e}")
    
    print("\n=== 推奨事項 ===")
    print("1. 上記のURLのいずれかを試してください")
    print("2. エラーが続く場合は、Azure Portal でアプリ設定を確認してください:")
    print("   - 認証 > リダイレクトURI")
    print("   - 認証 > サポートされているアカウントの種類")
    print("   - APIのアクセス許可")

if __name__ == "__main__":
    debug_auth()