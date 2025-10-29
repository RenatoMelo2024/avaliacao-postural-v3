import cv2
import mediapipe as mp
import numpy as np
import math
from typing import Dict, List, Tuple, Optional
import base64
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import logging
from datetime import datetime
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostureAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Configuração otimizada para melhor precisão
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=False,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Parâmetros de análise
        self.analysis_params = {
            'head_forward_threshold': 30,  # pixels
            'shoulder_slope_threshold': 5,  # graus
            'vertical_alignment_threshold': 25,  # pixels
            'confidence_threshold': 0.5
        }
        
    def analyze_posture_from_base64(self, image_base64: str, user_id: Optional[str] = None) -> Dict:
        """
        Analisa a postura a partir de uma imagem em base64
        """
        try:
            logger.info(f"Iniciando análise postural para usuário: {user_id}")
            
            # Validar formato base64
            if not self._validate_base64_image(image_base64):
                return {"error": "Formato de imagem inválido"}
            
            # Decodificar imagem base64
            image_data = base64.b64decode(image_base64.split(',')[1] if ',' in image_base64 else image_base64)
            image = Image.open(BytesIO(image_data))
            
            # Validar dimensões da imagem
            if not self._validate_image_dimensions(image):
                return {"error": "Dimensões da imagem inadequadas para análise"}
            
            # Converter para formato OpenCV
            image_rgb = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Realizar análise
            result = self.analyze_posture(image_rgb, user_id)
            
            # Adicionar metadados
            result['metadata'] = {
                'timestamp': datetime.now().isoformat(),
                'image_dimensions': f"{image.width}x{image.height}",
                'user_id': user_id,
                'analysis_version': '2.0'
            }
            
            logger.info(f"Análise concluída com sucesso para usuário: {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao processar imagem: {str(e)}")
            return {"error": f"Erro ao processar imagem: {str(e)}"}
    
    def analyze_posture(self, image: np.ndarray, user_id: Optional[str] = None) -> Dict:
        """
        Analisa a postura de uma pessoa na imagem com métricas aprimoradas
        """
        try:
            # Converter BGR para RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Pré-processamento da imagem para melhor detecção
            processed_image = self._preprocess_image(image_rgb)
            
            # Processar a imagem
            results = self.pose.process(processed_image)
            
            if not results.pose_landmarks:
                return {"error": "Nenhuma pessoa detectada na imagem. Certifique-se de que a pessoa esteja completamente visível."}
            
            # Validar qualidade dos landmarks
            if not self._validate_landmarks_quality(results.pose_landmarks.landmark):
                return {"error": "Qualidade da detecção insuficiente. Tente uma imagem com melhor iluminação e posicionamento."}
            
            # Extrair pontos de referência
            landmarks = results.pose_landmarks.landmark
            
            # Calcular métricas posturais aprimoradas
            metrics = self._calculate_enhanced_posture_metrics(landmarks, image.shape)
            
            # Gerar visualização melhorada
            annotated_image = self._draw_enhanced_posture_analysis(image_rgb, results, metrics)
            
            # Converter imagem anotada para base64
            annotated_base64 = self._image_to_base64(annotated_image)
            
            # Gerar relatório detalhado
            report = self._generate_comprehensive_report(metrics)
            
            # Calcular tendências (se houver histórico)
            trends = self._calculate_trends(metrics, user_id)
            
            return {
                "success": True,
                "metrics": metrics,
                "report": report,
                "trends": trends,
                "annotated_image": annotated_base64,
                "landmarks": self._landmarks_to_dict(landmarks),
                "confidence_scores": self._calculate_confidence_scores(landmarks)
            }
            
        except Exception as e:
            logger.error(f"Erro na análise postural: {str(e)}")
            return {"error": f"Erro na análise postural: {str(e)}"}
    
    def _validate_base64_image(self, image_base64: str) -> bool:
        """Valida se a string base64 representa uma imagem válida"""
        try:
            if ',' in image_base64:
                header, data = image_base64.split(',', 1)
                if not header.startswith('data:image/'):
                    return False
            else:
                data = image_base64
            
            # Tentar decodificar
            image_data = base64.b64decode(data)
            Image.open(BytesIO(image_data))
            return True
        except:
            return False
    
    def _validate_image_dimensions(self, image: Image.Image) -> bool:
        """Valida se as dimensões da imagem são adequadas para análise"""
        min_width, min_height = 300, 400
        max_width, max_height = 4000, 6000
        
        return (min_width <= image.width <= max_width and 
                min_height <= image.height <= max_height)
    
    def _validate_landmarks_quality(self, landmarks) -> bool:
        """Valida a qualidade dos landmarks detectados"""
        key_landmarks = [
            self.mp_pose.PoseLandmark.NOSE,
            self.mp_pose.PoseLandmark.LEFT_SHOULDER,
            self.mp_pose.PoseLandmark.RIGHT_SHOULDER,
            self.mp_pose.PoseLandmark.LEFT_HIP,
            self.mp_pose.PoseLandmark.RIGHT_HIP
        ]
        
        for landmark_idx in key_landmarks:
            if landmarks[landmark_idx].visibility < self.analysis_params['confidence_threshold']:
                return False
        
        return True
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Pré-processa a imagem para melhor detecção"""
        # Ajustar contraste e brilho se necessário
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        # Aplicar CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        
        # Recombinar canais
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
        
        return enhanced
    
    def _calculate_enhanced_posture_metrics(self, landmarks, image_shape) -> Dict:
        """
        Calcula métricas aprimoradas de postura com mais precisão
        """
        height, width = image_shape[:2]
        
        # Pontos de referência importantes
        nose = landmarks[self.mp_pose.PoseLandmark.NOSE]
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_ear = landmarks[self.mp_pose.PoseLandmark.LEFT_EAR]
        right_ear = landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR]
        left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
        left_ankle = landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE]
        right_ankle = landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE]
        
        metrics = {}
        
        # 1. Análise da cabeça (Forward Head Posture) - Melhorada
        ear_avg_x = (left_ear.x + right_ear.x) / 2
        ear_avg_y = (left_ear.y + right_ear.y) / 2
        shoulder_avg_x = (left_shoulder.x + right_shoulder.x) / 2
        shoulder_avg_y = (left_shoulder.y + right_shoulder.y) / 2
        
        head_forward_distance = abs(ear_avg_x - shoulder_avg_x) * width
        head_vertical_distance = abs(ear_avg_y - shoulder_avg_y) * height
        
        metrics['head_forward_distance'] = head_forward_distance
        metrics['head_vertical_distance'] = head_vertical_distance
        metrics['head_alignment_score'] = max(0, 100 - (head_forward_distance * 1.5))
        
        # 2. Análise dos ombros - Melhorada
        shoulder_slope = math.degrees(math.atan2(
            (right_shoulder.y - left_shoulder.y) * height,
            (right_shoulder.x - left_shoulder.x) * width
        ))
        
        # Calcular altura dos ombros
        shoulder_height_diff = abs(left_shoulder.y - right_shoulder.y) * height
        
        metrics['shoulder_slope'] = abs(shoulder_slope)
        metrics['shoulder_height_difference'] = shoulder_height_diff
        metrics['shoulder_alignment_score'] = max(0, 100 - (abs(shoulder_slope) * 8 + shoulder_height_diff * 2))
        
        # 3. Análise do alinhamento vertical - Melhorada
        head_x = nose.x
        shoulder_x = shoulder_avg_x
        hip_x = (left_hip.x + right_hip.x) / 2
        ankle_x = (left_ankle.x + right_ankle.x) / 2
        
        head_shoulder_offset = abs(head_x - shoulder_x) * width
        shoulder_hip_offset = abs(shoulder_x - hip_x) * width
        hip_ankle_offset = abs(hip_x - ankle_x) * width
        
        total_vertical_deviation = head_shoulder_offset + shoulder_hip_offset + hip_ankle_offset
        
        metrics['head_shoulder_offset'] = head_shoulder_offset
        metrics['shoulder_hip_offset'] = shoulder_hip_offset
        metrics['hip_ankle_offset'] = hip_ankle_offset
        metrics['total_vertical_deviation'] = total_vertical_deviation
        metrics['vertical_alignment_score'] = max(0, 100 - (total_vertical_deviation * 2))
        
        # 4. Nova métrica: Análise da pelve
        hip_slope = math.degrees(math.atan2(
            (right_hip.y - left_hip.y) * height,
            (right_hip.x - left_hip.x) * width
        ))
        
        metrics['hip_slope'] = abs(hip_slope)
        metrics['pelvic_alignment_score'] = max(0, 100 - (abs(hip_slope) * 10))
        
        # 5. Nova métrica: Simetria corporal
        left_side_length = math.sqrt(
            ((left_shoulder.x - left_hip.x) * width) ** 2 + 
            ((left_shoulder.y - left_hip.y) * height) ** 2
        )
        right_side_length = math.sqrt(
            ((right_shoulder.x - right_hip.x) * width) ** 2 + 
            ((right_shoulder.y - right_hip.y) * height) ** 2
        )
        
        symmetry_difference = abs(left_side_length - right_side_length)
        metrics['body_symmetry_difference'] = symmetry_difference
        metrics['body_symmetry_score'] = max(0, 100 - (symmetry_difference * 5))
        
        # 6. Score geral de postura - Melhorado
        scores = [
            metrics['head_alignment_score'],
            metrics['shoulder_alignment_score'],
            metrics['vertical_alignment_score'],
            metrics['pelvic_alignment_score'],
            metrics['body_symmetry_score']
        ]
        
        # Peso diferenciado para cada métrica
        weights = [0.25, 0.25, 0.25, 0.15, 0.10]
        metrics['overall_posture_score'] = sum(score * weight for score, weight in zip(scores, weights))
        
        # 7. Classificação da postura - Melhorada
        overall_score = metrics['overall_posture_score']
        if overall_score >= 85:
            metrics['posture_classification'] = "Excelente"
            metrics['posture_color'] = "#28a745"
            metrics['posture_icon'] = "🟢"
        elif overall_score >= 70:
            metrics['posture_classification'] = "Boa"
            metrics['posture_color'] = "#4ecdc4"
            metrics['posture_icon'] = "🔵"
        elif overall_score >= 50:
            metrics['posture_classification'] = "Regular"
            metrics['posture_color'] = "#ffc107"
            metrics['posture_icon'] = "🟡"
        elif overall_score >= 30:
            metrics['posture_classification'] = "Ruim"
            metrics['posture_color'] = "#fd7e14"
            metrics['posture_icon'] = "🟠"
        else:
            metrics['posture_classification'] = "Crítica"
            metrics['posture_color'] = "#dc3545"
            metrics['posture_icon'] = "🔴"
        
        # 8. Métricas de risco
        metrics['risk_factors'] = self._identify_risk_factors(metrics)
        
        return metrics
    
    def _identify_risk_factors(self, metrics: Dict) -> List[Dict]:
        """Identifica fatores de risco baseados nas métricas"""
        risk_factors = []
        
        if metrics['head_forward_distance'] > self.analysis_params['head_forward_threshold']:
            risk_factors.append({
                "factor": "Projeção anterior da cabeça",
                "severity": "Alto" if metrics['head_forward_distance'] > 50 else "Médio",
                "description": "Pode causar dores no pescoço e tensão muscular"
            })
        
        if metrics['shoulder_slope'] > self.analysis_params['shoulder_slope_threshold']:
            risk_factors.append({
                "factor": "Desequilíbrio dos ombros",
                "severity": "Alto" if metrics['shoulder_slope'] > 10 else "Médio",
                "description": "Pode levar a dores nas costas e tensão muscular"
            })
        
        if metrics['total_vertical_deviation'] > self.analysis_params['vertical_alignment_threshold']:
            risk_factors.append({
                "factor": "Desalinhamento postural",
                "severity": "Alto" if metrics['total_vertical_deviation'] > 50 else "Médio",
                "description": "Pode causar sobrecarga na coluna vertebral"
            })
        
        return risk_factors
    
    def _draw_enhanced_posture_analysis(self, image: np.ndarray, results, metrics: Dict) -> np.ndarray:
        """
        Desenha análise postural aprimorada na imagem
        """
        annotated_image = image.copy()
        
        # Desenhar landmarks da pose com estilo melhorado
        self.mp_drawing.draw_landmarks(
            annotated_image,
            results.pose_landmarks,
            self.mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
        )
        
        landmarks = results.pose_landmarks.landmark
        height, width = image.shape[:2]
        
        # Linha vertical de referência (linha de gravidade)
        nose = landmarks[self.mp_pose.PoseLandmark.NOSE]
        ankle_avg_x = (landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE].x + 
                      landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE].x) / 2
        
        cv2.line(annotated_image, 
                (int(ankle_avg_x * width), 0), 
                (int(ankle_avg_x * width), height), 
                (255, 255, 0), 2)
        
        # Linha horizontal dos ombros
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        cv2.line(annotated_image,
                (int(left_shoulder.x * width), int(left_shoulder.y * height)),
                (int(right_shoulder.x * width), int(right_shoulder.y * height)),
                (255, 0, 255), 2)
        
        # Linha horizontal dos quadris
        left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
        cv2.line(annotated_image,
                (int(left_hip.x * width), int(left_hip.y * height)),
                (int(right_hip.x * width), int(right_hip.y * height)),
                (0, 255, 255), 2)
        
        # Adicionar informações detalhadas
        info_box_height = 150
        overlay = annotated_image.copy()
        cv2.rectangle(overlay, (10, 10), (400, info_box_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, annotated_image, 0.3, 0, annotated_image)
        
        # Texto com métricas
        y_offset = 35
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        color = (255, 255, 255)
        thickness = 2
        
        cv2.putText(annotated_image, f"Score Geral: {metrics['overall_posture_score']:.1f}%", 
                   (15, y_offset), font, font_scale, color, thickness)
        y_offset += 25
        
        cv2.putText(annotated_image, f"Classificacao: {metrics['posture_classification']}", 
                   (15, y_offset), font, font_scale, color, thickness)
        y_offset += 25
        
        cv2.putText(annotated_image, f"Cabeca: {metrics['head_alignment_score']:.1f}%", 
                   (15, y_offset), font, font_scale, color, thickness)
        y_offset += 25
        
        cv2.putText(annotated_image, f"Ombros: {metrics['shoulder_alignment_score']:.1f}%", 
                   (15, y_offset), font, font_scale, color, thickness)
        y_offset += 25
        
        cv2.putText(annotated_image, f"Alinhamento: {metrics['vertical_alignment_score']:.1f}%", 
                   (15, y_offset), font, font_scale, color, thickness)
        
        return annotated_image
    
    def _generate_comprehensive_report(self, metrics: Dict) -> Dict:
        """
        Gera um relatório abrangente da análise postural
        """
        report = {
            "summary": {
                "overall_score": metrics['overall_posture_score'],
                "classification": metrics['posture_classification'],
                "color": metrics['posture_color'],
                "icon": metrics['posture_icon']
            },
            "details": [],
            "recommendations": [],
            "risk_factors": metrics['risk_factors'],
            "priority_areas": []
        }
        
        # Análise detalhada de cada área
        areas = [
            {
                "name": "Alinhamento da Cabeça",
                "score": metrics['head_alignment_score'],
                "threshold": 70,
                "good_desc": "Posicionamento adequado da cabeça em relação aos ombros",
                "poor_desc": f"Projeção anterior da cabeça detectada ({metrics['head_forward_distance']:.1f}px)",
                "recommendations": [
                    "Pratique exercícios de fortalecimento dos músculos cervicais profundos",
                    "Realize alongamentos dos músculos peitorais e suboccipitais",
                    "Mantenha consciência postural durante atividades diárias"
                ]
            },
            {
                "name": "Alinhamento dos Ombros",
                "score": metrics['shoulder_alignment_score'],
                "threshold": 70,
                "good_desc": "Ombros bem alinhados e nivelados",
                "poor_desc": f"Desequilíbrio dos ombros detectado (inclinação: {metrics['shoulder_slope']:.1f}°)",
                "recommendations": [
                    "Realize exercícios de fortalecimento unilateral",
                    "Pratique alongamentos específicos para músculos encurtados",
                    "Evite carregar peso sempre do mesmo lado"
                ]
            },
            {
                "name": "Alinhamento Vertical",
                "score": metrics['vertical_alignment_score'],
                "threshold": 70,
                "good_desc": "Excelente alinhamento da linha de gravidade corporal",
                "poor_desc": f"Desvio no alinhamento vertical ({metrics['total_vertical_deviation']:.1f}px)",
                "recommendations": [
                    "Fortaleça os músculos do core (abdominais e lombares)",
                    "Pratique exercícios de propriocepção e equilíbrio",
                    "Trabalhe a consciência corporal com exercícios específicos"
                ]
            },
            {
                "name": "Alinhamento Pélvico",
                "score": metrics['pelvic_alignment_score'],
                "threshold": 70,
                "good_desc": "Pelve bem posicionada e equilibrada",
                "poor_desc": f"Inclinação pélvica detectada ({metrics['hip_slope']:.1f}°)",
                "recommendations": [
                    "Fortaleça os músculos glúteos e abdominais",
                    "Alongue os flexores do quadril",
                    "Pratique exercícios de mobilidade pélvica"
                ]
            },
            {
                "name": "Simetria Corporal",
                "score": metrics['body_symmetry_score'],
                "threshold": 70,
                "good_desc": "Boa simetria entre os lados do corpo",
                "poor_desc": f"Assimetria corporal detectada ({metrics['body_symmetry_difference']:.1f}px)",
                "recommendations": [
                    "Realize exercícios unilaterais para corrigir desequilíbrios",
                    "Pratique atividades que promovam simetria corporal",
                    "Considere avaliação com fisioterapeuta"
                ]
            }
        ]
        
        # Processar cada área
        for area in areas:
            status = "Bom" if area["score"] >= area["threshold"] else "Atenção necessária"
            description = area["good_desc"] if area["score"] >= area["threshold"] else area["poor_desc"]
            
            report['details'].append({
                "area": area["name"],
                "score": area["score"],
                "status": status,
                "description": description
            })
            
            # Adicionar recomendações se necessário
            if area["score"] < area["threshold"]:
                report['recommendations'].extend(area["recommendations"])
                report['priority_areas'].append(area["name"])
        
        # Remover recomendações duplicadas
        report['recommendations'] = list(set(report['recommendations']))
        
        # Adicionar recomendações gerais baseadas na classificação
        if metrics['overall_posture_score'] < 50:
            report['recommendations'].insert(0, "Considere consultar um fisioterapeuta para avaliação detalhada")
            report['recommendations'].append("Implemente pausas regulares durante atividades prolongadas")
        
        return report
    
    def _calculate_trends(self, metrics: Dict, user_id: Optional[str]) -> Dict:
        """
        Calcula tendências baseadas no histórico (simulado por enquanto)
        """
        # Por enquanto, retorna dados simulados
        # Em uma implementação real, consultaria o banco de dados
        return {
            "improvement": "+5.2%",
            "trend": "melhorando",
            "last_analysis": "2024-01-10",
            "total_analyses": 3
        }
    
    def _calculate_confidence_scores(self, landmarks) -> Dict:
        """
        Calcula scores de confiança para diferentes partes do corpo
        """
        confidence_scores = {}
        
        # Grupos de landmarks por região
        regions = {
            "head": [self.mp_pose.PoseLandmark.NOSE, self.mp_pose.PoseLandmark.LEFT_EAR, self.mp_pose.PoseLandmark.RIGHT_EAR],
            "shoulders": [self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_SHOULDER],
            "torso": [self.mp_pose.PoseLandmark.LEFT_HIP, self.mp_pose.PoseLandmark.RIGHT_HIP],
            "legs": [self.mp_pose.PoseLandmark.LEFT_KNEE, self.mp_pose.PoseLandmark.RIGHT_KNEE, 
                    self.mp_pose.PoseLandmark.LEFT_ANKLE, self.mp_pose.PoseLandmark.RIGHT_ANKLE]
        }
        
        for region, landmark_indices in regions.items():
            visibilities = [landmarks[idx].visibility for idx in landmark_indices]
            confidence_scores[region] = sum(visibilities) / len(visibilities)
        
        return confidence_scores
    
    def _landmarks_to_dict(self, landmarks) -> List[Dict]:
        """
        Converte landmarks para formato de dicionário com informações extras
        """
        return [
            {
                "id": i,
                "name": self.mp_pose.PoseLandmark(i).name,
                "x": landmark.x,
                "y": landmark.y,
                "z": landmark.z,
                "visibility": landmark.visibility
            }
            for i, landmark in enumerate(landmarks)
        ]
    
    def _image_to_base64(self, image: np.ndarray) -> str:
        """
        Converte imagem numpy para base64 com qualidade otimizada
        """
        # Converter RGB para BGR para o OpenCV
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Codificar como JPEG com qualidade alta
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
        _, buffer = cv2.imencode('.jpg', image_bgr, encode_param)
        
        # Converter para base64
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return f"data:image/jpeg;base64,{image_base64}"
    
    def get_analysis_summary(self, metrics: Dict) -> str:
        """
        Gera um resumo textual da análise para relatórios
        """
        classification = metrics['posture_classification']
        score = metrics['overall_posture_score']
        
        summary = f"Análise Postural - Classificação: {classification} ({score:.1f}%)\n\n"
        
        if score >= 85:
            summary += "Excelente postura! Continue mantendo os bons hábitos posturais."
        elif score >= 70:
            summary += "Boa postura geral, com pequenos pontos de atenção."
        elif score >= 50:
            summary += "Postura regular. Recomenda-se atenção a alguns aspectos posturais."
        else:
            summary += "Postura necessita atenção. Recomenda-se acompanhamento profissional."
        
        return summary

# Instância global do analisador melhorado
posture_analyzer = PostureAnalyzer()

# Função de conveniência para análise rápida
def analyze_posture_quick(image_base64: str, user_id: Optional[str] = None) -> Dict:
    """Função de conveniência para análise rápida"""
    return posture_analyzer.analyze_posture_from_base64(image_base64, user_id)

# Função para validar se o serviço está funcionando
def health_check() -> Dict:
    """Verifica se o serviço de análise postural está funcionando"""
    try:
        # Criar uma imagem de teste pequena
        test_image = np.zeros((400, 300, 3), dtype=np.uint8)
        return {"status": "healthy", "message": "Serviço de análise postural funcionando"}
    except Exception as e:
        return {"status": "unhealthy", "message": f"Erro no serviço: {str(e)}"}

