import logging
import os
from datetime import datetime
from src.utils.config import Config


class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        
        # ログディレクトリの作成
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # ロガーの設定
        self.logger = logging.getLogger("OneDriveUploader")
        self.logger.setLevel(getattr(logging, Config.LOG_LEVEL))
        
        # ファイルハンドラの設定
        log_file = os.path.join(log_dir, Config.LOG_FILE)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
        
        # コンソールハンドラの設定
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # フォーマットの設定
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # ハンドラの追加
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def critical(self, message: str):
        self.logger.critical(message)
    
    def log_upload(self, file_path: str, remote_path: str, size: int, success: bool):
        status = "成功" if success else "失敗"
        self.info(f"アップロード {status}: {file_path} -> {remote_path} (サイズ: {size:,} bytes)")
    
    def log_auth(self, action: str, success: bool):
        status = "成功" if success else "失敗"
        self.info(f"認証 {action} {status}")


def get_logger():
    return Logger()