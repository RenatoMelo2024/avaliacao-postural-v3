import os
from openai import OpenAI
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

# O segredo OPENAI_API_KEY está disponível no ambiente
client = OpenAI()

def generate_audio_for_exercise(text: str, output_path: str, voice: str = "nova") -> Optional[str]:
    """
    Gera um arquivo de áudio MP3 a partir de um texto usando o OpenAI TTS.

    Args:
        text (str): O texto da narrativa do exercício.
        output_path (str): O caminho completo para salvar o arquivo MP3.
        voice (str): A voz a ser usada (e.g., 'alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer').

    Returns:
        Optional[str]: O caminho do arquivo gerado se for bem-sucedido, senão None.
    """
    try:
        logger.info(f"Gerando áudio para o texto: {text[:50]}...")
        
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        # Salvar o áudio no caminho especificado
        response.stream_to_file(output_path)
        
        logger.info(f"Áudio gerado com sucesso em: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Erro ao gerar áudio TTS: {str(e)}")
        return None

def generate_exercise_narrative(risk_factors: List[Dict]) -> str:
    """
    Gera uma narrativa de exercício baseada nos fatores de risco identificados.
    
    Args:
        risk_factors (List[Dict]): Lista de fatores de risco do relatório de análise.
        
    Returns:
        str: A narrativa completa do exercício.
    """
    if not risk_factors:
        return "Parabéns, sua postura está excelente! Mantenha os bons hábitos posturais."

    narrative = "Com base na sua avaliação postural, vamos começar com um exercício focado nas suas áreas de atenção. "
    
    # Mapeamento de fatores de risco para exercícios sugeridos
    exercise_map = {
        "Projeção anterior da cabeça": "Para a projeção anterior da cabeça, vamos fazer um exercício de retração cervical. Sente-se ou fique em pé com a coluna reta. Lentamente, deslize o queixo para trás, como se estivesse fazendo um 'queixo duplo', mantendo o olhar para a frente. Segure por cinco segundos e relaxe. Repita dez vezes. Isso ajuda a realinhar a cabeça e fortalecer os músculos profundos do pescoço.",
        "Assimetria dos Ombros": "Para a assimetria dos ombros, faremos o alongamento do trapézio superior. Incline a cabeça para o lado oposto do ombro mais alto, usando a mão para aplicar uma leve pressão. Você deve sentir o alongamento na lateral do pescoço. Mantenha por vinte segundos em cada lado. Este exercício ajuda a equilibrar a altura dos ombros.",
        "Assimetria Pélvica": "Para a assimetria pélvica, vamos fortalecer o glúteo médio. Deite-se de lado, com os joelhos dobrados e os pés juntos. Mantenha os pés em contato e levante o joelho superior, como se fosse abrir uma concha. Mantenha o movimento lento e controlado, sem girar o tronco. Faça quinze repetições em cada lado.",
        "Desvio de Eixo dos Joelhos": "Para o desvio dos joelhos, faremos agachamento isométrico com faixa. Coloque uma faixa elástica logo acima dos joelhos. Agache lentamente até um ângulo de quarenta e cinco graus, empurrando os joelhos contra a faixa para ativar os glúteos. Mantenha a posição por trinta segundos. Este exercício estabiliza os joelhos e melhora o alinhamento."
    }
    
    # Selecionar o exercício mais relevante (o primeiro fator de risco)
    main_risk = risk_factors[0]['factor']
    
    if main_risk in exercise_map:
        narrative += f"Seu principal ponto de atenção é: **{main_risk}**. O exercício que faremos é: {exercise_map[main_risk]}"
    else:
        narrative += "Seu principal ponto de atenção é o alinhamento geral. Vamos fazer uma 'postura da montanha' para consciência corporal. Fique em pé, distribua o peso igualmente nos pés, relaxe os ombros, e imagine um fio puxando o topo da sua cabeça para o céu. Mantenha esta postura por um minuto, respirando profundamente."
        
    narrative += " Lembre-se de respirar profundamente durante todo o exercício. Vamos lá!"
    
    return narrative

def generate_and_save_exercise_audio(risk_factors: List[Dict], user_id: str) -> Optional[str]:
    """
    Gera a narrativa e o áudio do exercício, salvando-o na pasta de uploads.
    """
    narrative = generate_exercise_narrative(risk_factors)
    
    # Definir o caminho para salvar o arquivo de áudio
    # Usar a pasta de uploads existente
    upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'exercise_audio')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Nome do arquivo baseado no user_id e timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"exercise_audio_{user_id}_{timestamp}.mp3"
    output_path = os.path.join(upload_dir, filename)
    
    audio_path = generate_audio_for_exercise(narrative, output_path)
    
    if audio_path:
        # Retornar o caminho relativo ou o nome do arquivo para ser armazenado no banco de dados
        return os.path.join('uploads', 'exercise_audio', filename)
    else:
        return None

# Importar datetime para uso na função generate_and_save_exercise_audio
from datetime import datetime
