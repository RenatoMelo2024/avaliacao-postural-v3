from flask import Blueprint, request, jsonify
from src.models.user import db, SessaoRV, Estudante
from src.routes.auth import token_required
import json

sessoes_rv_bp = Blueprint('sessoes_rv', __name__)

@sessoes_rv_bp.route('/', methods=['GET'])
@token_required
def listar_sessoes_rv(current_user):
    try:
        estudante_id = request.args.get('estudante_id')
        
        if estudante_id:
            # Verificar se o usuário tem permissão para ver as sessões deste estudante
            estudante = Estudante.query.get(estudante_id)
            if not estudante:
                return jsonify({'message': 'Estudante não encontrado!'}), 404
            
            if (current_user.tipo_usuario == 'estudante' and 
                estudante.id_usuario != current_user.id):
                return jsonify({'message': 'Acesso negado!'}), 403
            
            sessoes = SessaoRV.query.filter_by(id_estudante=estudante_id).all()
        else:
            # Listar todas as sessões baseado no tipo de usuário
            if current_user.tipo_usuario == 'admin':
                sessoes = SessaoRV.query.all()
            elif current_user.tipo_usuario in ['profissional_saude', 'gestor_educacional']:
                sessoes = SessaoRV.query.all()  # Simplificado por enquanto
            else:
                # Estudantes só veem suas próprias sessões
                estudante = Estudante.query.filter_by(id_usuario=current_user.id).first()
                if estudante:
                    sessoes = SessaoRV.query.filter_by(id_estudante=estudante.id).all()
                else:
                    sessoes = []
        
        return jsonify({
            'sessoes': [sessao.to_dict() for sessao in sessoes]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao listar sessões de RV: {str(e)}'}), 500

@sessoes_rv_bp.route('/', methods=['POST'])
@token_required
def criar_sessao_rv(current_user):
    try:
        data = request.get_json()
        
        # Validação dos dados
        if not data.get('id_estudante') or not data.get('tipo_sessao'):
            return jsonify({'message': 'ID do estudante e tipo de sessão são obrigatórios!'}), 400
        
        # Verificar se o estudante existe
        estudante = Estudante.query.get(data['id_estudante'])
        if not estudante:
            return jsonify({'message': 'Estudante não encontrado!'}), 404
        
        # Verificar permissões
        if current_user.tipo_usuario == 'estudante':
            if estudante.id_usuario != current_user.id:
                return jsonify({'message': 'Acesso negado!'}), 403
        
        # Criar nova sessão de RV
        nova_sessao = SessaoRV(
            id_estudante=data['id_estudante'],
            tipo_sessao=data['tipo_sessao'],
            duracao_minutos=data.get('duracao_minutos'),
            progresso_json=json.dumps(data.get('progresso', {})),
            pontuacao=data.get('pontuacao')
        )
        
        db.session.add(nova_sessao)
        db.session.commit()
        
        return jsonify({
            'message': 'Sessão de RV criada com sucesso!',
            'sessao': nova_sessao.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao criar sessão de RV: {str(e)}'}), 500

@sessoes_rv_bp.route('/<int:sessao_id>', methods=['GET'])
@token_required
def obter_sessao_rv(current_user, sessao_id):
    try:
        sessao = SessaoRV.query.get(sessao_id)
        
        if not sessao:
            return jsonify({'message': 'Sessão de RV não encontrada!'}), 404
        
        # Verificar permissões
        if current_user.tipo_usuario == 'estudante':
            estudante = Estudante.query.filter_by(id_usuario=current_user.id).first()
            if not estudante or sessao.id_estudante != estudante.id:
                return jsonify({'message': 'Acesso negado!'}), 403
        
        return jsonify({
            'sessao': sessao.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao obter sessão de RV: {str(e)}'}), 500

@sessoes_rv_bp.route('/<int:sessao_id>', methods=['PUT'])
@token_required
def atualizar_sessao_rv(current_user, sessao_id):
    try:
        sessao = SessaoRV.query.get(sessao_id)
        
        if not sessao:
            return jsonify({'message': 'Sessão de RV não encontrada!'}), 404
        
        # Verificar permissões
        if current_user.tipo_usuario == 'estudante':
            estudante = Estudante.query.filter_by(id_usuario=current_user.id).first()
            if not estudante or sessao.id_estudante != estudante.id:
                return jsonify({'message': 'Acesso negado!'}), 403
        
        data = request.get_json()
        
        # Atualizar campos
        if 'tipo_sessao' in data:
            sessao.tipo_sessao = data['tipo_sessao']
        if 'duracao_minutos' in data:
            sessao.duracao_minutos = data['duracao_minutos']
        if 'progresso' in data:
            sessao.progresso_json = json.dumps(data['progresso'])
        if 'pontuacao' in data:
            sessao.pontuacao = data['pontuacao']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Sessão de RV atualizada com sucesso!',
            'sessao': sessao.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao atualizar sessão de RV: {str(e)}'}), 500

@sessoes_rv_bp.route('/<int:sessao_id>', methods=['DELETE'])
@token_required
def deletar_sessao_rv(current_user, sessao_id):
    try:
        sessao = SessaoRV.query.get(sessao_id)
        
        if not sessao:
            return jsonify({'message': 'Sessão de RV não encontrada!'}), 404
        
        # Verificar permissões
        if current_user.tipo_usuario == 'estudante':
            estudante = Estudante.query.filter_by(id_usuario=current_user.id).first()
            if not estudante or sessao.id_estudante != estudante.id:
                return jsonify({'message': 'Acesso negado!'}), 403
        elif current_user.tipo_usuario not in ['admin', 'profissional_saude', 'gestor_educacional']:
            return jsonify({'message': 'Acesso negado!'}), 403
        
        db.session.delete(sessao)
        db.session.commit()
        
        return jsonify({'message': 'Sessão de RV deletada com sucesso!'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao deletar sessão de RV: {str(e)}'}), 500

@sessoes_rv_bp.route('/estatisticas/<int:estudante_id>', methods=['GET'])
@token_required
def obter_estatisticas_estudante(current_user, estudante_id):
    try:
        # Verificar se o estudante existe
        estudante = Estudante.query.get(estudante_id)
        if not estudante:
            return jsonify({'message': 'Estudante não encontrado!'}), 404
        
        # Verificar permissões
        if current_user.tipo_usuario == 'estudante':
            if estudante.id_usuario != current_user.id:
                return jsonify({'message': 'Acesso negado!'}), 403
        
        # Obter estatísticas das sessões
        sessoes = SessaoRV.query.filter_by(id_estudante=estudante_id).all()
        
        total_sessoes = len(sessoes)
        total_tempo = sum(s.duracao_minutos or 0 for s in sessoes)
        pontuacao_media = sum(s.pontuacao or 0 for s in sessoes) / total_sessoes if total_sessoes > 0 else 0
        
        sessoes_por_tipo = {}
        for sessao in sessoes:
            tipo = sessao.tipo_sessao
            if tipo not in sessoes_por_tipo:
                sessoes_por_tipo[tipo] = 0
            sessoes_por_tipo[tipo] += 1
        
        return jsonify({
            'estatisticas': {
                'total_sessoes': total_sessoes,
                'total_tempo_minutos': total_tempo,
                'pontuacao_media': round(pontuacao_media, 2),
                'sessoes_por_tipo': sessoes_por_tipo
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao obter estatísticas: {str(e)}'}), 500

