from app import app

# Vercelはmain.pyからapp変数を探します
# この変数がFSLKアプリケーションオブジェクトを指している必要があります

if __name__ == "__main__":
    # ローカル開発用のコード
    # Vercelではこの部分は使用されません
    app.run(host="0.0.0.0", port=5000, debug=False)
