import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.estudantes import estudantes_bp
from src.routes.avaliacoes import avaliacoes_bp
from src.routes.escolas import escolas_bp
from src.routes.sessoes_rv import sessoes_rv_bp
from src.routes.posture_analysis import posture_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Habilitar CORS para todas as rotas
CORS(app)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(estudantes_bp, url_prefix='/api/estudantes')
app.register_blueprint(avaliacoes_bp, url_prefix='/api/avaliacoes')
app.register_blueprint(escolas_bp, url_prefix='/api/escolas')
app.register_blueprint(sessoes_rv_bp, url_prefix='/api/sessoes-rv')
app.register_blueprint(posture_bp, url_prefix='/api/posture')

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Criar diretório de uploads
uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
os.makedirs(uploads_dir, exist_ok=True)

# Servir arquivos de upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(uploads_dir, filename)

with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
