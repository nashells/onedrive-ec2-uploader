# EC2デプロイメントガイド

## EC2環境での認証方法

EC2でサービスとして動かす場合、以下の方法を推奨します：

### 方法1: デバイスコードフロー（推奨）

**Azure Portal設定:**
1. Azure Portal → アプリの登録 → あなたのアプリ
2. **認証** → **詳細設定**
3. **パブリック クライアント フローを許可する** を **はい** に変更
4. **保存**

**メリット:**
- サーバー不要
- セキュア
- EC2環境に最適

### 方法2: 事前認証済みトークン

**ローカルで認証してトークンをEC2に転送:**

1. ローカルPCで認証を完了
2. `token_cache.json` をEC2にアップロード
3. EC2で自動トークン更新

```bash
# ローカルでトークン取得
python test_auth_with_code.py

# EC2にトークンファイルを転送
scp token_cache.json ec2-user@your-ec2:/path/to/app/
```

### 方法3: サービスプリンシパル（企業用）

Azure ADでサービスプリンシパルを作成して、クライアントクレデンシャル認証を使用。

## 推奨デプロイメント手順

### 1. EC2環境準備
```bash
sudo yum update -y
sudo yum install python3 python3-pip git -y
```

### 2. アプリケーションデプロイ
```bash
git clone https://github.com/nashells/onedrive-ec2-uploader.git
cd onedrive-ec2-uploader
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 設定
```bash
cp .env.example .env
# .envファイルを編集
```

### 4. 初回認証（方法2の場合）
ローカルで認証を完了してトークンファイルを転送

### 5. サービス化
```bash
sudo cp scripts/onedrive-uploader.service /etc/systemd/system/
sudo systemctl enable onedrive-uploader
sudo systemctl start onedrive-uploader
```

## セキュリティ考慮事項

1. **環境変数**: 認証情報は環境変数で管理
2. **ファイル権限**: トークンファイルの権限を制限
3. **ネットワーク**: 必要最小限のポート開放
4. **ログ**: 認証情報をログに出力しない