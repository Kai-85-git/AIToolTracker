from app import app

# Vercelデプロイ用のWSGIハンドラー
# 注: この変数名は重要です - Vercelは 'app' という名前の変数を探します
app = app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
