#!/usr/bin/env python3
"""
インポートテスト - 依存関係がインストールされているかテスト
"""

import os
import sys

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """必要なモジュールがインポートできるかテスト"""
    print("インポートテストを開始します...")
    
    try:
        print("1. 標準ライブラリのテスト...")
        import os, sys, json, webbrowser, logging
        from http.server import HTTPServer, BaseHTTPRequestHandler
        from urllib.parse import urlparse, parse_qs
        from datetime import datetime
        from pathlib import Path
        from typing import Optional, Dict, Any
        import functools, time
        print("   ✓ 標準ライブラリ OK")
        
        print("2. 外部ライブラリのテスト...")
        try:
            import msal
            print("   ✓ msal OK")
        except ImportError:
            print("   ✗ msal が見つかりません")
            
        try:
            import requests
            print("   ✓ requests OK")
        except ImportError:
            print("   ✗ requests が見つかりません")
            
        try:
            import aiohttp
            print("   ✓ aiohttp OK")
        except ImportError:
            print("   ✗ aiohttp が見つかりません")
            
        try:
            from dotenv import load_dotenv
            print("   ✓ python-dotenv OK")
        except ImportError:
            print("   ✗ python-dotenv が見つかりません")
            
        try:
            import boto3
            print("   ✓ boto3 OK")
        except ImportError:
            print("   ✗ boto3 が見つかりません")
        
        print("3. プロジェクトモジュールのテスト...")
        try:
            from src.utils.config import Config
            print("   ✓ Config クラス OK")
        except ImportError as e:
            print(f"   ✗ Config クラス: {e}")
            
        try:
            from src.utils.retry import retry_on_exception
            print("   ✓ retry_on_exception OK")
        except ImportError as e:
            print(f"   ✗ retry_on_exception: {e}")
            
        print("\nインポートテスト完了!")
        
    except Exception as e:
        print(f"テスト中にエラーが発生しました: {e}")

if __name__ == "__main__":
    test_imports()