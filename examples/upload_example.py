#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import OneDriveUploader


def upload_single_file_example():
    """単一ファイルのアップロード例"""
    uploader = OneDriveUploader()
    uploader.initialize()
    
    # ローカルファイルパス
    local_file = "example.txt"
    
    # テスト用ファイルの作成
    with open(local_file, "w", encoding="utf-8") as f:
        f.write("これはサンプルファイルです。\n")
    
    # OneDriveにアップロード
    remote_path = "samples/example.txt"
    uploader.upload_file(local_file, remote_path)
    
    # クリーンアップ
    os.remove(local_file)


def upload_multiple_files_example():
    """複数ファイルのアップロード例"""
    uploader = OneDriveUploader()
    uploader.initialize()
    
    # フォルダーの作成
    uploader.create_folder("batch_upload")
    
    # 複数のファイルをアップロード
    for i in range(3):
        filename = f"file_{i+1}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"ファイル番号: {i+1}\n")
        
        remote_path = f"batch_upload/{filename}"
        uploader.upload_file(filename, remote_path)
        
        os.remove(filename)
    
    # アップロードしたファイルの一覧表示
    uploader.list_files("batch_upload")


def upload_large_file_example():
    """大きなファイルのアップロード例（再開可能アップロード）"""
    uploader = OneDriveUploader()
    uploader.initialize()
    
    # 5MBのダミーファイルを作成
    large_file = "large_file.bin"
    with open(large_file, "wb") as f:
        f.write(b"0" * (5 * 1024 * 1024))
    
    # アップロード（進捗表示付き）
    remote_path = "large_files/large_file.bin"
    uploader.create_folder("large_files")
    uploader.upload_file(large_file, remote_path)
    
    # クリーンアップ
    os.remove(large_file)


if __name__ == "__main__":
    print("=== OneDrive アップロードサンプル ===\n")
    
    examples = {
        "1": ("単一ファイルのアップロード", upload_single_file_example),
        "2": ("複数ファイルのアップロード", upload_multiple_files_example),
        "3": ("大きなファイルのアップロード", upload_large_file_example),
    }
    
    print("実行するサンプルを選択してください:")
    for key, (desc, _) in examples.items():
        print(f"{key}. {desc}")
    
    choice = input("\n選択 (1-3): ")
    
    if choice in examples:
        print(f"\n{examples[choice][0]}を実行します...\n")
        try:
            examples[choice][1]()
            print("\n完了しました！")
        except Exception as e:
            print(f"\nエラー: {str(e)}")
    else:
        print("無効な選択です。")