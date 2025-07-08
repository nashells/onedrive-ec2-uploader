#!/usr/bin/env python3
"""
URL から認証コードを抽出するヘルパースクリプト
"""

from urllib.parse import urlparse, parse_qs

def extract_auth_code():
    print("=== 認証コード抽出ヘルパー ===")
    print()
    print("1. 現在表示されているエラーページのURLバーから、完全なURLをコピーしてください")
    print("   例: http://localhost:8000/?code=M.C507_BAY.2.U.xxxxxxx&state=...")
    print()
    print("2. 以下に貼り付けてください:")
    
    # URLを環境変数から取得するか、ファイルから読み込む
    import os
    
    # URLを引数として渡すか、環境変数で指定
    url = os.getenv('REDIRECT_URL')
    
    if not url:
        print("環境変数REDIRECT_URLが設定されていません。")
        print()
        print("以下のコマンドで実行してください:")
        print("REDIRECT_URL='完全なリダイレクトURL' python extract_code_from_url.py")
        print()
        print("例:")
        print("REDIRECT_URL='http://localhost:8000/?code=M.C507_BAY.2.U.xxxxxxx&state=...' python extract_code_from_url.py")
        return
    
    try:
        # URLを解析
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if 'code' not in params:
            print("エラー: URLに認証コードが含まれていません")
            print(f"取得したURL: {url}")
            return
        
        auth_code = params['code'][0]
        print(f"✓ 認証コードが抽出されました!")
        print(f"認証コード: {auth_code}")
        print()
        print("以下のコマンドでテストを実行してください:")
        print(f"AUTH_CODE='{auth_code}' python test_auth_with_code.py")
        
    except Exception as e:
        print(f"エラー: {str(e)}")
        print(f"URL: {url}")

if __name__ == "__main__":
    extract_auth_code()