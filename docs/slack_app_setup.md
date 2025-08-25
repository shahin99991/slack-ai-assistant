# Slack App設定手順

## 1. Slack Appの作成

1. [Slack API](https://api.slack.com/apps)にアクセス
2. "Create New App"をクリック
3. "From scratch"を選択
4. アプリ名（例: "SlackAIBot"）とワークスペースを選択
5. "Create App"をクリック

## 2. Bot Tokenのスコープ設定

1. 左サイドバーの"OAuth & Permissions"を選択
2. "Scopes"セクションまでスクロール
3. "Bot Token Scopes"で以下の権限を追加:
   - `channels:history` - パブリックチャンネルの履歴閲覧
   - `channels:read` - パブリックチャンネルの基本情報閲覧
   - `chat:write` - メッセージの送信
   - `app_mentions:read` - アプリへのメンション通知受信
   - `reactions:read` - リアクション情報の閲覧

## 3. アプリのインストール

1. 左サイドバーの"Install App"を選択
2. "Install to Workspace"をクリック
3. 権限を確認して"許可"をクリック

## 4. 認証情報の取得

以下の情報を取得し、`.env`ファイルに設定:

1. Bot User OAuth Token
   - "OAuth & Permissions"ページの"OAuth Tokens for Your Workspace"セクション
   - `xoxb-`で始まるトークンをコピー
   - `.env`ファイルの`SLACK_BOT_TOKEN`に設定

2. Signing Secret
   - "Basic Information"ページの"App Credentials"セクション
   - "Signing Secret"をコピー
   - `.env`ファイルの`SLACK_SIGNING_SECRET`に設定

3. App-Level Token
   - "Basic Information"ページの"App-Level Tokens"セクション
   - "Generate Token and Scopes"をクリック
   - トークン名を入力（例: "socket-token"）
   - `connections:write`スコープを追加
   - "Generate"をクリック
   - `xapp-`で始まるトークンをコピー
   - `.env`ファイルの`SLACK_APP_TOKEN`に設定

## 5. イベントの設定

1. 左サイドバーの"Event Subscriptions"を選択
2. "Enable Events"をオンに切り替え
3. "Subscribe to bot events"セクションで以下のイベントを追加:
   - `app_mention` - ボットへのメンション
   - `message.channels` - チャンネルでのメッセージ

## 6. Socket Modeの有効化

1. 左サイドバーの"Socket Mode"を選択
2. "Enable Socket Mode"をオンに切り替え
3. App-Level Tokenを使用して接続を確認

## 7. チャンネルIDの取得

監視対象のチャンネルIDを取得:

1. Slackクライアントでチャンネルを開く
2. チャンネル名をクリック
3. "About"セクションの"Channel ID"をコピー
4. `.env`ファイルの`SLACK_CHANNEL_IDS`に追加（カンマ区切りで複数指定可能）

## 8. 動作確認

1. ボットをチャンネルに招待
   ```
   /invite @SlackAIBot
   ```

2. メンションでボットをテスト
   ```
   @SlackAIBot こんにちは
   ```

## 注意事項

- 本番環境では、すべての認証情報を安全に管理
- チャンネルの追加時は、必ずボットを招待
- 権限の変更時は、アプリの再インストールが必要
- Socket Modeを使用することで、パブリックなエンドポイントは不要
