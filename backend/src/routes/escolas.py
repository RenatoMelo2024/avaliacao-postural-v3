from flask import Blueprint, request, jsonify
from src.models.user import db, Escola
from src.routes.auth import token_required

escolas_bp = Blueprint('escolas', __name__)

@escolas_bp.route('/', methods=['GET'])
@token_required
def listar_escolas(current_user):
    try:
        escolas = Escola.query.all()
        
        return jsonify({
            'escolas': [escola.to_dict() for escola in escolas]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao listar escolas: {str(e)}'}), 500

@escolas_bp.route('/', methods=['POST'])
@token_required
def criar_escola(current_user):
    try:
        # Apenas admins e gestores educacionais podem criar escolas
        if current_user.tipo_usuario not in ['admin', 'gestor_educacional']:
            return jsonify({'message': 'Acesso negado!'}), 403
        
        data = request.get_json()
        
        # Validação dos dados
        if not data.get('nome'):
            return jsonify({'message': 'Nome da escola é obrigatório!'}), 400
        
        # Criar nova escola
        nova_escola = Escola(
            nome=data['nome'],
            endereco=data.get('endereco'),
            telefone=data.get('telefone'),
            email=data.get('email')
        )
        
        db.session.add(nova_escola)
        db.session.commit()
        
        return jsonify({
            'message': 'Escola criada com sucesso!',
            'escola': nova_escola.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao criar escola: {str(e)}'}), 500

@escolas_bp.route('/<int:escola_id>', methods=['GET'])
@token_required
def obter_escola(current_user, escola_id):
    try:
        escola = Escola.query.get(escola_id)
        
        if not escola:
            return jsonify({'message': 'Escola não encontrada!'}), 404
        
        return jsonify({
            'escola': escola.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao obter escola: {str(e)}'}), 500

@escolas_bp.route('/<int:escola_id>', methods=['PUT'])
@token_required
def atualizar_escola(current_user, escola_id):
    try:
        # Apenas admins e gestores educacionais podem atualizar escolas
        if current_user.tipo_usuario not in ['admin', 'gestor_educacional']:
            return jsonify({'message': 'Acesso negado!'}), 403
        
        escola = Escola.query.get(escola_id)
        
        if not escola:
            return jsonify({'message': 'Escola não encontrada!'}), 404
        
        data = request.get_json()
        
        # Atualizar campos
        if 'nome' in data:
            escola.nome = data['nome']
        if 'endereco' in data:
            escola.endereco = data['endereco']
        if 'telefone' in data:
            escola.telefone = data['telefone']
        if 'email' in data:
            escola.email = data['email']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Escola atualizada com sucesso!',
            'escola': escola.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao atualizar escola: {str(e)}'}), 500

@escolas_bp.route('/<int:escola_id>', methods=['DELETE'])
@token_required
def deletar_escola(current_user, escola_id):
    try:
        # Apenas admins podem deletar escolas
        if current_user.tipo_usuario != 'admin':
            return jsonify({'message': 'Acesso negado!'}), 403
        
        escola = Escola.query.get(escola_id)
        
        if not escola:
            return jsonify({'message': 'Escola não encontrada!'}), 404
        
        db.session.delete(escola)
        db.session.commit()
        
        return jsonify({'message': 'Escola deletada com sucesso!'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao deletar escola: {str(e)}'}), 500

