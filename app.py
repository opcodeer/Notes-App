from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import datetime
import os
import subprocess
from dotenv import load_dotenv
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'notes.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
load_dotenv()  # loads variables from .env

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

db = SQLAlchemy(app)

# ---------------- Models ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    category = db.Column(db.String(50))
    pinned = db.Column(db.Boolean, default=False)
    summary = db.Column(db.Text, nullable=True)  # <-- NEW column for summary
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# ---------------- Token decorator ----------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'message': 'Token missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = db.session.get(User, data['id'])
        except Exception as e:
            return jsonify({'message': 'Invalid token!', 'error': str(e)}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# ---------------- Auth Routes ----------------
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    token = jwt.encode(
        {'id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=5)},
        app.config['SECRET_KEY'],
        algorithm="HS256"
    )
    return jsonify({'token': token, 'username': user.username})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username and password required!'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists!'}), 400

    hashed_pw = generate_password_hash(data['password'], method='pbkdf2:sha256', salt_length=8)
    new_user = User(username=data['username'], password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully!'}), 201

# ---------------- AI Summary ----------------
def generate_summary(note_content):
    if not note_content:
        return None
    try:
        # Run Gemini CLI via subprocess on Windows
        cmd = f'gemini "Summarize the following text: {note_content}"'
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True  # important for Windows
        )

        if result.returncode == 0:
            summary = result.stdout.strip()
            # Optional: truncate very long summaries
            if len(summary) > 200:
                summary = summary[:200] + "..."
            return summary
        else:
            print("Gemini CLI error:", result.stderr)
            return "Summary could not be generated."
    except Exception as e:
        print("Error running Gemini CLI:", e)
        return "Summary could not be generated."

# ---------------- Notes Routes ----------------
@app.route('/notes-page')
def notes_page():
    return render_template('notes.html')

@app.route('/notes', methods=['GET'])
@token_required
def get_notes(current_user):
    category = request.args.get('category')
    search = request.args.get('search', '').lower()

    query = Note.query.filter_by(user_id=current_user.id)
    if category:
        query = query.filter_by(category=category)
    notes = query.order_by(Note.pinned.desc(), Note.timestamp.desc()).all()
    if search:
        notes = [n for n in notes if search in n.title.lower() or search in n.content.lower()]

    return jsonify([{
        'id': n.id,
        'title': n.title,
        'content': n.content,
        'category': n.category,
        'pinned': n.pinned,
        'summary': n.summary,
        'timestamp': n.timestamp
    } for n in notes])

@app.route('/notes', methods=['POST'])
@token_required
def create_note(current_user):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    category = data.get('category', 'General')
    pinned = data.get('pinned', False)

    summary = generate_summary(content)

    new_note = Note(
        title=title,
        content=content,
        category=category,
        pinned=pinned,
        summary=summary,
        user_id=current_user.id
    )
    db.session.add(new_note)
    db.session.commit()

    return jsonify({
        'message': 'Note created successfully!',
        'summary': summary
    })

# ---------------- Swagger ----------------
SWAGGER_URL = '/docs'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Notes App"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# ---------------- Initialize DB ----------------
if __name__ == '__main__':
    with app.app_context():
        # Drop and create DB if needed
        db.create_all()
    app.run(debug=True)










# from flask import Flask, request, jsonify, render_template
# from flask_sqlalchemy import SQLAlchemy
# from flask_swagger_ui import get_swaggerui_blueprint
# from werkzeug.security import generate_password_hash, check_password_hash
# from functools import wraps
# import jwt
# import datetime
# import os
# import subprocess

# app = Flask(__name__)
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, 'notes.db')
# app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = 'your_secret_key_here'

# db = SQLAlchemy(app)

# # ---------------- Models ----------------
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(50), unique=True, nullable=False)
#     password = db.Column(db.String(200), nullable=False)

