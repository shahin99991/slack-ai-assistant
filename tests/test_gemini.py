"""Test Gemini API functionality."""

import os
import google.generativeai as genai

def test_gemini_api():
    """Test basic Gemini API functionality."""
    # APIキーの直接設定（main.pyで設定済み）
    api_key = "AIzaSyC6qaJaEdMniUh29ofNXqu-cZB5IV7KZok"
    genai.configure(api_key=api_key)
    
    # モデルの取得（gemini-2.0-flash-liteを使用）
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
    
    # テスト用のプロンプト
    prompt = "こんにちは、簡単なテストメッセージです。"
    
    # 応答の生成
    response = model.generate_content(prompt)
    
    # 応答の確認
    assert response is not None
    assert response.text is not None
    assert len(response.text) > 0
    print(f"Gemini API Response: {response.text}")

if __name__ == "__main__":
    test_gemini_api()