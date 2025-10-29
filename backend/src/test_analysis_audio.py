import base64
import os
import sys
import json
import logging

# Adicionar o diretório pai ao path para importações relativas funcionarem
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.posture_analysis_v2 import analyze_posture_quick_v2
from services.audio_generator import generate_and_save_exercise_audio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Imagem de teste simulada (um placeholder preto)
# Na prática, precisaria de uma imagem real para landmarks
def create_dummy_image_base64():
    """Cria uma imagem preta de 400x600 e retorna em base64."""
    from PIL import Image
    from io import BytesIO
    
    img = Image.new('RGB', (400, 600), color = 'black')
    
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return "data:image/jpeg;base64," + img_str

def simulate_analysis_and_audio_generation():
    logger.info("Iniciando simulação de análise postural e geração de áudio.")
    
    # 1. Simular a análise postural
    # Usando uma imagem dummy, a análise real falhará ou retornará resultados padrão.
    # Para o teste do áudio, vamos simular um resultado com fatores de risco.
    
    # A função analyze_posture_quick_v2 espera uma imagem real com landmarks.
    # Como não temos uma imagem real com pessoa, vamos simular o resultado
    # da análise para testar a função de geração de áudio.
    
    # 2. Simular o resultado da análise (incluindo fatores de risco)
    simulated_metrics = {
        "overall_posture_score": 65.0,
        "posture_classification": "Regular",
        "risk_factors": [
            {
                "factor": "Projeção anterior da cabeça",
                "severity": "Alto",
                "description": "Pode causar dores no pescoço e tensão muscular (Vista Lateral)"
            },
            {
                "factor": "Assimetria dos Ombros",
                "severity": "Médio",
                "description": "Diferença de altura entre os ombros, sugerindo desequilíbrio (Vista Frontal/Posterior)"
            }
        ]
    }
    
    user_id = "test_user_123"
    
    # 3. Gerar e salvar o áudio
    audio_path = generate_and_save_exercise_audio(simulated_metrics['risk_factors'], user_id)
    
    if audio_path:
        logger.info(f"Caminho do áudio gerado (relativo): {audio_path}")
        
        # Verificar se o arquivo foi realmente criado
        full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), audio_path)
        
        if os.path.exists(full_path):
            logger.info(f"SUCESSO: Arquivo de áudio encontrado em: {full_path}")
            logger.info(f"Tamanho do arquivo: {os.path.getsize(full_path)} bytes")
            # O arquivo deve ter um tamanho razoável para um MP3
            if os.path.getsize(full_path) > 10000: # Mais de 10 KB
                 logger.info("SUCESSO: O arquivo de áudio parece válido (tamanho > 10KB).")
            else:
                 logger.error("FALHA: O arquivo de áudio é muito pequeno. A geração pode ter falhado.")
                 
            # Limpar o arquivo de teste
            os.remove(full_path)
            logger.info("Arquivo de áudio de teste removido.")
        else:
            logger.error("FALHA: Arquivo de áudio não encontrado no sistema de arquivos.")
            
    else:
        logger.error("FALHA: A função generate_and_save_exercise_audio retornou None.")

if __name__ == "__main__":
    # Garantir que o diretório de uploads exista
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads', 'exercise_audio')
    os.makedirs(upload_dir, exist_ok=True)
    
    simulate_analysis_and_audio_generation()
