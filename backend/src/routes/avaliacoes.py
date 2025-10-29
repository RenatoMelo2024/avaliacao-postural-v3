from flask import Blueprint, request, jsonify
from src.models.user import db, AvaliacaoPostural, Estudante
from src.routes.auth import token_required
from datetime import datetime
import json

avaliacoes_bp = Blueprint('avaliacoes', __name__)

@avaliacoes_bp.route('/', methods=['GET'])
@token_required
def listar_avaliacoes(current_user):
    try:
        estudante_id = request.args.get('estudante_id')
        
        if estudante_id:
            # Verificar se o usuário tem permissão para ver as avaliações deste estudante
            estudante = Estudante.query.get(estudante_id)
            if not estudante:
                return jsonify({'message': 'Estudante não encontrado!'}), 404
            
            if (current_user.tipo_usuario == 'estudante' and 
                estudante.id_usuario != current_user.id):
                return jsonify({'message': 'Acesso negado!'}), 403
            
            avaliacoes = AvaliacaoPostural.query.filter_by(id_estudante=estudante_id).all()
        else:
            # Listar todas as avaliações baseado no tipo de usuário
            if current_user.tipo_usuario == 'admin':
                avaliacoes = AvaliacaoPostural.query.all()
            elif current_user.tipo_usuario in ['profissional_saude', 'gestor_educacional']:
                avaliacoes = AvaliacaoPostural.query.all()  # Simplificado por enquanto
            else:
                # Estudantes só veem suas próprias avaliações
                estudante = Estudante.query.filter_by(id_usuario=current_user.id).first()
                if estudante:
                    avaliacoes = AvaliacaoPostural.query.filter_by(id_estudante=estudante.id).all()
                else:
                    avaliacoes = []
        
        return jsonify({
            'avaliacoes': [avaliacao.to_dict() for avaliacao in avaliacoes]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao listar avaliações: {str(e)}'}), 500

@avaliacoes_bp.route('/', methods=['POST'])
@token_required
def criar_avaliacao(current_user):
    try:
        # Apenas profissionais de saúde podem criar avaliações
        if current_user.tipo_usuario not in ['admin', 'profissional_saude']:
            return jsonify({'message': 'Acesso negado! Apenas profissionais de saúde podem criar avaliações.'}), 403
        
        data = request.get_json()
        
        # Validação dos dados
        if not data.get('id_estudante'):
            return jsonify({'message': 'ID do estudante é obrigatório!'}), 400
        
        # Verificar se o estudante existe
        estudante = Estudante.query.get(data['id_estudante'])
        if not estudante:
            return jsonify({'message': 'Estudante não encontrado!'}), 404
        
        # Criar nova avaliação
        nova_avaliacao = AvaliacaoPostural(
            id_estudante=data['id_estudante'],
            imagem_frontal_url=data.get('imagem_frontal_url'),
            imagem_lateral_url=data.get('imagem_lateral_url'),
            imagem_posterior_url=data.get('imagem_posterior_url'),
            dados_alinhamento_json=json.dumps(data.get('dados_alinhamento', {})),
            observacoes=data.get('observacoes'),
            profissional_id=current_user.id
        )
        
        db.session.add(nova_avaliacao)
        db.session.commit()
        
        return jsonify({
            'message': 'Avaliação criada com sucesso!',
            'avaliacao': nova_avaliacao.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao criar avaliação: {str(e)}'}), 500

@avaliacoes_bp.route('/<int:avaliacao_id>', methods=['GET'])
@token_required
def obter_avaliacao(current_user, avaliacao_id):
    try:
        avaliacao = AvaliacaoPostural.query.get(avaliacao_id)
        
        if not avaliacao:
            return jsonify({'message': 'Avaliação não encontrada!'}), 404
        
        # Verificar permissões
        if current_user.tipo_usuario == 'estudante':
            estudante = Estudante.query.filter_by(id_usuario=current_user.id).first()
            if not estudante or avaliacao.id_estudante != estudante.id:
                return jsonify({'message': 'Acesso negado!'}), 403
        
        return jsonify({
            'avaliacao': avaliacao.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao obter avaliação: {str(e)}'}), 500

@avaliacoes_bp.route('/<int:avaliacao_id>', methods=['PUT'])
@token_required
def atualizar_avaliacao(current_user, avaliacao_id):
    try:
        # Apenas profissionais de saúde podem atualizar avaliações
        if current_user.tipo_usuario not in ['admin', 'profissional_saude']:
            return jsonify({'message': 'Acesso negado!'}), 403
        
        avaliacao = AvaliacaoPostural.query.get(avaliacao_id)
        
        if not avaliacao:
            return jsonify({'message': 'Avaliação não encontrada!'}), 404
        
        data = request.get_json()
        
        # Atualizar campos
        if 'imagem_frontal_url' in data:
            avaliacao.imagem_frontal_url = data['imagem_frontal_url']
        if 'imagem_lateral_url' in data:
            avaliacao.imagem_lateral_url = data['imagem_lateral_url']
        if 'imagem_posterior_url' in data:
            avaliacao.imagem_posterior_url = data['imagem_posterior_url']
        if 'dados_alinhamento' in data:
            avaliacao.dados_alinhamento_json = json.dumps(data['dados_alinhamento'])
        if 'observacoes' in data:
            avaliacao.observacoes = data['observacoes']
        if 'relatorio_pdf_url' in data:
            avaliacao.relatorio_pdf_url = data['relatorio_pdf_url']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Avaliação atualizada com sucesso!',
            'avaliacao': avaliacao.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao atualizar avaliação: {str(e)}'}), 500

@avaliacoes_bp.route('/<int:avaliacao_id>', methods=['DELETE'])
@token_required
def deletar_avaliacao(current_user, avaliacao_id):
    try:
        # Apenas admins e profissionais de saúde podem deletar avaliações
        if current_user.tipo_usuario not in ['admin', 'profissional_saude']:
            return jsonify({'message': 'Acesso negado!'}), 403
        
        avaliacao = AvaliacaoPostural.query.get(avaliacao_id)
        
        if not avaliacao:
            return jsonify({'message': 'Avaliação não encontrada!'}), 404
        
        db.session.delete(avaliacao)
        db.session.commit()
        
        return jsonify({'message': 'Avaliação deletada com sucesso!'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Erro ao deletar avaliação: {str(e)}'}), 500

@avaliacoes_bp.route('/upload-imagem', methods=['POST'])
@token_required
def upload_imagem(current_user):
    try:
        # Apenas profissionais de saúde podem fazer upload de imagens
        if current_user.tipo_usuario not in ['admin', 'profissional_saude']:
            return jsonify({'message': 'Acesso negado!'}), 403
        
        # Verificar se há arquivo na requisição
        if 'imagem' not in request.files:
            return jsonify({'message': 'Nenhuma imagem foi enviada!'}), 400
        
        arquivo = request.files['imagem']
        
        if arquivo.filename == '':
            return jsonify({'message': 'Nenhuma imagem foi selecionada!'}), 400
        
        # Verificar extensão do arquivo
        extensoes_permitidas = {'png', 'jpg', 'jpeg', 'gif'}
        if not ('.' in arquivo.filename and 
                arquivo.filename.rsplit('.', 1)[1].lower() in extensoes_permitidas):
            return jsonify({'message': 'Formato de arquivo não permitido!'}), 400
        
        # Salvar arquivo (implementação simplificada)
        # Em produção, usar serviços como AWS S3, Google Cloud Storage, etc.
        import os
        from werkzeug.utils import secure_filename
        
        upload_folder = '/home/ubuntu/postural_assessment_api/uploads'
        os.makedirs(upload_folder, exist_ok=True)
        
        filename = secure_filename(arquivo.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        filepath = os.path.join(upload_folder, filename)
        arquivo.save(filepath)
        
        # Retornar URL da imagem
        image_url = f'/uploads/{filename}'
        
        return jsonify({
            'message': 'Imagem enviada com sucesso!',
            'url': image_url
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro ao fazer upload da imagem: {str(e)}'}), 500

