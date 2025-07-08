#!/usr/bin/env python3
"""
OneDrive EC2 Uploader - モジュールモード実行用
python -m src で実行できるようにするためのファイル
"""

import os
import sys

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.main import main

if __name__ == "__main__":
    main()