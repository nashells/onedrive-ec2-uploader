# OneDrive EC2 Uploader

AWS EC2からMicrosoft OneDriveにファイルをアップロードするためのPythonアプリケーション

## 機能

- OAuth 2.0による安全な認証
- 単一ファイルのアップロード（小さいファイルと大きいファイルの両方に対応）
- 再開可能なアップロード（4MB以上のファイル）
- アップロード進捗の表示
- フォルダーの作成
- ファイル一覧の取得
- 自動リトライ機能
- 詳細なログ記録

## セットアップ手順

### 1. Microsoft Azureアプリの登録

1. [Azure Portal](https://portal.azure.com/)にログイン
2. 「Azure Active Directory」→「アプリの登録」→「新規登録」
3. 以下の情報を入力：
   - 名前: OneDrive EC2 Uploader (任意)
   - サポートされているアカウントの種類: 個人用 Microsoft アカウントのみ
   - リダイレクトURI: http://localhost:8000 (Web)
4. 登録後、以下の情報をメモ：
   - アプリケーション (クライアント) ID
   - ディレクトリ (テナント) ID
5. 「証明書とシークレット」→「新しいクライアント シークレット」でシークレットを作成
6. 「APIのアクセス許可」→「アクセス許可の追加」→「Microsoft Graph」→「委任されたアクセス許可」で以下を追加：
   - Files.ReadWrite.All
   - offline_access

### 2. 環境設定

1. `.env.example`を`.env`にコピー
   ```bash
   cp .env.example .env
   ```

2. `.env`ファイルを編集してAzureアプリの情報を設定：
   ```
   CLIENT_ID=your_client_id_here
   CLIENT_SECRET=your_client_secret_here
   TENANT_ID=your_tenant_id_here
   ```

### 3. Python環境のセットアップ

```bash
# 仮想環境の作成（推奨）
python -m venv venv

# 仮想環境の有効化
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

### 4. 実行

基本的な使い方：
```bash
python src/main.py
```

サンプルスクリプトの実行：
```bash
python examples/upload_example.py
```

初回実行時はブラウザが開き、Microsoftアカウントでのログインが必要です。認証後、トークンは自動的に保存され、次回以降は自動的に更新されます。

## プロジェクト構造

```
onedrive-ec2-uploader/
├── src/
│   ├── auth/           # 認証関連
│   ├── api/            # OneDrive API クライアント
│   └── utils/          # ユーティリティ（設定、ログ、リトライ）
├── examples/           # 使用例
├── logs/              # ログファイル
├── .env.example       # 環境変数のテンプレート
├── requirements.txt   # Python依存関係
└── README.md         # このファイル
```

## 使用例

```python
from src.main import OneDriveUploader

# アップローダーの初期化
uploader = OneDriveUploader()
uploader.initialize()

# フォルダーの作成
uploader.create_folder("my_folder")

# ファイルのアップロード
uploader.upload_file("local_file.txt", "my_folder/remote_file.txt")

# ファイル一覧の取得
files = uploader.list_files("my_folder")
```

## トラブルシューティング

- **認証エラー**: `.env`ファイルの設定を確認してください
- **アップロードエラー**: ネットワーク接続を確認し、ログファイルを参照してください
- **権限エラー**: Azureアプリに必要なAPI権限が付与されているか確認してください

## ログ

ログは`logs/onedrive_uploader.log`に保存されます。ログレベルは`.env`ファイルで設定可能です。