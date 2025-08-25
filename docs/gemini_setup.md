# Google AI (Gemini) API設定手順

## 1. Google AI Studioへのアクセス

1. [Google AI Studio](https://makersuite.google.com/app/apikey)にアクセス
2. Googleアカウントでログイン
3. 利用規約に同意

## 2. APIキーの取得

1. "Get API key"をクリック
2. 新しいAPIキーを作成、または既存のキーを選択
3. APIキーをコピー
4. `.env`ファイルの`GEMINI_API_KEY`に設定

## 3. APIの利用制限と料金

### 無料枠
- 60 calls/minute
- モデルごとに異なる制限あり

### 料金（2024年3月現在）
- Gemini Pro
  - Input: $0.00025 / 1K characters
  - Output: $0.0005 / 1K characters
- Embedding
  - $0.0001 / 1K characters

## 4. 使用するモデル

### テキスト生成
- モデル: `gemini-pro`
- 用途: 質問への回答生成
- 特徴:
  - 最大入力トークン: 30,720
  - 最大出力トークン: 2,048
  - 複数のターンの会話をサポート

### テキスト埋め込み
- モデル: `embedding-001`
- 用途: メッセージと質問のベクトル化
- 特徴:
  - 次元数: 768
  - 正規化済みベクトル
  - 高速な処理

## 5. APIの使用例

### テキスト生成
```python
import google.generativeai as genai

genai.configure(api_key="your-api-key")
model = genai.GenerativeModel("gemini-pro")

response = model.generate_content("あなたの質問")
print(response.text)
```

### テキスト埋め込み
```python
import google.generativeai as genai

genai.configure(api_key="your-api-key")

result = genai.embed_content(
    model="embedding-001",
    content="埋め込みたいテキスト",
)
embedding = result["embedding"]
```

## 6. エラー処理

主なエラーコードと対処方法:

- 429: Rate limit exceeded
  - リクエストの頻度を下げる
  - 再試行の間隔を調整
- 401: Invalid API key
  - APIキーの確認
  - 環境変数の設定確認
- 400: Invalid request
  - 入力内容の確認
  - パラメータの確認

## 7. ベストプラクティス

1. APIキーの管理
   - 環境変数での管理
   - 本番環境での安全な管理
   - 定期的なローテーション

2. レート制限への対応
   - リクエストの制御
   - バックオフ戦略の実装
   - キャッシュの活用

3. コスト管理
   - 使用量の監視
   - 予算アラートの設定
   - 最適化戦略の実装

4. エラーハンドリング
   - 適切な再試行ロジック
   - エラーログの記録
   - フォールバック戦略の実装

## 8. 注意事項

- APIキーを公開リポジトリにコミットしない
- 本番環境では適切なセキュリティ対策を実施
- 使用量とコストを定期的に監視
- モデルの制限と特性を理解した上で使用
