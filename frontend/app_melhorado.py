import streamlit as st
import requests
import json
import base64
from PIL import Image
import io
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import time
from pathlib import Path

# Carregar e converter a logo para base64
def get_base64_image(relative_path):
    # Obter o diretório do script atual
    script_dir = Path(__file__).parent
    # Construir o caminho absoluto para a imagem
    absolute_path = script_dir / relative_path
    with open(absolute_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

logo_base64 = get_base64_image("assets/logo_otimizada.png")

# Configuração da página
st.set_page_config(
    page_title="Postura+ - Avaliação Postural Digital",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para melhorar a aparência
st.markdown("""
<style>
    /* Estilo geral */
    .main {
        padding-top: 2rem;
    }
    
    /* Header personalizado */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* Cards personalizados */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .exercise-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        transition: transform 0.3s ease;
    }
    
    .exercise-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    
    /* Botões personalizados */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar personalizada */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Formulários */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e1e5e9;
        padding: 0.75rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    
    /* Alertas personalizados */
    .alert-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .alert-error {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Animações */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Progress bar personalizada */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# URL da API (ajustar conforme necessário)
API_BASE_URL = "http://localhost:5000/api"

# Classe para gerenciar a API
class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
        
    def set_token(self, token):
        self.token = token
        
    def get_headers(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def login(self, email, senha):
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "senha": senha}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                return data
            else:
                return {"error": response.json().get("message", "Erro no login")}
        except Exception as e:
            return {"error": f"Erro de conexão: {str(e)}"}
    
    def register(self, user_data):
        try:
            response = requests.post(
                f"{self.base_url}/auth/register",
                json=user_data
            )
            if response.status_code == 201:
                return response.json()
            else:
                return {"error": response.json().get("message", "Erro no registro")}
        except Exception as e:
            return {"error": f"Erro de conexão: {str(e)}"}
    
    def analyze_posture(self, image_base64):
        try:
            response = requests.post(
                f"{self.base_url}/posture/analyze",
                json={"image": image_base64},
                headers=self.get_headers()
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.json().get("message", "Erro na análise")}
        except Exception as e:
            return {"error": f"Erro de conexão: {str(e)}"}
    
    def get_students(self):
        try:
            response = requests.get(
                f"{self.base_url}/estudantes",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": response.json().get("message", "Erro ao buscar estudantes")}
        except Exception as e:
            return {"error": f"Erro de conexão: {str(e)}"}
    
    def create_student(self, student_data):
        try:
            response = requests.post(
                f"{self.base_url}/estudantes",
                json=student_data,
                headers=self.get_headers()
            )
            if response.status_code == 201:
                return response.json()
            else:
                return {"error": response.json().get("message", "Erro ao criar estudante")}
        except Exception as e:
            return {"error": f"Erro de conexão: {str(e)}"}

# Inicializar cliente da API
api_client = APIClient(API_BASE_URL)

# Funções auxiliares
def show_header():
    """Exibe o cabeçalho personalizado"""
    st.markdown(f"""
    <div class="header-container fade-in">
        <img src="data:image/png;base64,{logo_base64}" alt="Postura+ Logo" style="width: 100px; margin-bottom: 1rem;">
        <div class="header-title">Postura+</div>
        <div class="header-subtitle">Sistema Inteligente de Avaliação Postural Digital</div>
    </div>
    """, unsafe_allow_html=True)


def image_to_base64(image):
    """Converte imagem PIL para base64"""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"

def show_success_message(message):
    """Exibe mensagem de sucesso personalizada"""
    st.markdown(f"""
    <div class="alert-success fade-in">
        ✅ {message}
    </div>
    """, unsafe_allow_html=True)

def show_error_message(message):
    """Exibe mensagem de erro personalizada"""
    st.markdown(f"""
    <div class="alert-error fade-in">
        ❌ {message}
    </div>
    """, unsafe_allow_html=True)

def display_posture_results(results):
    """Exibe os resultados da análise postural com design melhorado"""
    if "error" in results:
        show_error_message(results["error"])
        return
    
    if not results.get("success"):
        show_error_message("Falha na análise postural")
        return
    
    metrics = results.get("metrics", {})
    report = results.get("report", {})
    
    # Exibir métricas principais com cards personalizados
    st.markdown("### 📊 Métricas da Análise")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score = metrics.get("overall_posture_score", 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">Score Geral</h3>
            <h2 style="margin: 0.5rem 0;">{score:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        classification = metrics.get("posture_classification", "N/A")
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">Classificação</h3>
            <h2 style="margin: 0.5rem 0;">{classification}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        head_score = metrics.get("head_alignment_score", 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">Cabeça</h3>
            <h2 style="margin: 0.5rem 0;">{head_score:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        shoulder_score = metrics.get("shoulder_alignment_score", 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">Ombros</h3>
            <h2 style="margin: 0.5rem 0;">{shoulder_score:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Exibir imagem anotada
    if "annotated_image" in results:
        st.markdown("### 🔍 Análise Visual")
        st.image(results["annotated_image"], caption="Análise Postural Detalhada", use_column_width=True)
    
    # Exibir relatório detalhado
    if report:
        st.markdown("### 📋 Relatório Detalhado")
        
        # Detalhes da análise
        if "details" in report:
            for detail in report["details"]:
                with st.expander(f"🎯 {detail['area']} - {detail['status']}"):
                    st.write(f"**Score:** {detail['score']:.1f}%")
                    st.write(f"**Descrição:** {detail['description']}")
        
        # Recomendações
        if "recommendations" in report:
            st.markdown("### 💡 Recomendações")
            for i, rec in enumerate(report["recommendations"], 1):
                st.markdown(f"**{i}.** {rec}")

# Páginas da aplicação
def login_page():
    """Página de login com design melhorado"""
    show_header()
    
    # Container centralizado
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Registro"])
        
        with tab1:
            st.markdown("### Acesse sua conta")
            
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("📧 Email", placeholder="Digite seu email")
                senha = st.text_input("🔒 Senha", type="password", placeholder="Digite sua senha")
                
                col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                with col_btn2:
                    submit = st.form_submit_button("🚀 Entrar", use_container_width=True)
                
                if submit:
                    if email and senha:
                        with st.spinner("🔄 Fazendo login..."):
                            result = api_client.login(email, senha)
                            
                        if "error" in result:
                            show_error_message(result["error"])
                        else:
                            st.session_state.user = result.get("usuario")
                            st.session_state.logged_in = True
                            show_success_message("Login realizado com sucesso!")
                            time.sleep(1)
                            st.rerun()
                    else:
                        show_error_message("Por favor, preencha todos os campos")
        
        with tab2:
            st.markdown("### Criar nova conta")
            
            with st.form("register_form", clear_on_submit=False):
                nome = st.text_input("👤 Nome completo", placeholder="Digite seu nome completo")
                email_reg = st.text_input("📧 Email", key="email_reg", placeholder="Digite seu email")
                senha_reg = st.text_input("🔒 Senha", type="password", key="senha_reg", placeholder="Crie uma senha segura")
                tipo_usuario = st.selectbox(
                    "👥 Tipo de usuário",
                    ["estudante", "profissional_saude", "gestor_educacional"],
                    format_func=lambda x: {
                        "estudante": "🎓 Estudante",
                        "profissional_saude": "👨‍⚕️ Profissional de Saúde",
                        "gestor_educacional": "🏫 Gestor Educacional"
                    }[x]
                )
                
                col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                with col_btn2:
                    submit_reg = st.form_submit_button("✨ Criar conta", use_container_width=True)
                
                if submit_reg:
                    if nome and email_reg and senha_reg:
                        user_data = {
                            "nome": nome,
                            "email": email_reg,
                            "senha": senha_reg,
                            "tipo_usuario": tipo_usuario
                        }
                        
                        with st.spinner("🔄 Criando conta..."):
                            result = api_client.register(user_data)
                        
                        if "error" in result:
                            show_error_message(result["error"])
                        else:
                            show_success_message("Conta criada com sucesso! Faça login para continuar.")
                    else:
                        show_error_message("Por favor, preencha todos os campos")

def dashboard_page():
    """Página principal do dashboard com design melhorado"""
    st.markdown("# 📊 Dashboard")
    st.markdown("Visão geral do sistema de avaliação postural")
    
    # Estatísticas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">👥 Estudantes</h3>
            <h2 style="margin: 0.5rem 0;">45</h2>
            <p style="color: #28a745; margin: 0;">+12% este mês</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">📋 Avaliações</h3>
            <h2 style="margin: 0.5rem 0;">128</h2>
            <p style="color: #28a745; margin: 0;">+8% este mês</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">🧘 Exercícios</h3>
            <h2 style="margin: 0.5rem 0;">89</h2>
            <p style="color: #28a745; margin: 0;">+23% este mês</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">📅 Próximas</h3>
            <h2 style="margin: 0.5rem 0;">12</h2>
            <p style="color: #ffc107; margin: 0;">Avaliações agendadas</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gráficos aprimorados
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Evolução das Avaliações")
        dates = pd.date_range("2024-01-01", periods=12, freq="M")
        values = [10, 15, 12, 18, 22, 25, 20, 28, 32, 30, 35, 40]
        df = pd.DataFrame({"Data": dates, "Avaliações": values})
        
        fig = px.line(df, x="Data", y="Avaliações", 
                     title="Crescimento Mensal de Avaliações",
                     color_discrete_sequence=["#667eea"])
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Classificação Postural")
        labels = ["Excelente", "Boa", "Regular", "Ruim"]
        values = [25, 35, 30, 10]
        colors = ["#28a745", "#17a2b8", "#ffc107", "#dc3545"]
        
        fig = px.pie(values=values, names=labels, 
                    title="Distribuição das Classificações",
                    color_discrete_sequence=colors)
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Atividades recentes com design melhorado
    st.markdown("### 🕐 Atividades Recentes")
    activities = [
        {"atividade": "Avaliação postural realizada para João Silva", "tempo": "2 horas atrás", "icon": "📋"},
        {"atividade": "Sessão de exercícios completada por Maria Santos", "tempo": "4 horas atrás", "icon": "🧘"},
        {"atividade": "Relatório mensal gerado para Escola ABC", "tempo": "1 dia atrás", "icon": "📊"},
    ]
    
    for activity in activities:
        st.markdown(f"""
        <div class="metric-card">
            <p style="margin: 0;"><strong>{activity['icon']} {activity['atividade']}</strong></p>
            <p style="color: #6c757d; margin: 0.5rem 0 0 0;"><em>{activity['tempo']}</em></p>
        </div>
        """, unsafe_allow_html=True)

def posture_analysis_page():
    """Página de análise postural com design melhorado"""
    st.markdown("# 📷 Análise Postural Inteligente")
    st.markdown("Faça upload de uma imagem para análise postural automática.")
    
    # Instruções melhoradas
    with st.expander("📋 Como usar a análise postural", expanded=False):
        st.markdown("""
        **Instruções para melhor resultado:**
        1. 📸 Use uma foto de corpo inteiro
        2. 🧍 Mantenha-se em pé, de frente para a câmera
        3. 💡 Certifique-se de ter boa iluminação
        4. 👕 Use roupas que permitam ver a silhueta do corpo
        5. 📐 Mantenha a câmera na altura do peito
        """)
    
    uploaded_file = st.file_uploader(
        "📁 Escolha uma imagem",
        type=["jpg", "jpeg", "png"],
        help="Formatos suportados: JPG, JPEG, PNG (máx. 10MB)"
    )
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### 🖼️ Imagem Original")
            st.image(image, caption="Imagem carregada", use_column_width=True)
            
            st.markdown("### ⚙️ Controles")
            if st.button("🔍 Analisar Postura", type="primary", use_container_width=True):
                with st.spinner("🧠 Analisando postura com IA..."):
                    # Simular tempo de processamento
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    # Converter imagem para base64
                    image_base64 = image_to_base64(image)
                    
                    # Enviar para análise
                    results = api_client.analyze_posture(image_base64)
                    
                    # Armazenar resultados na sessão
                    st.session_state.analysis_results = results
                    st.rerun()
        
        with col2:
            if hasattr(st.session_state, 'analysis_results'):
                st.markdown("### 📊 Resultados da Análise")
                display_posture_results(st.session_state.analysis_results)

def vr_exercises_page():
    """Página de exercícios com design melhorado"""
    st.markdown("# 🧘 Exercícios Posturais Interativos")
    st.markdown("Versão adaptada dos exercícios de realidade virtual em formato 2D interativo.")
    
    # Lista de exercícios aprimorada
    exercises = [
        {
            "id": 1,
            "title": "Alongamento Cervical",
            "description": "Exercícios para relaxar e fortalecer os músculos do pescoço",
            "duration": "5 minutos",
            "difficulty": "Iniciante",
            "category": "Pescoço",
            "icon": "🦴",
            "color": "#28a745",
            "instructions": [
                "Sente-se com a coluna ereta",
                "Incline a cabeça lentamente para a direita",
                "Mantenha por 15 segundos",
                "Repita para o lado esquerdo",
                "Faça movimentos circulares suaves"
            ]
        },
        {
            "id": 2,
            "title": "Fortalecimento do Core",
            "description": "Exercícios para fortalecer os músculos abdominais e das costas",
            "duration": "10 minutos",
            "difficulty": "Intermediário",
            "category": "Core",
            "icon": "💪",
            "color": "#17a2b8",
            "instructions": [
                "Deite-se de costas",
                "Flexione os joelhos",
                "Contraia o abdômen",
                "Levante o tronco lentamente",
                "Mantenha a posição por 5 segundos"
            ]
        },
        {
            "id": 3,
            "title": "Postura Consciente",
            "description": "Exercícios de consciência corporal e correção postural",
            "duration": "8 minutos",
            "difficulty": "Iniciante",
            "category": "Educação",
            "icon": "🎓",
            "color": "#ffc107",
            "instructions": [
                "Fique em pé diante de um espelho",
                "Observe sua postura atual",
                "Alinhe a cabeça sobre os ombros",
                "Mantenha os ombros relaxados",
                "Respire profundamente mantendo a posição"
            ]
        },
        {
            "id": 4,
            "title": "Relaxamento Guiado",
            "description": "Sessão de relaxamento com técnicas de respiração",
            "duration": "12 minutos",
            "difficulty": "Iniciante",
            "category": "Relaxamento",
            "icon": "🧘",
            "color": "#6f42c1",
            "instructions": [
                "Encontre uma posição confortável",
                "Feche os olhos",
                "Respire profundamente",
                "Relaxe cada grupo muscular",
                "Mantenha o foco na respiração"
            ]
        }
    ]
    
    # Grid de exercícios com cards melhorados
    cols = st.columns(2)
    
    for i, exercise in enumerate(exercises):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="exercise-card">
                <h3 style="color: {exercise['color']}; margin-top: 0;">
                    {exercise['icon']} {exercise['title']}
                </h3>
                <p><strong>⏱️ Duração:</strong> {exercise['duration']}</p>
                <p><strong>📊 Dificuldade:</strong> {exercise['difficulty']}</p>
                <p><strong>🏷️ Categoria:</strong> {exercise['category']}</p>
                <p style="margin-bottom: 1rem;">{exercise['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🚀 Iniciar {exercise['title']}", key=f"btn_{exercise['id']}", use_container_width=True):
                st.session_state.current_exercise = exercise
                st.session_state.exercise_started = True
                st.rerun()
    
    # Sessão de exercício ativa com design melhorado
    if hasattr(st.session_state, 'exercise_started') and st.session_state.exercise_started:
        exercise = st.session_state.current_exercise
        
        st.markdown("---")
        st.markdown(f"## 🏃 Sessão Ativa: {exercise['title']}")
        
        # Barra de progresso melhorada
        if 'exercise_progress' not in st.session_state:
            st.session_state.exercise_progress = 0
        
        progress_percentage = st.session_state.exercise_progress
        st.markdown(f"**Progresso: {progress_percentage}%**")
        progress_bar = st.progress(progress_percentage / 100)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📋 Instruções Passo a Passo")
            for i, instruction in enumerate(exercise['instructions'], 1):
                if i <= (progress_percentage // 20) + 1:
                    st.markdown(f"✅ **{i}.** {instruction}")
                else:
                    st.markdown(f"⏳ **{i}.** {instruction}")
        
        with col2:
            st.markdown("### 🎮 Controles")
            
            if progress_percentage < 100:
                if st.button("▶️ Próximo Passo", use_container_width=True):
                    st.session_state.exercise_progress = min(100, progress_percentage + 20)
                    st.rerun()
            
            if st.button("⏹️ Finalizar Sessão", use_container_width=True):
                st.session_state.exercise_started = False
                st.session_state.exercise_progress = 0
                show_success_message("Sessão finalizada com sucesso!")
                st.rerun()
        
        if progress_percentage >= 100:
            st.markdown("### 🎉 Parabéns!")
            st.markdown("Você concluiu o exercício com sucesso!")
            st.balloons()

def students_page():
    """Página de gerenciamento de estudantes com design melhorado"""
    st.markdown("# 👥 Gerenciamento de Estudantes")
    st.markdown("Gerencie os estudantes cadastrados no sistema")
    
    tab1, tab2 = st.tabs(["📋 Lista de Estudantes", "➕ Adicionar Estudante"])
    
    with tab1:
        st.markdown("### 📊 Estudantes Cadastrados")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            search_name = st.text_input("🔍 Buscar por nome", placeholder="Digite o nome...")
        with col2:
            filter_school = st.selectbox("🏫 Filtrar por escola", ["Todas", "Escola ABC", "Escola XYZ", "Colégio Central"])
        with col3:
            filter_age = st.selectbox("👶 Filtrar por idade", ["Todas", "12-14 anos", "15-17 anos", "18+ anos"])
        
        # Dados mockados
        students_data = [
            {"ID": 1, "Nome": "João Silva", "Idade": 15, "Escola": "Escola ABC", "Última Avaliação": "2024-01-15", "Status": "Ativo"},
            {"ID": 2, "Nome": "Maria Santos", "Idade": 16, "Escola": "Escola XYZ", "Última Avaliação": "2024-01-10", "Status": "Ativo"},
            {"ID": 3, "Nome": "Pedro Oliveira", "Idade": 14, "Escola": "Escola ABC", "Última Avaliação": "2024-01-12", "Status": "Ativo"},
        ]
        
        df = pd.DataFrame(students_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    with tab2:
        st.markdown("### ➕ Adicionar Novo Estudante")
        
        with st.form("student_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("👤 Nome completo", placeholder="Digite o nome completo")
                idade = st.number_input("🎂 Idade", min_value=5, max_value=25, value=15)
                genero = st.selectbox("⚧️ Gênero", ["Masculino", "Feminino", "Outro"])
            
            with col2:
                escola = st.text_input("🏫 Escola", placeholder="Nome da escola")
                turma = st.text_input("📚 Turma", placeholder="Ex: 9º Ano A")
                responsavel = st.text_input("👨‍👩‍👧‍👦 Responsável", placeholder="Nome do responsável")
            
            observacoes = st.text_area("📝 Observações", placeholder="Observações adicionais (opcional)")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                submit = st.form_submit_button("✨ Adicionar Estudante", use_container_width=True)
            
            if submit:
                if nome and escola:
                    show_success_message(f"Estudante {nome} adicionado com sucesso!")
                else:
                    show_error_message("Por favor, preencha todos os campos obrigatórios")

def schools_page():
    """Página de gerenciamento de escolas com design melhorado"""
    st.markdown("# 🏫 Gerenciamento de Escolas")
    st.markdown("Gerencie as escolas parceiras do sistema")
    
    tab1, tab2 = st.tabs(["📋 Lista de Escolas", "➕ Adicionar Escola"])
    
    with tab1:
        st.markdown("### 📊 Escolas Cadastradas")
        
        # Dados mockados com mais informações
        schools_data = [
            {"ID": 1, "Nome": "Escola ABC", "Endereço": "Rua A, 123", "Estudantes": 150, "Status": "Ativa", "Contato": "(11) 9999-9999"},
            {"ID": 2, "Nome": "Escola XYZ", "Endereço": "Rua B, 456", "Estudantes": 200, "Status": "Ativa", "Contato": "(11) 8888-8888"},
            {"ID": 3, "Nome": "Colégio Central", "Endereço": "Av. C, 789", "Estudantes": 300, "Status": "Ativa", "Contato": "(11) 7777-7777"},
        ]
        
        df = pd.DataFrame(schools_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    with tab2:
        st.markdown("### ➕ Adicionar Nova Escola")
        
        with st.form("school_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("🏫 Nome da escola", placeholder="Digite o nome da escola")
                endereco = st.text_area("📍 Endereço", placeholder="Endereço completo")
                telefone = st.text_input("📞 Telefone", placeholder="(11) 9999-9999")
            
            with col2:
                email = st.text_input("📧 Email", placeholder="contato@escola.com")
                diretor = st.text_input("👨‍💼 Diretor(a)", placeholder="Nome do diretor")
                num_estudantes = st.number_input("👥 Número de estudantes", min_value=1, value=100)
            
            observacoes = st.text_area("📝 Observações", placeholder="Observações adicionais (opcional)")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                submit = st.form_submit_button("✨ Adicionar Escola", use_container_width=True)
            
            if submit:
                if nome and endereco:
                    show_success_message(f"Escola {nome} adicionada com sucesso!")
                else:
                    show_error_message("Por favor, preencha todos os campos obrigatórios")

def reports_page():
    """Página de relatórios com design melhorado"""
    st.markdown("# 📊 Relatórios e Análises")
    st.markdown("Análises detalhadas e relatórios do sistema")
    
    tab1, tab2, tab3 = st.tabs(["📈 Relatórios Gerais", "🏫 Análise por Escola", "👤 Evolução Individual"])
    
    with tab1:
        st.markdown("### 📊 Métricas Gerais do Sistema")
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #28a745; margin: 0;">📊 Média Geral</h3>
                <h2 style="margin: 0.5rem 0;">72.5%</h2>
                <p style="color: #28a745; margin: 0;">+2.3% este mês</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #17a2b8; margin: 0;">⭐ Excelente</h3>
                <h2 style="margin: 0.5rem 0;">25%</h2>
                <p style="color: #28a745; margin: 0;">+5% este mês</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #ffc107; margin: 0;">⚠️ Atenção</h3>
                <h2 style="margin: 0.5rem 0;">15%</h2>
                <p style="color: #28a745; margin: 0;">-3% este mês</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #667eea; margin: 0;">📋 Total</h3>
                <h2 style="margin: 0.5rem 0;">128</h2>
                <p style="color: #6c757d; margin: 0;">Avaliações</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Gráficos detalhados
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Distribuição de Classificações")
            labels = ["Excelente", "Boa", "Regular", "Ruim"]
            values = [25, 40, 25, 10]
            colors = ["#28a745", "#17a2b8", "#ffc107", "#dc3545"]
            
            fig = px.bar(x=labels, y=values, 
                        title="Classificações Posturais",
                        color=labels,
                        color_discrete_sequence=colors)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333'),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 Evolução Mensal")
            months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
            scores = [68, 70, 71, 72, 73, 72.5]
            
            fig = px.line(x=months, y=scores, 
                         title="Média Mensal de Postura",
                         markers=True,
                         color_discrete_sequence=["#667eea"])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333')
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### 🏫 Análise Detalhada por Escola")
        
        escola_selecionada = st.selectbox(
            "Selecione uma escola para análise:",
            ["Escola ABC", "Escola XYZ", "Colégio Central"]
        )
        
        st.markdown(f"#### 📊 Relatório para: {escola_selecionada}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #667eea; margin: 0;">👥 Estudantes</h3>
                <h2 style="margin: 0.5rem 0;">150</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #667eea; margin: 0;">📋 Avaliações</h3>
                <h2 style="margin: 0.5rem 0;">120</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #28a745; margin: 0;">📊 Média</h3>
                <h2 style="margin: 0.5rem 0;">75.2%</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #ffc107; margin: 0;">📅 Última</h3>
                <h2 style="margin: 0.5rem 0;">15/01</h2>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 👤 Evolução Individual do Estudante")
        
        estudante_selecionado = st.selectbox(
            "Selecione um estudante:",
            ["João Silva", "Maria Santos", "Pedro Oliveira"]
        )
        
        st.markdown(f"#### 📈 Progresso de: {estudante_selecionado}")
        
        # Gráfico de evolução individual
        dates = pd.date_range("2024-01-01", periods=6, freq="M")
        scores = [65, 68, 72, 75, 78, 80]
        
        df_evolution = pd.DataFrame({"Data": dates, "Score": scores})
        
        fig = px.line(df_evolution, x="Data", y="Score", 
                     title=f"Evolução Postural - {estudante_selecionado}",
                     markers=True,
                     color_discrete_sequence=["#667eea"])
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Resumo da evolução
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #667eea; margin: 0;">📊 Score Atual</h3>
                <h2 style="margin: 0.5rem 0;">80%</h2>
                <p style="color: #28a745; margin: 0;">+15 pontos</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #28a745; margin: 0;">📈 Melhoria</h3>
                <h2 style="margin: 0.5rem 0;">+23%</h2>
                <p style="color: #28a745; margin: 0;">Últimos 6 meses</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #17a2b8; margin: 0;">🎯 Meta</h3>
                <h2 style="margin: 0.5rem 0;">85%</h2>
                <p style="color: #ffc107; margin: 0;">5 pontos restantes</p>
            </div>
            """, unsafe_allow_html=True)

# Função principal
def main():
    # Inicializar estado da sessão
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # Verificar se está logado
    if not st.session_state.logged_in:
        login_page()
        return
    
    # Sidebar com menu melhorado
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 1rem;">
            <img src="data:image/png;base64,{logo_base64}" alt="Postura+ Logo" style="width: 100px; margin-bottom: 1rem;">
            <h2 style="color: white; margin: 0;">Postura+</h2>
            <p style="color: rgba(255,255,255,0.8); margin: 0;">Menu Principal</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Informações do usuário
        if hasattr(st.session_state, 'user') and st.session_state.user:
            user_info = st.session_state.user
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                <p style="margin: 0;"><strong>👤 {user_info.get('nome', 'N/A')}</strong></p>
                <p style="margin: 0; color: #6c757d; font-size: 0.9rem;">{user_info.get('tipo_usuario', 'N/A').replace('_', ' ').title()}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Menu de navegação
        selected = option_menu(
            menu_title=None,
            options=["Dashboard", "Análise Postural", "Exercícios", "Estudantes", "Escolas", "Relatórios"],
            icons=["house-fill", "camera-fill", "person-arms-up", "people-fill", "building-fill", "graph-up"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#667eea", "font-size": "18px"}, 
                "nav-link": {
                    "font-size": "16px", 
                    "text-align": "left", 
                    "margin": "0px", 
                    "--hover-color": "#f0f2f6",
                    "border-radius": "10px",
                    "padding": "10px"
                },
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    "color": "white"
                },
            }
        )
        
        st.markdown("---")
        
        # Botão de logout melhorado
        if st.button("🚪 Sair do Sistema", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            if hasattr(st.session_state, 'analysis_results'):
                del st.session_state.analysis_results
            if hasattr(st.session_state, 'exercise_started'):
                del st.session_state.exercise_started
            if hasattr(st.session_state, 'exercise_progress'):
                del st.session_state.exercise_progress
            show_success_message("Logout realizado com sucesso!")
            time.sleep(1)
            st.rerun()
    
    # Renderizar página selecionada
    if selected == "Dashboard":
        dashboard_page()
    elif selected == "Análise Postural":
        posture_analysis_page()
    elif selected == "Exercícios":
        vr_exercises_page()
    elif selected == "Estudantes":
        students_page()
    elif selected == "Escolas":
        schools_page()
    elif selected == "Relatórios":
        reports_page()

if __name__ == "__main__":
    main()