# class Note(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100))
#     content = db.Column(db.Text)
#     category = db.Column(db.String(50))
#     pinned = db.Column(db.Boolean, default=False)
#     summary = db.Column(db.Text, nullable=True)  # <-- NEW column for AI summary
#     timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# # ---------------- Token decorator ----------------
# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
#         auth_header = request.headers.get('Authorization')
#         if auth_header and auth_header.startswith('Bearer '):
#             token = auth_header.split(' ')[1]
#         if not token:
#             return jsonify({'message': 'Token missing!'}), 401
#         try:
#             data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
#             current_user = User.query.get(data['id'])
#         except Exception as e:
#             return jsonify({'message': 'Invalid token!', 'error': str(e)}), 401
#         return f(current_user, *args, **kwargs)
#     return decorated

# # ---------------- Auth Routes ----------------
# @app.route('/')
# def home():
#     return render_template('login.html')

# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     user = User.query.filter_by(username=data['username']).first()
#     if not user or not check_password_hash(user.password, data['password']):
#         return jsonify({'message': 'Invalid credentials'}), 401

#     token = jwt.encode(
#         {'id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=5)},
#         app.config['SECRET_KEY'],
#         algorithm="HS256"
#     )
#     return jsonify({'token': token, 'username': user.username})

# @app.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()
#     if not data or not data.get('username') or not data.get('password'):
#         return jsonify({'message': 'Username and password required!'}), 400

#     if User.query.filter_by(username=data['username']).first():
#         return jsonify({'message': 'Username already exists!'}), 400

#     hashed_pw = generate_password_hash(data['password'], method='pbkdf2:sha256', salt_length=8)
#     new_user = User(username=data['username'], password=hashed_pw)
#     db.session.add(new_user)
#     db.session.commit()

#     return jsonify({'message': 'User registered successfully!'}), 201

# # ---------------- AI Summary ----------------
# def generate_summary(note_content):
#     if not note_content:
#         return None
#     result = subprocess.run(
#         ['gemini', f'Summarize the following note: {note_content}'],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True
#     )
#     return result.stdout.strip() if result.returncode == 0 else None

# # ---------------- Notes Routes ----------------
# @app.route('/notes-page')
# def notes_page():
#     return render_template('notes.html')

# @app.route('/notes', methods=['GET'])
# @token_required
# def get_notes(current_user):
#     category = request.args.get('category')
#     search = request.args.get('search', '').lower()

#     query = Note.query.filter_by(user_id=current_user.id)
#     if category:
#         query = query.filter_by(category=category)
#     notes = query.order_by(Note.pinned.desc(), Note.timestamp.desc()).all()
#     if search:
#         notes = [n for n in notes if search in n.title.lower() or search in n.content.lower()]

#     return jsonify([{
#         'id': n.id,
#         'title': n.title,
#         'content': n.content,
#         'category': n.category,
#         'pinned': n.pinned,
#         'summary': n.summary,  # include summary
#         'timestamp': n.timestamp
#     } for n in notes])

# @app.route('/notes', methods=['POST'])
# @token_required
# def create_note(current_user):
#     data = request.get_json()
#     title = data.get('title')
#     content = data.get('content')
#     category = data.get('category', 'General')
#     pinned = data.get('pinned', False)

#     # Generate AI summary
#     summary = generate_summary(content)

#     new_note = Note(
#         title=title,
#         content=content,
#         category=category,
#         pinned=pinned,
#         summary=summary,  # store AI summary
#         user_id=current_user.id
#     )
#     db.session.add(new_note)
#     db.session.commit()

#     return jsonify({
#         'message': 'Note created successfully!',
#         'summary': summary  # optional: return AI summary
#     })

# # ---------------- Swagger ----------------
# SWAGGER_URL = '/docs'
# API_URL = '/static/swagger.json'

# swaggerui_blueprint = get_swaggerui_blueprint(
#     SWAGGER_URL,
#     API_URL,
#     config={
#         'app_name': "Notes App"
#     }
# )
# app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# # ---------------- Initialize DB ----------------
# if __name__ == '__main__':
#     with app.app_context():
#         # Safe migration for summary column
#         try:
#             db.engine.execute("ALTER TABLE note ADD COLUMN summary TEXT;")
#         except Exception as e:
#             print("Column 'summary' might already exist:", e)
#         db.create_all()
#     app.run(debug=True)











