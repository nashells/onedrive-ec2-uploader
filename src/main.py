import os
import sys
from pathlib import Path
from requests.exceptions import HTTPError

# プロジェクトルートをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.auth.authenticator import OneDriveAuthenticator
from src.api.onedrive_client import OneDriveClient
from src.utils.config import Config
from src.utils.logger import get_logger
from src.utils.retry import retry_on_exception


class OneDriveUploader:
    def __init__(self):
        self.logger = get_logger()
        self.authenticator = OneDriveAuthenticator()
        self.client = None
        
    def initialize(self):
        try:
            Config.validate()
            self.logger.info("設定の検証が完了しました")
            
            # 認証
            self.logger.info("認証を開始します...")
            token_result = self.authenticator.get_token()
            
            if "access_token" not in token_result:
                raise Exception("アクセストークンの取得に失敗しました")
            
            self.client = OneDriveClient(token_result["access_token"])
            self.logger.log_auth("トークン取得", True)
            self.logger.info("OneDriveへの接続に成功しました")
            
        except Exception as e:
            self.logger.error(f"初期化エラー: {str(e)}")
            self.logger.log_auth("初期化", False)
            raise
    
    @retry_on_exception(max_retries=3, delay=1.0, backoff=2.0, exceptions=(HTTPError,))
    def upload_file(self, local_path: str, remote_path: str):
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"ファイルが見つかりません: {local_path}")
        
        file_size = os.path.getsize(local_path)
        self.logger.info(f"アップロード開始: {local_path} ({file_size:,} bytes)")
        
        def progress_callback(uploaded, total):
            percent = (uploaded / total) * 100
            print(f"\rアップロード進捗: {percent:.1f}% ({uploaded:,}/{total:,} bytes)", end="")
        
        try:
            result = self.client.upload_file(local_path, remote_path, progress_callback)
            print()  # 改行
            self.logger.log_upload(local_path, remote_path, file_size, True)
            self.logger.info(f"アップロード完了: {result.get('name', remote_path)}")
            return result
        except Exception as e:
            print()  # 改行
            self.logger.error(f"アップロードエラー: {str(e)}")
            self.logger.log_upload(local_path, remote_path, file_size, False)
            raise
    
    def create_folder(self, folder_path: str):
        try:
            result = self.client.create_folder(folder_path)
            if result.get("status") == "already_exists":
                self.logger.info(f"フォルダーは既に存在します: {folder_path}")
            else:
                self.logger.info(f"フォルダーを作成しました: {folder_path}")
            return result
        except Exception as e:
            self.logger.error(f"フォルダー作成エラー: {str(e)}")
            raise
    
    def list_files(self, folder_path: str = ""):
        try:
            result = self.client.list_files(folder_path)
            files = result.get("value", [])
            
            self.logger.info(f"フォルダー内のファイル一覧: {folder_path or 'ルート'}")
            for file in files:
                file_type = "フォルダー" if "folder" in file else "ファイル"
                size = file.get("size", 0) if "folder" not in file else "-"
                print(f"  {file_type}: {file['name']} (サイズ: {size})")
            
            return files
        except Exception as e:
            self.logger.error(f"ファイル一覧取得エラー: {str(e)}")
            raise


def main():
    uploader = OneDriveUploader()
    
    try:
        uploader.initialize()
        
        # デモ: テキストファイルのアップロード
        demo_file = "test_upload.txt"
        if not os.path.exists(demo_file):
            with open(demo_file, "w", encoding="utf-8") as f:
                f.write("OneDriveアップロードテスト\n")
                f.write("これはテストファイルです。\n")
                f.write("正常にアップロードされるはずです。\n")
        
        # フォルダーの作成
        uploader.create_folder("test_folder")
        
        # ファイルのアップロード
        uploader.upload_file(demo_file, "test_folder/test_upload.txt")
        
        # ファイル一覧の表示
        uploader.list_files("test_folder")
        
    except Exception as e:
        print(f"\nエラーが発生しました: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()