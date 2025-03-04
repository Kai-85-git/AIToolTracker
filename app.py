import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_key")

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ai_tools.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Import models after db initialization
from models import AITool

# Create all database tables
with app.app_context():
    db.create_all()

CATEGORIES = ['テキスト生成', '画像生成', '音声生成', '動画生成', 'コード生成', 'その他']

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