# from flask import Flask, request, jsonify, render_template
# from flask_sqlalchemy import SQLAlchemy
# from flask_swagger_ui import get_swaggerui_blueprint
# from werkzeug.security import generate_password_hash, check_password_hash
# from functools import wraps
# import jwt
# import datetime
# import os

# app = Flask(__name__)
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, 'notes.db')
# app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = 'your_secret_key_here'

# db = SQLAlchemy(app)

# # ---------------- Models ----------------
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(50), unique=True, nullable=False)
#     password = db.Column(db.String(200), nullable=False)

# class Note(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100))
#     content = db.Column(db.Text)
#     category = db.Column(db.String(50))
#     pinned = db.Column(db.Boolean, default=False)
#     timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# # ---------------- Token decorator ----------------
# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
#         auth_header = request.headers.get('Authorization')
#         if auth_header and auth_header.startswith('Bearer '):
#             token = auth_header.split(' ')[1]
#         if not token:
#             return jsonify({'message': 'Token missing!'}), 401
#         try:
#             data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
#             current_user = User.query.get(data['id'])
#         except Exception as e:
#             return jsonify({'message': 'Invalid token!', 'error': str(e)}), 401
#         return f(current_user, *args, **kwargs)
#     return decorated

# # ---------------- Auth Routes ----------------
# @app.route('/')
# def home():
#     return render_template('login.html')

# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     user = User.query.filter_by(username=data['username']).first()
#     if not user or not check_password_hash(user.password, data['password']):
#         return jsonify({'message': 'Invalid credentials'}), 401

#     token = jwt.encode(
#         {'id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=5)},
#         app.config['SECRET_KEY'],
#         algorithm="HS256"
#     )
#     return jsonify({'token': token, 'username': user.username})

# @app.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()
#     if not data or not data.get('username') or not data.get('password'):
#         return jsonify({'message': 'Username and password required!'}), 400

#     if User.query.filter_by(username=data['username']).first():
#         return jsonify({'message': 'Username already exists!'}), 400

#     hashed_pw = generate_password_hash(data['password'], method='pbkdf2:sha256', salt_length=8)
#     new_user = User(username=data['username'], password=hashed_pw)
#     db.session.add(new_user)
#     db.session.commit()

#     return jsonify({'message': 'User registered successfully!'}), 201

# # ---------------- Notes Routes ----------------
# @app.route('/notes-page')
# def notes_page():
#     return render_template('notes.html')

# @app.route('/notes', methods=['GET'])
# @token_required
# def get_notes(current_user):
#     category = request.args.get('category')
#     search = request.args.get('search', '').lower()

#     query = Note.query.filter_by(user_id=current_user.id)
#     if category:
#         query = query.filter_by(category=category)
#     notes = query.order_by(Note.pinned.desc(), Note.timestamp.desc()).all()
#     if search:
#         notes = [n for n in notes if search in n.title.lower() or search in n.content.lower()]

#     return jsonify([{
#         'id': n.id,
#         'title': n.title,
#         'content': n.content,
#         'category': n.category,
#         'pinned': n.pinned,
#         'timestamp': n.timestamp
#     } for n in notes])

# @app.route('/notes', methods=['POST'])
# @token_required
# def create_note(current_user):
#     data = request.get_json()
#     new_note = Note(
#         title=data.get('title'),
#         content=data.get('content'),
#         category=data.get('category', 'General'),
#         pinned=data.get('pinned', False),
#         user_id=current_user.id
#     )
#     db.session.add(new_note)
#     db.session.commit()
#     return jsonify({'message': 'Note created successfully!'})

# SWAGGER_URL = '/docs'
# API_URL = '/static/swagger.json'

# swaggerui_blueprint = get_swaggerui_blueprint(
#     SWAGGER_URL,
#     API_URL,
#     config={
#         'app_name': "Notes App"
#     }
# )
# app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
# # ---------------- Initialize DB ----------------
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
