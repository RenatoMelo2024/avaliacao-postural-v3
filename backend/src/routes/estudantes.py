from flask import Blueprint, request, jsonify
from src.models.user import db, Estudante, User, Escola
from src.routes.auth import token_required
from datetime import datetime

estudantes_bp = Blueprint('estudantes', __name__)

@estudantes_bp.route('/', methods=['GET'])
@token_required
def listar_estudantes(current_user):
    try:
        # Filtrar estudantes baseado no tipo de usuário
        if current_user.tipo_usuario == 'admin':
            estudantes = Estudante.query.all()
        elif current_user.tipo_usuario in ['profissional_saude', 'gestor_educacional']:
            # Profissionais podem ver estudantes de suas escolas/clínicas
            estudantes = Estudante.query.all()  # Simplificado por enquanto
        else:
            # Estudantes só veem seus próprios dados
            estudantes = Estudante.query.filter_by(id_usuario=current_user.id).all()
        
        return jsonify({
            'estudantes': [estudante.to_dict() for estudante in estudantes]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao listar estudantes: {str(e)}'}), 500

@estudantes_bp.route('/', methods=['POST'])
@token_required
def criar_estudante(current_user):
    try:
        data = request.get_json()
        
        # Validação dos dados
        if not data.get('nome'):
            return jsonify({'message': 'Nome é obrigatório!'}), 400
        
        # Verificar se o usuário já tem um perfil de estudante
        if current_user.tipo_usuario == 'estudante':
            estudante_existente = Estudante.query.filter_by(id_usuario=current_user.id).first()
            if estudante_existente:
                return jsonify({'message': 'Usuário já possui perfil de estudante!'}), 400
        
        # Criar novo estudante
        novo_estudante = Estudante(
            id_usuario=data.get('id_usuario', current_user.id),
            nome=data['nome'],
            data_nascimento=datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date() if data.get('data_nascimento') else None,
            genero=data.get('genero'),
            escola_id=data.get('escola_id'),
            responsavel_nome=data.get('responsavel_nome'),
            responsavel_telefone=data.get('responsavel_telefone')
        )
        
        db.session.add(novo_estudante)
        db.session.commit()
        
        return jsonify({
            'message': 'Estudante criado com sucesso!',
            'estudante': novo_estudante.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao criar estudante: {str(e)}'}), 500

@estudantes_bp.route('/<int:estudante_id>', methods=['GET'])
@token_required
def obter_estudante(current_user, estudante_id):
    try:
        estudante = Estudante.query.get(estudante_id)
        
        if not estudante:
            return jsonify({'message': 'Estudante não encontrado!'}), 404
        
        # Verificar permissões
        if (current_user.tipo_usuario == 'estudante' and 
            estudante.id_usuario != current_user.id):
            return jsonify({'message': 'Acesso negado!'}), 403
        
        return jsonify({
            'estudante': estudante.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao obter estudante: {str(e)}'}), 500

@estudantes_bp.route('/<int:estudante_id>', methods=['PUT'])
@token_required
def atualizar_estudante(current_user, estudante_id):
    try:
        estudante = Estudante.query.get(estudante_id)
        
        if not estudante:
            return jsonify({'message': 'Estudante não encontrado!'}), 404
        
        # Verificar permissões
        if (current_user.tipo_usuario == 'estudante' and 
            estudante.id_usuario != current_user.id):
            return jsonify({'message': 'Acesso negado!'}), 403
        
        data = request.get_json()
        
        # Atualizar campos
        if 'nome' in data:
            estudante.nome = data['nome']
        if 'data_nascimento' in data:
            estudante.data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
        if 'genero' in data:
            estudante.genero = data['genero']
        if 'escola_id' in data:
            estudante.escola_id = data['escola_id']
        if 'responsavel_nome' in data:
            estudante.responsavel_nome = data['responsavel_nome']
        if 'responsavel_telefone' in data:
            estudante.responsavel_telefone = data['responsavel_telefone']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Estudante atualizado com sucesso!',
            'estudante': estudante.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao atualizar estudante: {str(e)}'}), 500

@estudantes_bp.route('/<int:estudante_id>', methods=['DELETE'])
@token_required
def deletar_estudante(current_user, estudante_id):
    try:
        # Apenas admins e gestores podem deletar estudantes
        if current_user.tipo_usuario not in ['admin', 'gestor_educacional']:
            return jsonify({'message': 'Acesso negado!'}), 403
        
        estudante = Estudante.query.get(estudante_id)
        
        if not estudante:
            return jsonify({'message': 'Estudante não encontrado!'}), 404
        
        db.session.delete(estudante)
        db.session.commit()
        
        return jsonify({'message': 'Estudante deletado com sucesso!'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao deletar estudante: {str(e)}'}), 500

