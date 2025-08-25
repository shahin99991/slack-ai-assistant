# Slack AI Assistant 運用マニュアル

## サービスの基本操作

### 起動と停止
```bash
# ボットの起動
sudo systemctl start slackbot

# ボットの停止
sudo systemctl stop slackbot

# ボットの再起動
sudo systemctl restart slackbot
```

### 自動起動の設定
```bash
# 自動起動を有効化（PC起動時に自動的に開始）
sudo systemctl enable slackbot

# 自動起動を無効化（PC起動時に自動起動しない）
sudo systemctl disable slackbot
```

### 状態確認
```bash
# サービスの状態確認
sudo systemctl status slackbot

# リアルタイムログの確認
sudo journalctl -u slackbot -f

# 直近のログ確認（最新50行）
sudo journalctl -u slackbot -n 50
```

## 運用モード

1. **開発・テストモード**
   - 必要なときだけ手動で起動/停止
   - `sudo systemctl start slackbot` で起動
   - `sudo systemctl stop slackbot` で停止
   - ログを監視して動作確認

2. **本番運用モード**
   - 自動起動を有効化（`sudo systemctl enable slackbot`）
   - システム起動時に自動的に開始
   - 定期的なログ確認推奨

## リソース監視

### メモリ使用量の確認
```bash
ps aux | grep python | grep main.py
```

### ログファイルの確認
```bash
# システムログの確認
tail -f /var/log/slackbot.log

# エラーログの確認
tail -f /var/log/slackbot.error.log
```

## トラブルシューティング

1. **サービスが起動しない場合**
   ```bash
   # ログの確認
   sudo journalctl -u slackbot -n 50
   
   # 設定ファイルの確認
   sudo systemctl cat slackbot
   ```

2. **応答がない場合**
   ```bash
   # サービスの状態確認
   sudo systemctl status slackbot
   
   # 必要に応じて再起動
   sudo systemctl restart slackbot
   ```

3. **エラーが発生した場合**
   - ログを確認
   - .envファイルの設定を確認
   - 必要に応じてサービスを再起動

## 注意事項

1. **リソース管理**
   - メモリ使用量は通常低め
   - API使用量は質問応答時のみ発生

2. **セキュリティ**
   - .envファイルの権限設定を確認
   - ログファイルのアクセス権限を確認

3. **メンテナンス**
   - 定期的なログの確認
   - 不要なログファイルの削除
   - APIキーの有効期限確認
