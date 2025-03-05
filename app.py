import os
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import logging

# 詳細なデバッグログを有効化
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)
logger.debug("アプリケーション起動開始")

# 環境変数をログに出力（デバッグ用）
logger.debug(f"環境変数: {dict(os.environ)}")

try:
    # Initialize Flask app
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev_key")

    # SQLiteメモリ内データベースを使用
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    logger.debug(f"データベースURI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # モデルとデータベースをインポート
    logger.debug("モデルとデータベースをインポート中...")
    from models import db, AITool
    logger.debug("モデルとデータベースのインポート成功")

    # データベースをアプリケーションに初期化
    logger.debug("データベース初期化中...")
    db.init_app(app)
    logger.debug("データベース初期化成功")

    # リクエストハンドラーの前後にデバッグログを追加
    @app.before_request
    def log_request():
        logger.debug(f"リクエスト: {request.method} {request.path}")

    @app.after_request
    def log_response(response):
        logger.debug(f"レスポンス: {response.status_code}")
        return response

    # テーブルを作成し、サンプルデータを追加
    with app.app_context():
        logger.debug("テーブル作成とサンプルデータ追加開始")
        db.create_all()
        
        # デモデータを追加
        if not AITool.query.first():
            logger.debug("サンプルデータを追加中...")
            demo_tools = [
                AITool(
                    name="GPT-4",
                    url="https://openai.com/gpt-4",
                    developer="OpenAI",
                    description="最先端の大規模言語モデル。テキスト生成、会話、コンテンツ作成に優れています。",
                    category="テキスト生成",
                    features="複雑な会話、コードの生成と説明、長文の要約",
                    pricing="有料サブスクリプション",
                    api_access=True,
                    tags="LLM,AI,テキスト生成",
                    notes="GPT-3.5と比較して複雑なタスクの処理能力が向上"
                ),
                AITool(
                    name="DALL-E 3",
                    url="https://openai.com/dall-e-3",
                    developer="OpenAI",
                    description="テキスト入力から高品質な画像を生成するAIシステム。",
                    category="画像生成",
                    features="テキストプロンプトからの画像生成、スタイル調整、解像度のカスタマイズ",
                    pricing="クレジット制",
                    api_access=True,
                    tags="画像生成,生成AI,OpenAI",
                    notes="詳細なプロンプトほど良い結果が得られる"
                ),
                AITool(
                    name="Midjourney",
                    url="https://www.midjourney.com/",
                    developer="Midjourney, Inc.",
                    description="テキストから芸術的な画像を生成するAI。Discord内で動作します。",
                    category="画像生成",
                    features="高品質な画像生成、細かいスタイル調整、バリエーション作成",
                    pricing="月額サブスクリプション",
                    api_access=False,
                    tags="画像生成,Discord,アート",
                    notes="非常に芸術的な画像を生成できる"
                ),
            ]
            db.session.add_all(demo_tools)
            db.session.commit()
            logger.debug("サンプルデータ追加完了")
        else:
            logger.debug("既存のデータが見つかりました。サンプルデータは追加しません。")

        logger.debug("テーブル作成とデータ追加完了")

except Exception as e:
    logger.error(f"アプリケーション初期化エラー: {str(e)}", exc_info=True)
    raise

# カテゴリーリスト
CATEGORIES = [
    'テキスト生成',
    '画像生成',
    '音声生成',
    '音楽生成',
    '動画生成',
    'コード生成',
    '3D生成',
    'プレゼン生成',
    '検索生成',
    'マインドマップ生成',
    '議事録生成',
    'AI開発',
    'その他'
]

@app.route('/')
def index():
    logger.debug("インデックスページにアクセスしました")
    tools = AITool.query.all()
    logger.debug(f"ツールの数: {len(tools)}")
    return render_template('index.html', tools=tools, categories=CATEGORIES)

@app.route('/tool/<int:tool_id>')
def tool_detail(tool_id):
    logger.debug(f"ツール詳細ページにアクセスしました: ID {tool_id}")
    tool = AITool.query.get_or_404(tool_id)
    return render_template('tool_detail.html', tool=tool, categories=CATEGORIES)

@app.route('/tool/add', methods=['POST'])
def add_tool():
    logger.debug("ツール追加リクエストを受信しました")
    try:
        tool = AITool(
            name=request.form['name'],
            url=request.form['url'],
            developer=request.form['developer'],
            description=request.form['description'],
            category=request.form['category'],
            features=request.form['features'],
            pricing=request.form['pricing'],
            api_access=bool(request.form.get('api_access')),
            tags=request.form['tags'],
            notes=request.form['notes']
        )
        db.session.add(tool)
        db.session.commit()
        logger.debug(f"ツールが正常に追加されました: {tool.name}")
        flash('ツールが正常に登録されました！', 'success')
    except Exception as e:
        logger.error(f"ツール追加エラー: {str(e)}", exc_info=True)
        flash(f'ツールの登録中にエラーが発生しました: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/tool/edit/<int:tool_id>', methods=['POST'])
def edit_tool(tool_id):
    logger.debug(f"ツール編集リクエストを受信しました: ID {tool_id}")
    tool = AITool.query.get_or_404(tool_id)
    try:
        tool.name = request.form['name']
        tool.url = request.form['url']
        tool.developer = request.form['developer']
        tool.description = request.form['description']
        tool.category = request.form['category']
        tool.features = request.form['features']
        tool.pricing = request.form['pricing']
        tool.api_access = bool(request.form.get('api_access'))
        tool.tags = request.form['tags']
        tool.notes = request.form['notes']
        db.session.commit()
        logger.debug(f"ツールが正常に更新されました: ID {tool_id}")
        flash('ツールが正常に更新されました！', 'success')
    except Exception as e:
        logger.error(f"ツール更新エラー: {str(e)}", exc_info=True)
        flash(f'ツールの更新中にエラーが発生しました: {str(e)}', 'error')
    return redirect(url_for('tool_detail', tool_id=tool_id))

@app.route('/tool/delete/<int:tool_id>', methods=['POST'])
def delete_tool(tool_id):
    logger.debug(f"ツール削除リクエストを受信しました: ID {tool_id}")
    tool = AITool.query.get_or_404(tool_id)
    try:
        db.session.delete(tool)
        db.session.commit()
        logger.debug(f"ツールが正常に削除されました: ID {tool_id}")
        flash('ツールが正常に削除されました！', 'success')
    except Exception as e:
        logger.error(f"ツール削除エラー: {str(e)}", exc_info=True)
        flash(f'ツールの削除中にエラーが発生しました: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/compare')
def compare():
    logger.debug("ツール比較ページにアクセスしました")
    tool_ids = request.args.getlist('tools')
    logger.debug(f"比較するツールID: {tool_ids}")
    tools = AITool.query.filter(AITool.id.in_(tool_ids)).all()
    return render_template('compare.html', tools=tools)

@app.route('/search')
def search():
    logger.debug("検索リクエストを受信しました")
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    tags = request.args.get('tags', '')
    
    logger.debug(f"検索パラメータ - キーワード: {query}, カテゴリー: {category}, タグ: {tags}")

    tools_query = AITool.query
    
    if query:
        tools_query = tools_query.filter(
            (AITool.name.ilike(f'%{query}%')) |
            (AITool.description.ilike(f'%{query}%')) |
            (AITool.developer.ilike(f'%{query}%'))
        )
    
    if category:
        tools_query = tools_query.filter(AITool.category == category)
    
    if tags:
        for tag in tags.split(','):
            tools_query = tools_query.filter(AITool.tags.ilike(f'%{tag.strip()}%'))

    tools = tools_query.all()
    logger.debug(f"検索結果: {len(tools)}件のツールが見つかりました")
    return jsonify([tool.to_dict() for tool in tools])

# エラーハンドラーの追加
@app.errorhandler(404)
def page_not_found(e):
    logger.error(f"404 エラー: {request.path}")
    return render_template('index.html', tools=[], categories=CATEGORIES), 404

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"500 エラー: {str(e)}", exc_info=True)
    return render_template('index.html', tools=[], categories=CATEGORIES), 500

if __name__ == "__main__":
    # ローカル開発用のコード
    logger.debug("ローカルサーバーを起動します")
    app.run(host="0.0.0.0", port=5000, debug=True)
