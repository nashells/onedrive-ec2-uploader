#!/usr/bin/env python3
"""
手動認証用スクリプト
ブラウザが利用できない環境での認証テスト用
"""

import os
import sys

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.auth.authenticator import OneDriveAuthenticator
from src.api.onedrive_client import OneDriveClient
from src.utils.config import Config

def manual_auth():
    print("=== 手動認証テスト ===")
    
    authenticator = OneDriveAuthenticator()
    
    # 認証URLを表示
    auth_url = authenticator.app.get_authorization_request_url(
        scopes=Config.SCOPE,
        redirect_uri=Config.REDIRECT_URI
    )
    
    print(f"\n1. ブラウザで以下のURLを開いてください:")
    print(f"{auth_url}")
    print(f"\n2. Microsoftアカウントでログインしてください")
    print(f"3. リダイレクト後のURLから認証コード（code=の後の部分）をコピーしてください")
    
    # 認証コードを手動入力
    auth_code = input(f"\n認証コードを入力してください: ").strip()
    
    if not auth_code:
        print("認証コードが入力されませんでした。")
        return
    
    try:
        # トークンを取得
        result = authenticator.app.acquire_token_by_authorization_code(
            code=auth_code,
            scopes=Config.SCOPE,
            redirect_uri=Config.REDIRECT_URI
        )
        
        if "error" in result:
            print(f"エラー: {result.get('error_description', result.get('error'))}")
            return
        
        print("✓ 認証成功！")
        print(f"アクセストークン取得済み（有効期限: {result.get('expires_in', 'Unknown')}秒）")
        
        # トークンキャッシュを保存
        authenticator._save_cache()
        
        # OneDriveクライアントのテスト
        client = OneDriveClient(result["access_token"])
        
        print("\n=== OneDrive接続テスト ===")
        files = client.list_files()
        print(f"✓ OneDriveルートフォルダーにアクセス成功")
        print(f"ファイル数: {len(files.get('value', []))}")
        
        # テストファイルの作成とアップロード
        test_file = "test_manual_upload.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("手動認証テストファイル\n作成日時: " + str(result.get('expires_in')))
        
        upload_result = client.upload_file(test_file, "test_manual_upload.txt")
        print(f"✓ ファイルアップロード成功: {upload_result.get('name', 'test_manual_upload.txt')}")
        
        # クリーンアップ
        os.remove(test_file)
        
        print(f"\n=== テスト完了 ===")
        print(f"トークンキャッシュが保存されました。次回は自動でログインできます。")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    manual_auth()