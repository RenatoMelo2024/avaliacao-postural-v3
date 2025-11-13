from flask import Blueprint, request, jsonify, current_app
from src.models.user import db, User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Inicializar JWTManager no main.py e usar aqui
# A chave secreta é configurada no main.py através do app.config['JWT_SECRET_KEY']

def init_jwt(app):
    JWTManager(app)

# Decorador personalizado para obter o usuário atual
def get_current_user_from_jwt():
    user_id = get_jwt_identity()
    return User.query.get(user_id)

def token_required(f):
    @jwt_required()
    @wraps(f)
    def decorated(*args, **kwargs):
        current_user = get_current_user_from_jwt()
        if current_user is None:
            return jsonify({'message': 'Token inválido ou usuário não encontrado!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validação dos dados
        if not data.get('nome') or not data.get('email') or not data.get('senha'):
            return jsonify({'message': 'Nome, email e senha são obrigatórios!'}), 400
        
        # Verificar se o usuário já existe
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email já cadastrado!'}), 400
        
        # Criar novo usuário
        novo_usuario = User(
            nome=data['nome'],
            email=data['email'],
            tipo_usuario=data.get('tipo_usuario', 'estudante')
        )
        novo_usuario.set_password(data['senha'])
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        return jsonify({
            'message': 'Usuário criado com sucesso!',
            'usuario': novo_usuario.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao criar usuário: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('senha'):
            return jsonify({'message': 'Email e senha são obrigatórios!'}), 400
        
        usuario = User.query.filter_by(email=data['email']).first()
        
        if not usuario or not usuario.check_password(data['senha']):
            return jsonify({'message': 'Credenciais inválidas!'}), 401
        
        if not usuario.ativo:
            return jsonify({'message': 'Usuário inativo!'}), 401
        
        # Gerar token JWT
        access_token = create_access_token(identity=usuario.id)
        
        return jsonify({
            'message': 'Login realizado com sucesso!',
            'token': access_token,
            'usuario': usuario.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro no login: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    return jsonify({
        'usuario': current_user.to_dict()
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    # Em uma implementação mais robusta, você poderia adicionar o token a uma blacklist
    return jsonify({'message': 'Logout realizado com sucesso!'}), 200

