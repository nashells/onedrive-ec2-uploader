#!/usr/bin/env python3
"""
OneDrive EC2 Uploader - メインエントリーポイント
プロジェクトルートから実行するためのスクリプト
"""

import os
import sys

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# メインスクリプトの実行
if __name__ == "__main__":
    from src.main import main
    main()