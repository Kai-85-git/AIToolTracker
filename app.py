import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_key")

# Vercel向けの設定: メモリ内データベース (デモ用) または環境変数から取得したデータベースURL
database_url = os.environ.get("DATABASE_URL", "sqlite:///memory:")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# モデルとデータベースをインポート
from models import db, AITool

# データベースをアプリケーションに初期化
db.init_app(app)

# Create all database tables
with app.app_context():
    db.create_all()
    
    # デモデータを追加（データベースが空の場合）
    if not AITool.query.first():
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
    tools = AITool.query.all()
    return render_template('index.html', tools=tools, categories=CATEGORIES)

@app.route('/tool/<int:tool_id>')
def tool_detail(tool_id):
    tool = AITool.query.get_or_404(tool_id)
    return render_template('tool_detail.html', tool=tool, categories=CATEGORIES)

@app.route('/tool/add', methods=['POST'])
def add_tool():
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
        flash('ツールが正常に登録されました！', 'success')
    except Exception as e:
        flash(f'ツールの登録中にエラーが発生しました: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/tool/edit/<int:tool_id>', methods=['POST'])
def edit_tool(tool_id):
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
        flash('ツールが正常に更新されました！', 'success')
    except Exception as e:
        flash(f'ツールの更新中にエラーが発生しました: {str(e)}', 'error')
    return redirect(url_for('tool_detail', tool_id=tool_id))

@app.route('/tool/delete/<int:tool_id>', methods=['POST'])
def delete_tool(tool_id):
    tool = AITool.query.get_or_404(tool_id)
    try:
        db.session.delete(tool)
        db.session.commit()
        flash('ツールが正常に削除されました！', 'success')
    except Exception as e:
        flash(f'ツールの削除中にエラーが発生しました: {str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/compare')
def compare():
    tool_ids = request.args.getlist('tools')
    tools = AITool.query.filter(AITool.id.in_(tool_ids)).all()
    return render_template('compare.html', tools=tools)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    tags = request.args.get('tags', '')

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
    return jsonify([tool.to_dict() for tool in tools])
