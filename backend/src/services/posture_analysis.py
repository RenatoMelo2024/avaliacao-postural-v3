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

class PostureAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=False,
            min_detection_confidence=0.5
        )
        
    def analyze_posture_from_base64(self, image_base64: str) -> Dict:
        """
        Analisa a postura a partir de uma imagem em base64
        """
        try:
            # Decodificar imagem base64
            image_data = base64.b64decode(image_base64.split(',')[1] if ',' in image_base64 else image_base64)
            image = Image.open(BytesIO(image_data))
            image_rgb = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            return self.analyze_posture(image_rgb)
        except Exception as e:
            return {"error": f"Erro ao processar imagem: {str(e)}"}
    
    def analyze_posture(self, image: np.ndarray) -> Dict:
        """
        Analisa a postura de uma pessoa na imagem
        """
        try:
            # Converter BGR para RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Processar a imagem
            results = self.pose.process(image_rgb)
            
            if not results.pose_landmarks:
                return {"error": "Nenhuma pessoa detectada na imagem"}
            
            # Extrair pontos de referência
            landmarks = results.pose_landmarks.landmark
            
            # Calcular métricas posturais
            metrics = self._calculate_posture_metrics(landmarks, image.shape)
            
            # Gerar visualização
            annotated_image = self._draw_posture_analysis(image_rgb, results, metrics)
            
            # Converter imagem anotada para base64
            annotated_base64 = self._image_to_base64(annotated_image)
            
            # Gerar relatório
            report = self._generate_posture_report(metrics)
            
            return {
                "success": True,
                "metrics": metrics,
                "report": report,
                "annotated_image": annotated_base64,
                "landmarks": self._landmarks_to_dict(landmarks)
            }
            
        except Exception as e:
            return {"error": f"Erro na análise postural: {str(e)}"}
    
    def _calculate_posture_metrics(self, landmarks, image_shape) -> Dict:
        """
        Calcula métricas específicas de postura
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
        
        metrics = {}
        
        # 1. Alinhamento da cabeça (Forward Head Posture)
        ear_avg_x = (left_ear.x + right_ear.x) / 2
        shoulder_avg_x = (left_shoulder.x + right_shoulder.x) / 2
        head_forward_distance = abs(ear_avg_x - shoulder_avg_x) * width
        metrics['head_forward_distance'] = head_forward_distance
        metrics['head_alignment_score'] = max(0, 100 - (head_forward_distance * 2))
        
        # 2. Inclinação dos ombros
        shoulder_slope = math.degrees(math.atan2(
            (right_shoulder.y - left_shoulder.y) * height,
            (right_shoulder.x - left_shoulder.x) * width
        ))
        metrics['shoulder_slope'] = abs(shoulder_slope)
        metrics['shoulder_alignment_score'] = max(0, 100 - (abs(shoulder_slope) * 10))
        
        # 3. Alinhamento vertical (cabeça-ombro-quadril)
        head_x = nose.x
        shoulder_x = shoulder_avg_x
        hip_x = (left_hip.x + right_hip.x) / 2
        
        head_shoulder_offset = abs(head_x - shoulder_x) * width
        shoulder_hip_offset = abs(shoulder_x - hip_x) * width
        
        metrics['head_shoulder_offset'] = head_shoulder_offset
        metrics['shoulder_hip_offset'] = shoulder_hip_offset
        metrics['vertical_alignment_score'] = max(0, 100 - ((head_shoulder_offset + shoulder_hip_offset) * 3))
        
        # 4. Score geral de postura
        scores = [
            metrics['head_alignment_score'],
            metrics['shoulder_alignment_score'],
            metrics['vertical_alignment_score']
        ]
        metrics['overall_posture_score'] = sum(scores) / len(scores)
        
        # 5. Classificação da postura
        overall_score = metrics['overall_posture_score']
        if overall_score >= 80:
            metrics['posture_classification'] = "Excelente"
            metrics['posture_color'] = "green"
        elif overall_score >= 60:
            metrics['posture_classification'] = "Boa"
            metrics['posture_color'] = "yellow"
        elif overall_score >= 40:
            metrics['posture_classification'] = "Regular"
            metrics['posture_color'] = "orange"
        else:
            metrics['posture_classification'] = "Ruim"
            metrics['posture_color'] = "red"
        
        return metrics
    
    def _draw_posture_analysis(self, image: np.ndarray, results, metrics: Dict) -> np.ndarray:
        """
        Desenha a análise postural na imagem
        """
        annotated_image = image.copy()
        
        # Desenhar landmarks da pose
        self.mp_drawing.draw_landmarks(
            annotated_image,
            results.pose_landmarks,
            self.mp_pose.POSE_CONNECTIONS,
            self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
        )
        
        # Adicionar linhas de referência para alinhamento
        landmarks = results.pose_landmarks.landmark
        height, width = image.shape[:2]
        
        # Linha vertical de referência
        nose = landmarks[self.mp_pose.PoseLandmark.NOSE]
        cv2.line(annotated_image, 
                (int(nose.x * width), 0), 
                (int(nose.x * width), height), 
                (255, 255, 0), 2)
        
        # Linha horizontal dos ombros
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        cv2.line(annotated_image,
                (int(left_shoulder.x * width), int(left_shoulder.y * height)),
                (int(right_shoulder.x * width), int(right_shoulder.y * height)),
                (255, 0, 255), 2)
        
        # Adicionar texto com métricas
        y_offset = 30
        cv2.putText(annotated_image, f"Score Geral: {metrics['overall_posture_score']:.1f}%", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y_offset += 30
        cv2.putText(annotated_image, f"Classificacao: {metrics['posture_classification']}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return annotated_image
    
    def _generate_posture_report(self, metrics: Dict) -> Dict:
        """
        Gera um relatório detalhado da análise postural
        """
        report = {
            "summary": {
                "overall_score": metrics['overall_posture_score'],
                "classification": metrics['posture_classification'],
                "color": metrics['posture_color']
            },
            "details": [],
            "recommendations": []
        }
        
        # Análise da cabeça
        if metrics['head_alignment_score'] < 70:
            report['details'].append({
                "area": "Alinhamento da Cabeça",
                "score": metrics['head_alignment_score'],
                "status": "Atenção necessária",
                "description": f"Projeção anterior da cabeça detectada ({metrics['head_forward_distance']:.1f}px)"
            })
            report['recommendations'].append(
                "Pratique exercícios de fortalecimento dos músculos do pescoço e alongamento dos músculos peitorais"
            )
        else:
            report['details'].append({
                "area": "Alinhamento da Cabeça",
                "score": metrics['head_alignment_score'],
                "status": "Bom",
                "description": "Posicionamento adequado da cabeça"
            })
        
        # Análise dos ombros
        if metrics['shoulder_alignment_score'] < 70:
            report['details'].append({
                "area": "Alinhamento dos Ombros",
                "score": metrics['shoulder_alignment_score'],
                "status": "Atenção necessária",
                "description": f"Inclinação dos ombros detectada ({metrics['shoulder_slope']:.1f}°)"
            })
            report['recommendations'].append(
                "Realize exercícios de fortalecimento unilateral e alongamento para corrigir desequilíbrios"
            )
        else:
            report['details'].append({
                "area": "Alinhamento dos Ombros",
                "score": metrics['shoulder_alignment_score'],
                "status": "Bom",
                "description": "Ombros bem alinhados"
            })
        
        # Análise do alinhamento vertical
        if metrics['vertical_alignment_score'] < 70:
            report['details'].append({
                "area": "Alinhamento Vertical",
                "score": metrics['vertical_alignment_score'],
                "status": "Atenção necessária",
                "description": "Desvio no alinhamento vertical detectado"
            })
            report['recommendations'].append(
                "Trabalhe o fortalecimento do core e pratique exercícios de consciência corporal"
            )
        else:
            report['details'].append({
                "area": "Alinhamento Vertical",
                "score": metrics['vertical_alignment_score'],
                "status": "Bom",
                "description": "Bom alinhamento vertical"
            })
        
        return report
    
    def _landmarks_to_dict(self, landmarks) -> List[Dict]:
        """
        Converte landmarks para formato de dicionário
        """
        return [
            {
                "x": landmark.x,
                "y": landmark.y,
                "z": landmark.z,
                "visibility": landmark.visibility
            }
            for landmark in landmarks
        ]
    
    def _image_to_base64(self, image: np.ndarray) -> str:
        """
        Converte imagem numpy para base64
        """
        # Converter RGB para BGR para o OpenCV
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Codificar como JPEG
        _, buffer = cv2.imencode('.jpg', image_bgr)
        
        # Converter para base64
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return f"data:image/jpeg;base64,{image_base64}"

# Instância global do analisador
posture_analyzer = PostureAnalyzer()

