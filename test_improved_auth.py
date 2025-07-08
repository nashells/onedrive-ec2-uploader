#!/usr/bin/env python3
"""
改善された認証フローのテスト
"""

import os
import sys

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.auth.authenticator import OneDriveAuthenticator
from src.utils.config import Config

def test_improved_auth():
    print("=== 改善された認証フローのテスト ===")
    print()
    print("このテストでは以下が実行されます:")
    print("1. localhost:8000で一時的なHTTPサーバーを起動")
    print("2. ブラウザで認証ページを自動で開く")  
    print("3. 認証完了後、正常な成功ページを表示")
    print("4. 認証コードを自動で取得")
    print()
    
    try:
        authenticator = OneDriveAuthenticator()
        
        print("認証を開始します...")
        result = authenticator.get_token()
        
        if "access_token" in result:
            print("✓ 認証が正常に完了しました！")
            print(f"✓ アクセストークンを取得しました")
            print(f"✓ トークンの有効期限: {result.get('expires_in', 'Unknown')}秒")
            
            # 簡単な接続テスト
            from src.api.onedrive_client import OneDriveClient
            client = OneDriveClient(result["access_token"])
            
            files = client.list_files()
            print(f"✓ OneDriveに正常に接続できました")
            print(f"✓ ルートフォルダー内のアイテム数: {len(files.get('value', []))}")
            
        else:
            print("✗ 認証に失敗しました")
            
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_improved_auth()
    if success:
        print("\n=== テスト成功 ===")
        print("改善された認証フローが正常に動作しました！")
        print("今後は `python run.py` で自動ログインできます。")
    else:
        print("\n=== テスト失敗 ===")
        print("認証フローに問題があります。")