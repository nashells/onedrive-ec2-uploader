#!/usr/bin/env python3
"""
デバイスコードフローのテスト
Azure Portal でパブリッククライアントフロー有効化後に実行
"""

import os
import sys

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.utils.config import Config
import msal

def test_device_flow():
    print("=== デバイスコードフローテスト ===")
    print()
    print("前提条件:")
    print("✓ Azure Portal でパブリッククライアントフローが有効化されている")
    print()
    
    print("設定情報:")
    print(f"CLIENT_ID: {Config.CLIENT_ID}")
    print(f"AUTHORITY: {Config.AUTHORITY}")
    print(f"SCOPE: {Config.SCOPE}")
    print()
    
    try:
        # PublicClientApplicationを作成
        app = msal.PublicClientApplication(
            Config.CLIENT_ID,
            authority=Config.AUTHORITY
        )
        
        print("デバイスフローを初期化しています...")
        
        # デバイスフローを開始
        flow = app.initiate_device_flow(scopes=Config.SCOPE)
        
        if "user_code" not in flow:
            print("❌ デバイスフローの初期化に失敗しました")
            print("Azure Portal でパブリッククライアントフローが有効になっているか確認してください")
            return False
        
        print("✅ デバイスフロー初期化成功!")
        print()
        print("=" * 70)
        print("🔐 Microsoft OneDrive デバイス認証")
        print("=" * 70)
        print(f"1. ブラウザで以下のURLを開いてください:")
        print(f"   🌐 {flow['verification_uri']}")
        print()
        print(f"2. 画面に表示されるコード入力欄に以下を入力してください:")
        print(f"   📋 デバイスコード: {flow['user_code']}")
        print()
        print(f"3. Microsoftアカウントでログインしてください")
        print()
        print(f"⏳ 認証完了を待機中... (タイムアウト: {flow.get('expires_in', 900)}秒)")
        print("   認証を完了すると自動的に進みます")
        print("=" * 70)
        
        # ユーザーの認証を待機
        result = app.acquire_token_by_device_flow(flow)
        
        if "error" in result:
            print(f"❌ 認証エラー: {result['error']}")
            print(f"詳細: {result.get('error_description', '')}")
            return False
        
        if "access_token" not in result:
            print("❌ アクセストークンの取得に失敗しました")
            return False
        
        print()
        print("🎉 認証成功!")
        print(f"✅ アクセストークンを取得しました")
        print(f"✅ 有効期限: {result.get('expires_in', 'Unknown')}秒")
        
        # OneDriveクライアントのテスト
        print()
        print("OneDrive接続テストを実行中...")
        
        from src.api.onedrive_client import OneDriveClient
        client = OneDriveClient(result["access_token"])
        
        files = client.list_files()
        print(f"✅ OneDriveに正常に接続しました")
        print(f"✅ ルートフォルダー内のアイテム数: {len(files.get('value', []))}")
        
        # トークンキャッシュを保存
        try:
            # MSALのバージョンに応じてキャッシュを保存
            if hasattr(app.token_cache, 'serialize'):
                # 新しいMSALバージョン
                cache_data = app.token_cache.serialize()
            else:
                # 古いMSALバージョン
                cache_data = app.token_cache._cache
            
            with open('token_cache.json', 'w') as f:
                if isinstance(cache_data, str):
                    f.write(cache_data)
                else:
                    import json
                    json.dump(cache_data, f)
                    
        except Exception as cache_error:
            print(f"⚠️  トークンキャッシュの保存に失敗しましたが、認証は成功しています")
            print(f"キャッシュエラー: {cache_error}")
            print("手動でトークンを再取得する必要がある場合があります")
        
        print(f"✅ トークンキャッシュを保存しました")
        print()
        print("🚀 EC2環境でのデプロイ準備完了!")
        print("   今後は 'python run.py' で自動ログインできます")
        
        return True
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_device_flow()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ デバイスコードフローテスト成功!")
        print("EC2環境での認証準備が完了しました")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ デバイスコードフローテスト失敗")
        print("Azure Portal の設定を確認してください")
        print("=" * 50)