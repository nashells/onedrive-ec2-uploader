import os
import requests
from typing import Optional, Dict, Any
from src.utils.config import Config


class OneDriveClient:
    def __init__(self, auth_token: str):
        self.auth_token = auth_token
        self.headers = {
            'Authorization': f'Bearer {auth_token}',
            'Accept': 'application/json'
        }
        self.base_url = Config.GRAPH_API_ENDPOINT
    
    def upload_file(self, file_path: str, remote_path: str, progress_callback=None) -> Dict[str, Any]:
        file_size = os.path.getsize(file_path)
        
        if file_size < 4 * 1024 * 1024:  # 4MB未満
            return self._simple_upload(file_path, remote_path)
        else:
            return self._resumable_upload(file_path, remote_path, progress_callback)
    
    def _simple_upload(self, file_path: str, remote_path: str) -> Dict[str, Any]:
        upload_url = f"{self.base_url}/me/drive/root:/{remote_path}:/content"
        
        with open(file_path, 'rb') as f:
            response = requests.put(
                upload_url,
                headers={**self.headers, 'Content-Type': 'application/octet-stream'},
                data=f
            )
        
        response.raise_for_status()
        return response.json()
    
    def _resumable_upload(self, file_path: str, remote_path: str, progress_callback=None) -> Dict[str, Any]:
        file_size = os.path.getsize(file_path)
        
        # アップロードセッションの作成
        create_session_url = f"{self.base_url}/me/drive/root:/{remote_path}:/createUploadSession"
        session_response = requests.post(
            create_session_url,
            headers=self.headers,
            json={
                "item": {
                    "@microsoft.graph.conflictBehavior": "replace"
                }
            }
        )
        session_response.raise_for_status()
        upload_url = session_response.json()['uploadUrl']
        
        # チャンクサイズ（10MB）
        chunk_size = 10 * 1024 * 1024
        
        with open(file_path, 'rb') as f:
            uploaded = 0
            
            while uploaded < file_size:
                chunk = f.read(chunk_size)
                chunk_len = len(chunk)
                
                headers = {
                    'Content-Length': str(chunk_len),
                    'Content-Range': f'bytes {uploaded}-{uploaded + chunk_len - 1}/{file_size}'
                }
                
                response = requests.put(upload_url, headers=headers, data=chunk)
                response.raise_for_status()
                
                uploaded += chunk_len
                
                if progress_callback:
                    progress_callback(uploaded, file_size)
                
                if uploaded >= file_size:
                    return response.json()
        
        return {}
    
    def create_folder(self, folder_path: str) -> Dict[str, Any]:
        parent_path = "/".join(folder_path.split("/")[:-1])
        folder_name = folder_path.split("/")[-1]
        
        if parent_path:
            create_url = f"{self.base_url}/me/drive/root:/{parent_path}:/children"
        else:
            create_url = f"{self.base_url}/me/drive/root/children"
        
        response = requests.post(
            create_url,
            headers=self.headers,
            json={
                "name": folder_name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "fail"
            }
        )
        
        if response.status_code == 409:  # すでに存在
            return {"status": "already_exists"}
        
        response.raise_for_status()
        return response.json()
    
    def list_files(self, folder_path: str = "") -> Dict[str, Any]:
        if folder_path:
            list_url = f"{self.base_url}/me/drive/root:/{folder_path}:/children"
        else:
            list_url = f"{self.base_url}/me/drive/root/children"
        
        response = requests.get(list_url, headers=self.headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        info_url = f"{self.base_url}/me/drive/root:/{file_path}"
        
        response = requests.get(info_url, headers=self.headers)
        
        if response.status_code == 404:
            return None
        
        response.raise_for_status()
        return response.json()
    
    def delete_file(self, file_path: str) -> bool:
        delete_url = f"{self.base_url}/me/drive/root:/{file_path}"
        
        response = requests.delete(delete_url, headers=self.headers)
        
        if response.status_code in [204, 404]:
            return True
        
        response.raise_for_status()
        return True