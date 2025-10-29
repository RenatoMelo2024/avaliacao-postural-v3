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
import os

# Configuração da página
st.set_page_config(
    page_title="PosturaAI - Avaliação Postural Digital",
    page_icon="assets/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para melhorar a aparência
st.markdown("""
<style>
    /* Estilo geral */
    .main {
        padding-top: 1rem;
    }
    
    /* Header personalizado com logo */
    .header-container {
        background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .header-logo {
        max-height: 80px;
        margin-bottom: 1rem;
    }
    
    .header-title {
        font-size: 2.8rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .header-subtitle {
        font-size: 1.3rem;
        opacity: 0.95;
        font-weight: 300;
    }
    
    /* Cards personalizados */
    .metric-card {
        background: white;
        padding: 1.8rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 5px solid #4ecdc4;
        margin-bottom: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .exercise-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 1rem 0;
        transition: all 0.3s ease;
        border: 1px solid #f0f2f6;
    }
    
    .exercise-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 35px rgba(0,0,0,0.15);
        border-color: #4ecdc4;
    }
    
    /* Botões personalizados */
    .stButton > button {
        background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.7rem 2.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(78, 205, 196, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(78, 205, 196, 0.4);
        background: linear-gradient(135deg, #44a08d 0%, #4ecdc4 100%);
    }
    
    /* Sidebar personalizada */
    .css-1d391kg {
        background: linear-gradient(180deg, #4ecdc4 0%, #44a08d 100%);
    }
    
    /* Formulários */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 12px;
        border: 2px solid #e1e5e9;
        padding: 0.8rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #4ecdc4;
        box-shadow: 0 0 0 0.2rem rgba(78, 205, 196, 0.25);
    }
    
    /* Alertas personalizados */
    .alert-success {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #b8dabd;
        color: #155724;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .alert-error {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border: 1px solid #f1b0b7;
        color: #721c24;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Animações */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    .slide-in {
        animation: slideIn 0.5s ease-out;
    }
    
    /* Progress bar personalizada */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        border-radius: 10px;
    }
    
    /* Tabs personalizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f8f9fa;
        border-radius: 10px;
        color: #495057;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        color: white;
    }
    
    /* Dataframe personalizado */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    /* Sidebar logo */
    .sidebar-logo {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .sidebar-logo img {
        max-height: 60px;
        margin-bottom: 0.5rem;
    }
    
    .sidebar-logo h2 {
        color: white;
        margin: 0;
        font-size: 1.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    .sidebar-logo p {
        color: rgba(255,255,255,0.9);
        margin: 0;
        font-size: 0.9rem;
    }
    
    /* User info card */
    .user-info-card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
    }
    
    /* Expander personalizado */
    .streamlit-expanderHeader {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 0.5rem;
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
    """Exibe o cabeçalho personalizado com logo"""
    # Verificar se a logo existe
    logo_path = "assets/logo_header.png"
    if os.path.exists(logo_path):
        logo_base64 = get_image_base64(logo_path)
        st.markdown(f"""
        <div class="header-container fade-in">
            <img src="data:image/png;base64,{logo_base64}" class="header-logo" alt="PosturaAI Logo">
            <div class="header-title">PosturaAI</div>
            <div class="header-subtitle">Sistema Inteligente de Avaliação Postural Digital</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="header-container fade-in">
            <div class="header-title">🏥 PosturaAI</div>
            <div class="header-subtitle">Sistema Inteligente de Avaliação Postural Digital</div>
        </div>
        """, unsafe_allow_html=True)

def get_image_base64(image_path):
    """Converte imagem local para base64"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

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
        <div class="metric-card slide-in">
            <h3 style="color: #4ecdc4; margin: 0; font-size: 1.1rem;">Score Geral</h3>
            <h2 style="margin: 0.5rem 0; color: #2c3e50;">{score:.1f}%</h2>
            <p style="color: #7f8c8d; margin: 0; font-size: 0.9rem;">Avaliação global</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        classification = metrics.get("posture_classification", "N/A")
        st.markdown(f"""
        <div class="metric-card slide-in">
            <h3 style="color: #4ecdc4; margin: 0; font-size: 1.1rem;">Classificação</h3>
            <h2 style="margin: 0.5rem 0; color: #2c3e50;">{classification}</h2>
            <p style="color: #7f8c8d; margin: 0; font-size: 0.9rem;">Status postural</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        head_score = metrics.get("head_alignment_score", 0)
        st.markdown(f"""
        <div class="metric-card slide-in">
            <h3 style="color: #4ecdc4; margin: 0; font-size: 1.1rem;">Cabeça</h3>
            <h2 style="margin: 0.5rem 0; color: #2c3e50;">{head_score:.1f}%</h2>
            <p style="color: #7f8c8d; margin: 0; font-size: 0.9rem;">Alinhamento</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        shoulder_score = metrics.get("shoulder_alignment_score", 0)
        st.markdown(f"""
        <div class="metric-card slide-in">
            <h3 style="color: #4ecdc4; margin: 0; font-size: 1.1rem;">Ombros</h3>
            <h2 style="margin: 0.5rem 0; color: #2c3e50;">{shoulder_score:.1f}%</h2>
            <p style="color: #7f8c8d; margin: 0; font-size: 0.9rem;">Simetria</p>
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
            st.markdown("Entre com suas credenciais para acessar o sistema")
            
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
            st.markdown("Preencha os dados abaixo para criar sua conta")
            
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
        <div class="metric-card slide-in">
            <h3 style="color: #4ecdc4; margin: 0; font-size: 1.1rem;">👥 Estudantes</h3>
            <h2 style="margin: 0.5rem 0; color: #2c3e50;">45</h2>
            <p style="color: #28a745; margin: 0; font-size: 0.9rem;">+12% este mês</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card slide-in">
            <h3 style="color: #4ecdc4; margin: 0; font-size: 1.1rem;">📋 Avaliações</h3>
            <h2 style="margin: 0.5rem 0; color: #2c3e50;">128</h2>
            <p style="color: #28a745; margin: 0; font-size: 0.9rem;">+8% este mês</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card slide-in">
            <h3 style="color: #4ecdc4; margin: 0; font-size: 1.1rem;">🧘 Exercícios</h3>
            <h2 style="margin: 0.5rem 0; color: #2c3e50;">89</h2>
            <p style="color: #28a745; margin: 0; font-size: 0.9rem;">+23% este mês</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card slide-in">
            <h3 style="color: #4ecdc4; margin: 0; font-size: 1.1rem;">📅 Próximas</h3>
            <h2 style="margin: 0.5rem 0; color: #2c3e50;">12</h2>
            <p style="color: #ffc107; margin: 0; font-size: 0.9rem;">Avaliações agendadas</p>
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
                     color_discrete_sequence=["#4ecdc4"])
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333'),
            title_font_size=16,
            title_x=0.5
        )
        fig.update_traces(line=dict(width=3))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Classificação Postural")
        labels = ["Excelente", "Boa", "Regular", "Ruim"]
        values = [25, 35, 30, 10]
        colors = ["#28a745", "#4ecdc4", "#ffc107", "#dc3545"]
        
        fig = px.pie(values=values, names=labels, 
                    title="Distribuição das Classificações",
                    color_discrete_sequence=colors)
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333'),
            title_font_size=16,
            title_x=0.5
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Atividades recentes com design melhorado
    st.markdown("### 🕐 Atividades Recentes")
    activities = [
        {"atividade": "Avaliação postural realizada para João Silva", "tempo": "2 horas atrás", "icon": "📋", "color": "#4ecdc4"},
        {"atividade": "Sessão de exercícios completada por Maria Santos", "tempo": "4 horas atrás", "icon": "🧘", "color": "#28a745"},
        {"atividade": "Relatório mensal gerado para Escola ABC", "tempo": "1 dia atrás", "icon": "📊", "color": "#17a2b8"},
    ]
    
    for activity in activities:
        st.markdown(f"""
        <div class="metric-card slide-in">
            <p style="margin: 0; color: {activity['color']};"><strong>{activity['icon']} {activity['atividade']}</strong></p>
            <p style="color: #6c757d; margin: 0.5rem 0 0 0; font-size: 0.9rem;"><em>{activity['tempo']}</em></p>
        </div>
        """, unsafe_allow_html=True)

def posture_analysis_page():
    """Página de análise postural com design melhorado"""
    st.markdown("# 📷 Análise Postural Inteligente")
    st.markdown("Faça upload de uma imagem para análise postural automática usando inteligência artificial.")
    
    # Instruções melhoradas
    with st.expander("📋 Como usar a análise postural", expanded=False):
        st.markdown("""
        **Instruções para melhor resultado:**
        
        🔹 **Posicionamento:** Use uma foto de corpo inteiro, de frente para a câmera
        
        🔹 **Postura:** Mantenha-se em pé, relaxado, com os braços ao lado do corpo
        
        🔹 **Iluminação:** Certifique-se de ter boa iluminação, evite sombras
        
        🔹 **Vestimenta:** Use roupas que permitam ver a silhueta do corpo
        
        🔹 **Câmera:** Mantenha a câmera na altura do peito, a cerca de 2-3 metros de distância
        
        🔹 **Fundo:** Prefira um fundo neutro e sem distrações
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
                    status_text = st.empty()
                    
                    steps = [
                        "Carregando imagem...",
                        "Detectando pontos corporais...",
                        "Calculando métricas posturais...",
                        "Gerando relatório...",
                        "Finalizando análise..."
                    ]
                    
                    for i, step in enumerate(steps):
                        status_text.text(step)
                        for j in range(20):
                            progress_bar.progress((i * 20 + j + 1))
                            time.sleep(0.01)
                    
                    status_text.text("Análise concluída!")
                    
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
            "benefits": ["Reduz tensão cervical", "Melhora flexibilidade", "Alivia dores de cabeça"],
            "instructions": [
                "Sente-se com a coluna ereta e ombros relaxados",
                "Incline a cabeça lentamente para a direita por 15 segundos",
                "Retorne ao centro e repita para o lado esquerdo",
                "Faça movimentos circulares suaves no sentido horário",
                "Repita no sentido anti-horário para finalizar"
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
            "color": "#4ecdc4",
            "benefits": ["Fortalece abdômen", "Melhora estabilidade", "Protege a coluna"],
            "instructions": [
                "Deite-se de costas em uma superfície firme",
                "Flexione os joelhos mantendo os pés no chão",
                "Contraia o abdômen e levante o tronco lentamente",
                "Mantenha a posição por 5 segundos",
                "Desça controladamente e repita o movimento"
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
            "benefits": ["Aumenta consciência corporal", "Corrige postura", "Desenvolve hábitos saudáveis"],
            "instructions": [
                "Fique em pé diante de um espelho",
                "Observe sua postura atual sem julgamentos",
                "Alinhe a cabeça sobre os ombros suavemente",
                "Mantenha os ombros relaxados e nivelados",
                "Respire profundamente mantendo o alinhamento"
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
            "benefits": ["Reduz estresse", "Relaxa músculos", "Melhora bem-estar"],
            "instructions": [
                "Encontre uma posição confortável (sentado ou deitado)",
                "Feche os olhos e relaxe completamente",
                "Respire profundamente pelo nariz",
                "Relaxe cada grupo muscular progressivamente",
                "Mantenha o foco na respiração e no momento presente"
            ]
        }
    ]
    
    # Grid de exercícios com cards melhorados
    cols = st.columns(2)
    
    for i, exercise in enumerate(exercises):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="exercise-card fade-in">
                <h3 style="color: {exercise['color']}; margin-top: 0; font-size: 1.3rem;">
                    {exercise['icon']} {exercise['title']}
                </h3>
                <p style="color: #6c757d; margin-bottom: 1rem; font-size: 1rem;">{exercise['description']}</p>
                
                <div style="display: flex; gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap;">
                    <span style="background: #e9ecef; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem;">
                        ⏱️ {exercise['duration']}
                    </span>
                    <span style="background: #e9ecef; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem;">
                        📊 {exercise['difficulty']}
                    </span>
                    <span style="background: #e9ecef; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem;">
                        🏷️ {exercise['category']}
                    </span>
                </div>
                
                <div style="margin-bottom: 1rem;">
                    <strong style="color: {exercise['color']};">Benefícios:</strong>
                    <ul style="margin: 0.5rem 0; padding-left: 1.2rem;">
                        {"".join([f"<li style='margin: 0.2rem 0;'>{benefit}</li>" for benefit in exercise['benefits']])}
                    </ul>
                </div>
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
        st.markdown(f"""
        ## 🏃 Sessão Ativa: {exercise['title']}
        <p style="color: #6c757d; font-size: 1.1rem; margin-bottom: 1.5rem;">{exercise['description']}</p>
        """, unsafe_allow_html=True)
        
        # Barra de progresso melhorada
        if 'exercise_progress' not in st.session_state:
            st.session_state.exercise_progress = 0
        
        progress_percentage = st.session_state.exercise_progress
        current_step = min(len(exercise['instructions']), (progress_percentage // 20) + 1)
        
        st.markdown(f"""
        **Progresso: {progress_percentage}% - Passo {current_step}/{len(exercise['instructions'])}**
        """)
        progress_bar = st.progress(progress_percentage / 100)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📋 Instruções Passo a Passo")
            for i, instruction in enumerate(exercise['instructions'], 1):
                if i <= current_step:
                    if i == current_step and progress_percentage < 100:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%); 
                                   color: white; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                            <strong>🎯 PASSO ATUAL {i}:</strong> {instruction}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"✅ **{i}.** {instruction}")
                else:
                    st.markdown(f"⏳ **{i}.** {instruction}")
        
        with col2:
            st.markdown("### 🎮 Controles")
            
            if progress_percentage < 100:
                if st.button("▶️ Próximo Passo", use_container_width=True):
                    st.session_state.exercise_progress = min(100, progress_percentage + 20)
                    st.rerun()
                
                if st.button("⏸️ Pausar", use_container_width=True):
                    show_success_message("Exercício pausado. Clique em 'Próximo Passo' para continuar.")
            
            if st.button("⏹️ Finalizar Sessão", use_container_width=True):
                st.session_state.exercise_started = False
                st.session_state.exercise_progress = 0
                show_success_message("Sessão finalizada com sucesso!")
                st.rerun()
            
            # Informações do exercício
            st.markdown("### ℹ️ Informações")
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin-top: 1rem;">
                <p><strong>⏱️ Duração:</strong> {exercise['duration']}</p>
                <p><strong>📊 Dificuldade:</strong> {exercise['difficulty']}</p>
                <p><strong>🏷️ Categoria:</strong> {exercise['category']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        if progress_percentage >= 100:
            st.markdown("### 🎉 Parabéns!")
            st.markdown("Você concluiu o exercício com sucesso! Continue praticando para melhores resultados.")
            st.balloons()

def students_page():
    """Página de gerenciamento de estudantes com design melhorado"""
    st.markdown("# 👥 Gerenciamento de Estudantes")
    st.markdown("Gerencie os estudantes cadastrados no sistema")
    
    tab1, tab2 = st.tabs(["📋 Lista de Estudantes", "➕ Adicionar Estudante"])
    
    with tab1:
        st.markdown("### 📊 Estudantes Cadastrados")
        
        # Filtros aprimorados
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            search_name = st.text_input("🔍 Buscar por nome", placeholder="Digite o nome...")
        with col2:
            filter_school = st.selectbox("🏫 Filtrar por escola", ["Todas", "Escola ABC", "Escola XYZ", "Colégio Central"])
        with col3:
            filter_age = st.selectbox("👶 Filtrar por idade", ["Todas", "12-14 anos", "15-17 anos", "18+ anos"])
        with col4:
            filter_status = st.selectbox("📊 Status", ["Todos", "Ativo", "Inativo"])
        
        # Dados mockados aprimorados
        students_data = [
            {"ID": 1, "Nome": "João Silva", "Idade": 15, "Escola": "Escola ABC", "Turma": "9º A", "Última Avaliação": "2024-01-15", "Score": "78%", "Status": "Ativo"},
            {"ID": 2, "Nome": "Maria Santos", "Idade": 16, "Escola": "Escola XYZ", "Turma": "1º B", "Última Avaliação": "2024-01-10", "Score": "85%", "Status": "Ativo"},
            {"ID": 3, "Nome": "Pedro Oliveira", "Idade": 14, "Escola": "Escola ABC", "Turma": "8º C", "Última Avaliação": "2024-01-12", "Score": "72%", "Status": "Ativo"},
            {"ID": 4, "Nome": "Ana Costa", "Idade": 17, "Escola": "Colégio Central", "Turma": "2º A", "Última Avaliação": "2024-01-08", "Score": "91%", "Status": "Ativo"},
        ]
        
        df = pd.DataFrame(students_data)
        
        # Aplicar filtros
        if search_name:
            df = df[df['Nome'].str.contains(search_name, case=False, na=False)]
        if filter_school != "Todas":
            df = df[df['Escola'] == filter_school]
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Estatísticas rápidas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Estudantes", len(df))
        with col2:
            avg_score = df['Score'].str.replace('%', '').astype(float).mean()
            st.metric("Score Médio", f"{avg_score:.1f}%")
        with col3:
            active_students = len(df[df['Status'] == 'Ativo'])
            st.metric("Estudantes Ativos", active_students)
    
    with tab2:
        st.markdown("### ➕ Adicionar Novo Estudante")
        
        with st.form("student_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("👤 Nome completo", placeholder="Digite o nome completo")
                idade = st.number_input("🎂 Idade", min_value=5, max_value=25, value=15)
                genero = st.selectbox("⚧️ Gênero", ["Masculino", "Feminino", "Outro"])
                escola = st.text_input("🏫 Escola", placeholder="Nome da escola")
            
            with col2:
                turma = st.text_input("📚 Turma", placeholder="Ex: 9º Ano A")
                responsavel = st.text_input("👨‍👩‍👧‍👦 Responsável", placeholder="Nome do responsável")
                telefone = st.text_input("📞 Telefone do responsável", placeholder="(11) 99999-9999")
                email_responsavel = st.text_input("📧 Email do responsável", placeholder="responsavel@email.com")
            
            observacoes = st.text_area("📝 Observações", placeholder="Observações médicas ou outras informações relevantes (opcional)")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                submit = st.form_submit_button("✨ Adicionar Estudante", use_container_width=True)
            
            if submit:
                if nome and escola and responsavel:
                    show_success_message(f"Estudante {nome} adicionado com sucesso!")
                else:
                    show_error_message("Por favor, preencha todos os campos obrigatórios (Nome, Escola e Responsável)")

def schools_page():
    """Página de gerenciamento de escolas com design melhorado"""
    st.markdown("# 🏫 Gerenciamento de Escolas")
    st.markdown("Gerencie as escolas parceiras do sistema")
    
    tab1, tab2 = st.tabs(["📋 Lista de Escolas", "➕ Adicionar Escola"])
    
    with tab1:
        st.markdown("### 📊 Escolas Cadastradas")
        
        # Dados mockados com mais informações
        schools_data = [
            {"ID": 1, "Nome": "Escola ABC", "Endereço": "Rua A, 123 - Centro", "Estudantes": 150, "Avaliações": 120, "Score Médio": "76%", "Status": "Ativa", "Contato": "(11) 9999-9999"},
            {"ID": 2, "Nome": "Escola XYZ", "Endereço": "Rua B, 456 - Vila Nova", "Estudantes": 200, "Avaliações": 180, "Score Médio": "82%", "Status": "Ativa", "Contato": "(11) 8888-8888"},
            {"ID": 3, "Nome": "Colégio Central", "Endereço": "Av. C, 789 - Centro", "Estudantes": 300, "Avaliações": 250, "Score Médio": "79%", "Status": "Ativa", "Contato": "(11) 7777-7777"},
        ]
        
        df = pd.DataFrame(schools_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Estatísticas das escolas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Escolas", len(df))
        with col2:
            total_students = df['Estudantes'].sum()
            st.metric("Total de Estudantes", total_students)
        with col3:
            total_evaluations = df['Avaliações'].sum()
            st.metric("Total de Avaliações", total_evaluations)
        with col4:
            avg_score = df['Score Médio'].str.replace('%', '').astype(float).mean()
            st.metric("Score Médio Geral", f"{avg_score:.1f}%")
    
    with tab2:
        st.markdown("### ➕ Adicionar Nova Escola")
        
        with st.form("school_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("🏫 Nome da escola", placeholder="Digite o nome da escola")
                endereco = st.text_area("📍 Endereço", placeholder="Endereço completo com CEP")
                telefone = st.text_input("📞 Telefone", placeholder="(11) 9999-9999")
                email = st.text_input("📧 Email", placeholder="contato@escola.com")
            
            with col2:
                diretor = st.text_input("👨‍💼 Diretor(a)", placeholder="Nome do diretor")
                num_estudantes = st.number_input("👥 Número de estudantes", min_value=1, value=100)
                tipo_escola = st.selectbox("🏷️ Tipo de escola", ["Pública", "Privada", "Técnica", "Universitária"])
                nivel_ensino = st.multiselect("📚 Níveis de ensino", ["Fundamental I", "Fundamental II", "Ensino Médio", "Técnico", "Superior"])
            
            observacoes = st.text_area("📝 Observações", placeholder="Informações adicionais sobre a escola (opcional)")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                submit = st.form_submit_button("✨ Adicionar Escola", use_container_width=True)
            
            if submit:
                if nome and endereco and telefone:
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
            <div class="metric-card slide-in">
                <h3 style="color: #28a745; margin: 0; font-size: 1.1rem;">📊 Média Geral</h3>
                <h2 style="margin: 0.5rem 0; color: #2c3e50;">78.5%</h2>
                <p style="color: #28a745; margin: 0; font-size: 0.9rem;">+3.2% este mês</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card slide-in">
                <h3 style="color: #4ecdc4; margin: 0; font-size: 1.1rem;">⭐ Excelente</h3>
                <h2 style="margin: 0.5rem 0; color: #2c3e50;">28%</h2>
                <p style="color: #28a745; margin: 0; font-size: 0.9rem;">+7% este mês</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card slide-in">
                <h3 style="color: #ffc107; margin: 0; font-size: 1.1rem;">⚠️ Atenção</h3>
                <h2 style="margin: 0.5rem 0; color: #2c3e50;">12%</h2>
                <p style="color: #28a745; margin: 0; font-size: 0.9rem;">-5% este mês</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card slide-in">
                <h3 style="color: #dc3545; margin: 0; font-size: 1.1rem;">🚨 Crítico</h3>
                <h2 style="margin: 0.5rem 0; color: #2c3e50;">3%</h2>
                <p style="color: #28a745; margin: 0; font-size: 0.9rem;">-2% este mês</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Gráficos detalhados
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Distribuição de Classificações")
            labels = ["Excelente", "Boa", "Regular", "Ruim"]
            values = [28, 42, 27, 3]
            colors = ["#28a745", "#4ecdc4", "#ffc107", "#dc3545"]
            
            fig = px.bar(x=labels, y=values, 
                        title="Classificações Posturais (%)",
                        color=labels,
                        color_discrete_sequence=colors)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333'),
                showlegend=False,
                title_font_size=16,
                title_x=0.5
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 Evolução Mensal")
            months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
            scores = [72, 74, 75, 76, 77, 78.5]
            
            fig = px.line(x=months, y=scores, 
                         title="Média Mensal de Postura (%)",
                         markers=True,
                         color_discrete_sequence=["#4ecdc4"])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333'),
                title_font_size=16,
                title_x=0.5
            )
            fig.update_traces(line=dict(width=3), marker=dict(size=8))
            st.plotly_chart(fig, use_container_width=True)
        
        # Análise por faixa etária
        st.markdown("### 👶 Análise por Faixa Etária")
        age_data = {
            "Faixa Etária": ["12-14 anos", "15-17 anos", "18+ anos"],
            "Quantidade": [45, 78, 32],
            "Score Médio": [76, 79, 82]
        }
        
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(x=age_data["Faixa Etária"], y=age_data["Quantidade"],
                        title="Distribuição por Idade",
                        color_discrete_sequence=["#4ecdc4"])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333'),
                title_font_size=16,
                title_x=0.5
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(x=age_data["Faixa Etária"], y=age_data["Score Médio"],
                        title="Score Médio por Idade (%)",
                        color_discrete_sequence=["#28a745"])
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#333'),
                title_font_size=16,
                title_x=0.5
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### 🏫 Análise Detalhada por Escola")
        
        escola_selecionada = st.selectbox(
            "Selecione uma escola para análise:",
            ["Escola ABC", "Escola XYZ", "Colégio Central"]
        )
        
        st.markdown(f"#### 📊 Relatório Completo: {escola_selecionada}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card slide-in">
                <h3 style="color: #4ecdc4; margin: 0; font-size: 1rem;">👥 Estudantes</h3>
                <h2 style="margin: 0.5rem 0; color: #2c3e50;">150</h2>
                <p style="color: #6c757d; margin: 0; font-size: 0.8rem;">Total cadastrados</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card slide-in">
                <h3 style="color: #4ecdc4; margin: 0; font-size: 1rem;">📋 Avaliações</h3>
                <h2 style="margin: 0.5rem 0; color: #2c3e50;">120</h2>
                <p style="color: #6c757d; margin: 0; font-size: 0.8rem;">Realizadas</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card slide-in">
                <h3 style="color: #28a745; margin: 0; font-size: 1rem;">📊 Score Médio</h3>
                <h2 style="margin: 0.5rem 0; color: #2c3e50;">76.2%</h2>
                <p style="color: #28a745; margin: 0; font-size: 0.8rem;">+2.1% este mês</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card slide-in">
                <h3 style="color: #ffc107; margin: 0; font-size: 1rem;">📅 Última</h3>
                <h2 style="margin: 0.5rem 0; color: #2c3e50;">15/01</h2>
                <p style="color: #6c757d; margin: 0; font-size: 0.8rem;">Avaliação</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Gráfico específico da escola
        st.markdown("### 📈 Evolução da Escola")
        months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
        school_scores = [74, 75, 75.5, 76, 76.1, 76.2]
        
        fig = px.line(x=months, y=school_scores, 
                     title=f"Evolução do Score - {escola_selecionada}",
                     markers=True,
                     color_discrete_sequence=["#4ecdc4"])
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333'),
            title_font_size=16,
            title_x=0.5
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=8))
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### 👤 Evolução Individual do Estudante")
        
        estudante_selecionado = st.selectbox(
            "Selecione um estudante:",
            ["João Silva", "Maria Santos", "Pedro Oliveira", "Ana Costa"]
        )
        
        st.markdown(f"#### 📈 Progresso Detalhado: {estudante_selecionado}")
        
        # Gráfico de evolução individual
        dates = pd.date_range("2024-01-01", periods=6, freq="M")
        scores = [65, 68, 72, 75, 78, 82]
        
        df_evolution = pd.DataFrame({"Data": dates, "Score": scores})
        
        fig = px.line(df_evolution, x="Data", y="Score", 
                     title=f"Evolução Postural - {estudante_selecionado}",
                     markers=True,
                     color_discrete_sequence=["#4ecdc4"])
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333'),
            title_font_size=16,
            title_x=0.5
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=8))
        st.plotly_chart(fig, use_container_width=True)
        
        # Resumo da evolução
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card slide-in">
                <h3 style="color: #4ecdc4; margin: 0; font-size: 1rem;">📊 Score Atual</h3>
                <h2 style="margin: 0.5rem 0; color: #2c3e50;">82%</h2>
                <p style="color: #28a745; margin: 0; font-size: 0.8rem;">+17 pontos</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card slide-in">
                <h3 style="color: #28a745; margin: 0; font-size: 1rem;">📈 Melhoria</h3>
                <h2 style="margin: 0.5rem 0; color: #2c3e50;">+26%</h2>
                <p style="color: #28a745; margin: 0; font-size: 0.8rem;">Últimos 6 meses</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card slide-in">
                <h3 style="color: #17a2b8; margin: 0; font-size: 1rem;">🎯 Meta</h3>
                <h2 style="margin: 0.5rem 0; color: #2c3e50;">85%</h2>
                <p style="color: #ffc107; margin: 0; font-size: 0.8rem;">3 pontos restantes</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card slide-in">
                <h3 style="color: #6f42c1; margin: 0; font-size: 1rem;">🏆 Ranking</h3>
                <h2 style="margin: 0.5rem 0; color: #2c3e50;">2º</h2>
                <p style="color: #6c757d; margin: 0; font-size: 0.8rem;">Na turma</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Recomendações personalizadas
        st.markdown("### 💡 Recomendações Personalizadas")
        recommendations = [
            "Continue praticando os exercícios de alongamento cervical",
            "Foque em exercícios de fortalecimento do core",
            "Mantenha a consciência postural durante as atividades diárias",
            "Agende uma nova avaliação em 30 dias"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid #4ecdc4;">
                <strong>{i}.</strong> {rec}
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
        # Logo na sidebar
        logo_path = "assets/logo_header.png"
        if os.path.exists(logo_path):
            logo_base64 = get_image_base64(logo_path)
            st.markdown(f"""
            <div class="sidebar-logo">
                <img src="data:image/png;base64,{logo_base64}" alt="PosturaAI Logo">
                <h2>PosturaAI</h2>
                <p>Menu Principal</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="sidebar-logo">
                <h2>🏥 PosturaAI</h2>
                <p>Menu Principal</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Informações do usuário
        if hasattr(st.session_state, 'user') and st.session_state.user:
            user_info = st.session_state.user
            st.markdown(f"""
            <div class="user-info-card">
                <p style="margin: 0; color: #4ecdc4;"><strong>👤 {user_info.get('nome', 'N/A')}</strong></p>
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
                "icon": {"color": "#4ecdc4", "font-size": "18px"}, 
                "nav-link": {
                    "font-size": "16px", 
                    "text-align": "left", 
                    "margin": "0px", 
                    "--hover-color": "#f0f2f6",
                    "border-radius": "12px",
                    "padding": "12px 16px",
                    "transition": "all 0.3s ease"
                },
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%)",
                    "color": "white",
                    "box-shadow": "0 4px 15px rgba(78, 205, 196, 0.3)"
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
        
        # Informações do sistema
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #6c757d; font-size: 0.8rem;">
            <p>PosturaAI v2.0</p>
            <p>Sistema Inteligente de<br>Avaliação Postural</p>
        </div>
        """, unsafe_allow_html=True)
    
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

