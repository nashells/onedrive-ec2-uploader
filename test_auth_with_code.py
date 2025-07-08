#!/usr/bin/env python3
"""
認証コード指定テスト用スクリプト
環境変数AUTH_CODEで認証コードを渡す
"""

import os
import sys

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.auth.authenticator import OneDriveAuthenticator
from src.api.onedrive_client import OneDriveClient
from src.utils.config import Config

def test_auth_with_code():
    print("=== 認証コード指定テスト ===")
    
    # 認証URLを表示
    authenticator = OneDriveAuthenticator()
    auth_url = authenticator.app.get_authorization_request_url(
        scopes=Config.SCOPE,
        redirect_uri=Config.REDIRECT_URI
    )
    
    print(f"\n手順:")
    print(f"1. ブラウザで以下のURLを開いてください:")
    print(f"   {auth_url}")
    print(f"")
    print(f"2. Microsoftアカウントでログインしてください")
    print(f"")
    print(f"3. リダイレクト後のURLから認証コードをコピーして、以下のコマンドで実行してください:")
    print(f"   AUTH_CODE='認証コード' python test_auth_with_code.py")
    print(f"")
    
    # 環境変数から認証コードを取得
    auth_code = os.getenv('AUTH_CODE')
    
    if not auth_code:
        print("環境変数AUTH_CODEが設定されていません。")
        print("上記の手順に従って認証コードを取得してください。")
        return
    
    print(f"認証コードが設定されました: {auth_code[:10]}...")
    
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
        test_file = "test_auth_upload.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("認証テスト成功！\n")
            f.write("OneDriveアップローダーが正常に動作しています。\n")
        
        upload_result = client.upload_file(test_file, "test_auth_upload.txt")
        print(f"✓ ファイルアップロード成功: {upload_result.get('name', 'test_auth_upload.txt')}")
        
        # クリーンアップ
        os.remove(test_file)
        
        print(f"\n=== テスト完了 ===")
        print(f"✓ すべての機能が正常に動作しました！")
        print(f"✓ トークンキャッシュが保存されました")
        print(f"✓ 次回からは 'python run.py' で自動ログインできます")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auth_with_code()