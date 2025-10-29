from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO
import sqlite3
from ..services.posture_analysis_v2 import posture_analyzer_v2 as posture_analyzer
from ..models.user import User
from ..services.audio_generator import generate_and_save_exercise_audio

posture_bp = Blueprint('posture', __name__)

def get_db_connection():
    """Conecta ao banco de dados SQLite"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'app.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

UPLOAD_FOLDER = 'uploads/posture_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Criar diretório de upload se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@posture_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_posture():
    """
    Endpoint para análise postural
    Aceita imagem via upload de arquivo ou base64
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Verificar se é upload de arquivo ou base64
        if 'image' in request.files:
            # Upload de arquivo
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
            
            if file and allowed_file(file.filename):
                # Salvar arquivo temporariamente
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                # Carregar imagem
                image = cv2.imread(filepath)
                if image is None:
                    return jsonify({'error': 'Erro ao carregar imagem'}), 400
                
                # Analisar postura
                analysis_result = posture_analyzer.analyze_posture(image)
        
        # Geração do áudio do exercício
        if 'risk_factors' in analysis_result['metrics']:
            audio_path = generate_and_save_exercise_audio(analysis_result['metrics']['risk_factors'], current_user_id)
            analysis_result['exercise_audio_path'] = audio_path
        else:
            analysis_result['exercise_audio_path'] = None
                
                # Remover arquivo temporário
                os.remove(filepath)
                
        elif 'image_base64' in request.json:
            # Imagem em base64
            image_base64 = request.json['image_base64']
            analysis_result = posture_analyzer.analyze_posture_from_base64(image_base64)
            
            # Geração do áudio do exercício
            if 'risk_factors' in analysis_result['metrics']:
                audio_path = generate_and_save_exercise_audio(analysis_result['metrics']['risk_factors'], current_user_id)
                analysis_result['exercise_audio_path'] = audio_path
            else:
                analysis_result['exercise_audio_path'] = None
            
        else:
            return jsonify({'error': 'Imagem não fornecida'}), 400
        
        if 'error' in analysis_result:
            return jsonify(analysis_result), 400
        
        # Salvar resultado no banco de dados
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Dados adicionais do request
        estudante_id = request.json.get('estudante_id') if request.json else None
        observacoes = request.json.get('observacoes', '') if request.json else ''
        
        cursor.execute('''
            INSERT INTO avaliacao (
                usuario_id, estudante_id, imagem_original, imagem_anotada,
                score_geral, classificacao_postura, metricas_detalhadas,
                relatorio_completo, observacoes, audio_exercicio_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            current_user_id,
            estudante_id,
            request.json.get('image_base64', '') if request.json else '',
            analysis_result['annotated_image'],
            analysis_result['metrics']['overall_posture_score'],
            analysis_result['metrics']['posture_classification'],
            str(analysis_result['metrics']),
            str(analysis_result['report']),
            observacoes,
            analysis_result.get('exercise_audio_path')
        ))
        
        avaliacao_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Adicionar ID da avaliação ao resultado
        analysis_result['avaliacao_id'] = avaliacao_id
        
        return jsonify(analysis_result), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@posture_bp.route('/history', methods=['GET'])
@jwt_required()
def get_posture_history():
    """
    Retorna o histórico de avaliações posturais do usuário
    """
    try:
        current_user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Buscar avaliações do usuário
        cursor.execute('''
            SELECT a.*, e.nome as estudante_nome
            FROM avaliacao a
            LEFT JOIN estudante e ON a.estudante_id = e.id
            WHERE a.usuario_id = ?
            ORDER BY a.data_criacao DESC
        ''', (current_user_id,))
        
        avaliacoes = []
        for row in cursor.fetchall():
            avaliacao = {
                'id': row[0],
                'estudante_id': row[2],
                'estudante_nome': row[-1],
                'data_criacao': row[3],
                'score_geral': row[6],
                'classificacao_postura': row[7],
                'observacoes': row[10]
            }
            avaliacoes.append(avaliacao)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'avaliacoes': avaliacoes
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@posture_bp.route('/details/<int:avaliacao_id>', methods=['GET'])
@jwt_required()
def get_posture_details(avaliacao_id):
    """
    Retorna detalhes completos de uma avaliação específica
    """
    try:
        current_user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Buscar avaliação específica
        cursor.execute('''
            SELECT a.*, e.nome as estudante_nome, u.nome as avaliador_nome
            FROM avaliacao a
            LEFT JOIN estudante e ON a.estudante_id = e.id
            LEFT JOIN user u ON a.usuario_id = u.id
            WHERE a.id = ? AND a.usuario_id = ?
        ''', (avaliacao_id, current_user_id))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'error': 'Avaliação não encontrada'}), 404
        
        # Converter strings de volta para objetos Python
        import ast
        try:
            metricas = ast.literal_eval(row[8]) if row[8] else {}
            relatorio = ast.literal_eval(row[9]) if row[9] else {}
        except:
            metricas = {}
            relatorio = {}
        
        avaliacao_detalhada = {
            'id': row[0],
            'usuario_id': row[1],
            'estudante_id': row[2],
            'data_criacao': row[3],
            'imagem_original': row[4],
            'imagem_anotada': row[5],
            'score_geral': row[6],
            'classificacao_postura': row[7],
            'metricas_detalhadas': metricas,
            'relatorio_completo': relatorio,
            'observacoes': row[10],
            'audio_exercicio_path': row[11],
            'estudante_nome': row[-2],
            'avaliador_nome': row[-1]
        }
        
        conn.close()
        
        return jsonify({
            'success': True,
            'avaliacao': avaliacao_detalhada
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@posture_bp.route('/compare', methods=['POST'])
@jwt_required()
def compare_postures():
    """
    Compara duas avaliações posturais
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        avaliacao1_id = data.get('avaliacao1_id')
        avaliacao2_id = data.get('avaliacao2_id')
        
        if not avaliacao1_id or not avaliacao2_id:
            return jsonify({'error': 'IDs das avaliações são obrigatórios'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Buscar ambas as avaliações
        cursor.execute('''
            SELECT id, data_criacao, score_geral, classificacao_postura, metricas_detalhadas
            FROM avaliacao
            WHERE id IN (?, ?) AND usuario_id = ?
        ''', (avaliacao1_id, avaliacao2_id, current_user_id))
        
        rows = cursor.fetchall()
        if len(rows) != 2:
            return jsonify({'error': 'Uma ou ambas avaliações não foram encontradas'}), 404
        
        # Processar dados das avaliações
        avaliacoes = []
        for row in rows:
            import ast
            try:
                metricas = ast.literal_eval(row[4]) if row[4] else {}
            except:
                metricas = {}
            
            avaliacoes.append({
                'id': row[0],
                'data_criacao': row[1],
                'score_geral': row[2],
                'classificacao_postura': row[3],
                'metricas': metricas
            })
        
        # Ordenar por ID para manter consistência
        avaliacoes.sort(key=lambda x: x['id'])
        
        # Calcular comparação
        comparacao = {
            'avaliacao_anterior': avaliacoes[0],
            'avaliacao_atual': avaliacoes[1],
            'evolucao': {
                'score_geral': avaliacoes[1]['score_geral'] - avaliacoes[0]['score_geral'],
                'melhorou': avaliacoes[1]['score_geral'] > avaliacoes[0]['score_geral'],
                'areas_melhoradas': [],
                'areas_pioradas': []
            }
        }
        
        # Comparar métricas específicas
        metricas_anteriores = avaliacoes[0]['metricas']
        metricas_atuais = avaliacoes[1]['metricas']
        
        metricas_comparar = ['head_alignment_score', 'shoulder_alignment_score', 'vertical_alignment_score']
        
        for metrica in metricas_comparar:
            if metrica in metricas_anteriores and metrica in metricas_atuais:
                diferenca = metricas_atuais[metrica] - metricas_anteriores[metrica]
                if diferenca > 5:  # Melhora significativa
                    comparacao['evolucao']['areas_melhoradas'].append({
                        'area': metrica.replace('_', ' ').title(),
                        'diferenca': diferenca
                    })
                elif diferenca < -5:  # Piora significativa
                    comparacao['evolucao']['areas_pioradas'].append({
                        'area': metrica.replace('_', ' ').title(),
                        'diferenca': diferenca
                    })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'comparacao': comparacao
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

