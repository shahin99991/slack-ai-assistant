# デプロイメントガイド

## 1. 前提条件

- Python 3.10以上
- pipまたはvenv
- Slackワークスペースの管理者権限
- Google AI Studioのアカウント

## 2. 環境設定

### 2.1 Python仮想環境の作成

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
.\venv\Scripts\activate  # Windows
```

### 2.2 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2.3 環境変数の設定

以下の環境変数を設定する必要があります：

```bash
# Slack設定
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_CHANNEL_IDS=C1234567890

# Google AI (Gemini)設定
GEMINI_API_KEY=your-gemini-api-key

# ChromaDB設定
CHROMA_PERSIST_DIRECTORY=data/chroma

# アプリケーション設定
DEBUG=false
LOG_LEVEL=INFO
MAX_RESPONSE_TIME=10
```

## 3. アプリケーションの実行

### 3.1 開発環境での実行

```bash
python src/main.py
```

### 3.2 本番環境での実行

systemdサービスとして実行する場合の設定例：

```ini
[Unit]
Description=Slack AI Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/SlackAIBot
Environment=PYTHONPATH=/path/to/SlackAIBot
Environment=SLACK_BOT_TOKEN=xoxb-your-bot-token
Environment=SLACK_APP_TOKEN=xapp-your-app-token
Environment=SLACK_SIGNING_SECRET=your-signing-secret
Environment=SLACK_CHANNEL_IDS=C1234567890
Environment=GEMINI_API_KEY=your-gemini-api-key
Environment=CHROMA_PERSIST_DIRECTORY=data/chroma
Environment=DEBUG=false
Environment=LOG_LEVEL=INFO
Environment=MAX_RESPONSE_TIME=10
ExecStart=/path/to/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 4. 監視とログ

### 4.1 ログの確認

アプリケーションのログは標準出力に出力されます。systemdを使用している場合：

```bash
journalctl -u slack-ai-bot.service -f
```

### 4.2 メトリクスの監視

- メモリ使用量
- CPU使用量
- ディスク使用量（ChromaDBのデータディレクトリ）
- APIレスポンス時間

## 5. バックアップ

### 5.1 ChromaDBのバックアップ

定期的にChromaDBのデータディレクトリをバックアップすることを推奨します：

```bash
tar -czf backup-$(date +%Y%m%d).tar.gz data/chroma/
```

### 5.2 設定のバックアップ

環境変数とsystemd設定ファイルのバックアップを保管してください。

## 6. トラブルシューティング

### 6.1 一般的な問題

1. Slack認証エラー
   - トークンの有効期限と権限を確認
   - Slackアプリの設定を確認

2. Gemini APIエラー
   - APIキーの有効性を確認
   - クォータ制限を確認

3. ChromaDBエラー
   - ディスク容量を確認
   - パーミッションを確認

### 6.2 パフォーマンスの最適化

1. メモリ使用量の削減
   - `MAX_RESPONSE_TIME`の調整
   - ChromaDBのキャッシュサイズの調整

2. レスポンス時間の改善
   - ベクトル検索のパラメータ調整
   - 類似度閾値の調整

## 7. セキュリティ

### 7.1 推奨事項

1. 環境変数の保護
   - 本番環境では環境変数を安全に管理
   - シークレットマネージャーの使用を検討

2. アクセス制御
   - 最小権限の原則に従う
   - 定期的なトークンのローテーション

3. データ保護
   - ChromaDBのデータの暗号化を検討
   - 定期的なバックアップの暗号化

## 8. メンテナンス

### 8.1 定期的なタスク

1. 依存関係の更新
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. ログのローテーション
   ```bash
   logrotate /etc/logrotate.d/slack-ai-bot
   ```

3. データベースの最適化
   - 古いメッセージの削除
   - インデックスの再構築

### 8.2 アップグレード手順

1. アプリケーションの停止
2. バックアップの作成
3. コードの更新
4. 依存関係の更新
5. データベースのマイグレーション（必要な場合）
6. アプリケーションの再起動
