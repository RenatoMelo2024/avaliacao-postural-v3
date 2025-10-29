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

# Configuração da página
st.set_page_config(
    page_title="Avaliação Postura +",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
def image_to_base64(image):
    """Converte imagem PIL para base64"""
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"

def display_posture_results(results):
    """Exibe os resultados da análise postural"""
    if "error" in results:
        st.error(results["error"])
        return
    
    if not results.get("success"):
        st.error("Falha na análise postural")
        return
    
    metrics = results.get("metrics", {})
    report = results.get("report", {})
    
    # Exibir métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score = metrics.get("overall_posture_score", 0)
        st.metric("Score Geral", f"{score:.1f}%")
    
    with col2:
        classification = metrics.get("posture_classification", "N/A")
        st.metric("Classificação", classification)
    
    with col3:
        head_score = metrics.get("head_alignment_score", 0)
        st.metric("Alinhamento da Cabeça", f"{head_score:.1f}%")
    
    with col4:
        shoulder_score = metrics.get("shoulder_alignment_score", 0)
        st.metric("Alinhamento dos Ombros", f"{shoulder_score:.1f}%")
    
    # Exibir imagem anotada
    if "annotated_image" in results:
        st.subheader("Análise Visual")
        st.image(results["annotated_image"], caption="Análise Postural", use_column_width=True)
    
    # Exibir relatório detalhado
    if report:
        st.subheader("Relatório Detalhado")
        
        # Detalhes da análise
        if "details" in report:
            for detail in report["details"]:
                with st.expander(f"{detail['area']} - {detail['status']}"):
                    st.write(f"**Score:** {detail['score']:.1f}%")
                    st.write(f"**Descrição:** {detail['description']}")
        
        # Recomendações
        if "recommendations" in report:
            st.subheader("Recomendações")
            for i, rec in enumerate(report["recommendations"], 1):
                st.write(f"{i}. {rec}")

# Páginas da aplicação
def login_page():
    """Página de login"""
    st.title("📲 Avaliação Postura+")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["Login", "Registro"])
    
    with tab1:
        st.subheader("Fazer Login")
        
        with st.form("login_form"):
            email = st.text_input("Email")
            senha = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar")
            
            if submit:
                if email and senha:
                    with st.spinner("Fazendo login..."):
                        result = api_client.login(email, senha)
                        
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.session_state.user = result.get("usuario")
                        st.session_state.logged_in = True
                        st.success("Login realizado com sucesso!")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.error("Por favor, preencha todos os campos")
    
    with tab2:
        st.subheader("Criar Conta")
        
        with st.form("register_form"):
            nome = st.text_input("Nome completo")
            email_reg = st.text_input("Email", key="email_reg")
            senha_reg = st.text_input("Senha", type="password", key="senha_reg")
            tipo_usuario = st.selectbox(
                "Tipo de usuário",
                ["estudante", "profissional_saude", "gestor_educacional"]
            )
            submit_reg = st.form_submit_button("Criar conta")
            
            if submit_reg:
                if nome and email_reg and senha_reg:
                    user_data = {
                        "nome": nome,
                        "email": email_reg,
                        "senha": senha_reg,
                        "tipo_usuario": tipo_usuario
                    }
                    
                    with st.spinner("Criando conta..."):
                        result = api_client.register(user_data)
                    
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.success("Conta criada com sucesso! Faça login para continuar.")
                else:
                    st.error("Por favor, preencha todos os campos")

def dashboard_page():
    """Página principal do dashboard"""
    st.title("📊 Dashboard")
    
    # Estatísticas mockadas (em uma implementação real, viriam da API)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Estudantes", "45", "+12%")
    
    with col2:
        st.metric("Avaliações Realizadas", "128", "+8%")
    
    with col3:
        st.metric("Sessões de Exercícios", "89", "+23%")
    
    with col4:
        st.metric("Próximas Avaliações", "12")
    
    st.markdown("---")
    
    # Gráficos de exemplo
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Evolução das Avaliações")
        # Dados de exemplo
        dates = pd.date_range("2024-01-01", periods=12, freq="M")
        values = [10, 15, 12, 18, 22, 25, 20, 28, 32, 30, 35, 40]
        df = pd.DataFrame({"Data": dates, "Avaliações": values})
        
        fig = px.line(df, x="Data", y="Avaliações", title="Avaliações por Mês")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Distribuição por Classificação Postural")
        # Dados de exemplo
        labels = ["Excelente", "Boa", "Regular", "Ruim"]
        values = [25, 35, 30, 10]
        
        fig = px.pie(values=values, names=labels, title="Classificação Postural")
        st.plotly_chart(fig, use_container_width=True)
    
    # Atividades recentes
    st.subheader("Atividades Recentes")
    activities = [
        {"atividade": "Avaliação postural realizada para João Silva", "tempo": "2 horas atrás"},
        {"atividade": "Sessão de exercícios completada por Maria Santos", "tempo": "4 horas atrás"},
        {"atividade": "Relatório mensal gerado para Escola ABC", "tempo": "1 dia atrás"},
    ]
    
    for activity in activities:
        st.write(f"• {activity['atividade']} - *{activity['tempo']}*")

def posture_analysis_page():
    """Página de análise postural"""
    st.title("📷 Análise Postural")
    
    st.markdown("""
    Faça upload de uma imagem para análise postural automática.
    A análise detectará pontos corporais e fornecerá métricas sobre o alinhamento postural.
    """)
    
    uploaded_file = st.file_uploader(
        "Escolha uma imagem",
        type=["jpg", "jpeg", "png"],
        help="Formatos suportados: JPG, JPEG, PNG"
    )
    
    if uploaded_file is not None:
        # Exibir imagem carregada
        image = Image.open(uploaded_file)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Imagem Original")
            st.image(image, caption="Imagem carregada", use_column_width=True)
            
            if st.button("Analisar Postura", type="primary"):
                with st.spinner("Analisando postura..."):
                    # Converter imagem para base64
                    image_base64 = image_to_base64(image)
                    
                    # Enviar para análise
                    results = api_client.analyze_posture(image_base64)
                    
                    # Armazenar resultados na sessão
                    st.session_state.analysis_results = results
        
        with col2:
            if hasattr(st.session_state, 'analysis_results'):
                st.subheader("Resultados da Análise")
                display_posture_results(st.session_state.analysis_results)

def vr_exercises_page():
    """Página de exercícios (versão 2D interativa)"""
    st.title("🧘 Exercícios Posturais Interativos")
    
    st.markdown("""
    Versão adaptada dos exercícios de realidade virtual em formato 2D interativo.
    Siga as instruções e visualizações para melhorar sua postura.
    """)
    
    # Lista de exercícios
    exercises = [
        {
            "id": 1,
            "title": "Alongamento Cervical",
            "description": "Exercícios para relaxar e fortalecer os músculos do pescoço",
            "duration": "5 minutos",
            "difficulty": "Iniciante",
            "category": "Pescoço",
            "icon": "🦴",
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
            "instructions": [
                "Encontre uma posição confortável",
                "Feche os olhos",
                "Respire profundamente",
                "Relaxe cada grupo muscular",
                "Mantenha o foco na respiração"
            ]
        }
    ]
    
    # Grid de exercícios
    cols = st.columns(2)
    
    for i, exercise in enumerate(exercises):
        with cols[i % 2]:
            with st.container():
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 10px; padding: 20px; margin: 10px 0;">
                    <h3>{exercise['icon']} {exercise['title']}</h3>
                    <p><strong>Duração:</strong> {exercise['duration']}</p>
                    <p><strong>Dificuldade:</strong> {exercise['difficulty']}</p>
                    <p><strong>Categoria:</strong> {exercise['category']}</p>
                    <p>{exercise['description']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Iniciar {exercise['title']}", key=f"btn_{exercise['id']}"):
                    st.session_state.current_exercise = exercise
                    st.session_state.exercise_started = True
    
    # Sessão de exercício ativa
    if hasattr(st.session_state, 'exercise_started') and st.session_state.exercise_started:
        exercise = st.session_state.current_exercise
        
        st.markdown("---")
        st.subheader(f"🏃 Sessão Ativa: {exercise['title']}")
        
        # Barra de progresso simulada
        if 'exercise_progress' not in st.session_state:
            st.session_state.exercise_progress = 0
        
        progress_bar = st.progress(st.session_state.exercise_progress)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Instruções")
            for i, instruction in enumerate(exercise['instructions'], 1):
                st.write(f"{i}. {instruction}")
        
        with col2:
            st.subheader("Controles")
            
            if st.button("▶️ Continuar"):
                if st.session_state.exercise_progress < 100:
                    st.session_state.exercise_progress += 20
                    st.rerun()
            
            if st.button("⏹️ Finalizar Sessão"):
                st.session_state.exercise_started = False
                st.session_state.exercise_progress = 0
                st.success("Sessão finalizada!")
                st.rerun()
        
        if st.session_state.exercise_progress >= 100:
            st.success("🎉 Exercício concluído! Parabéns!")
            st.balloons()

def students_page():
    """Página de gerenciamento de estudantes"""
    st.title("👥 Gerenciamento de Estudantes")
    
    tab1, tab2 = st.tabs(["Lista de Estudantes", "Adicionar Estudante"])
    
    with tab1:
        st.subheader("Estudantes Cadastrados")
        
        # Buscar estudantes (mockado para demonstração)
        students_data = [
            {"id": 1, "nome": "João Silva", "idade": 15, "escola": "Escola ABC", "ultima_avaliacao": "2024-01-15"},
            {"id": 2, "nome": "Maria Santos", "idade": 16, "escola": "Escola XYZ", "ultima_avaliacao": "2024-01-10"},
            {"id": 3, "nome": "Pedro Oliveira", "idade": 14, "escola": "Escola ABC", "ultima_avaliacao": "2024-01-12"},
        ]
        
        df = pd.DataFrame(students_data)
        st.dataframe(df, use_container_width=True)
    
    with tab2:
        st.subheader("Adicionar Novo Estudante")
        
        with st.form("student_form"):
            nome = st.text_input("Nome completo")
            idade = st.number_input("Idade", min_value=5, max_value=25, value=15)
            escola = st.text_input("Escola")
            genero = st.selectbox("Gênero", ["Masculino", "Feminino", "Outro"])
            
            if st.form_submit_button("Adicionar Estudante"):
                if nome and escola:
                    student_data = {
                        "nome": nome,
                        "idade": idade,
                        "escola": escola,
                        "genero": genero
                    }
                    
                    # Aqui seria feita a chamada para a API
                    st.success(f"Estudante {nome} adicionado com sucesso!")
                else:
                    st.error("Por favor, preencha todos os campos obrigatórios")

def schools_page():
    """Página de gerenciamento de escolas"""
    st.title("🏫 Gerenciamento de Escolas")
    
    tab1, tab2 = st.tabs(["Lista de Escolas", "Adicionar Escola"])
    
    with tab1:
        st.subheader("Escolas Cadastradas")
        
        # Dados mockados
        schools_data = [
            {"id": 1, "nome": "Escola ABC", "endereco": "Rua A, 123", "estudantes": 150},
            {"id": 2, "nome": "Escola XYZ", "endereco": "Rua B, 456", "estudantes": 200},
            {"id": 3, "nome": "Colégio Central", "endereco": "Av. C, 789", "estudantes": 300},
        ]
        
        df = pd.DataFrame(schools_data)
        st.dataframe(df, use_container_width=True)
    
    with tab2:
        st.subheader("Adicionar Nova Escola")
        
        with st.form("school_form"):
            nome = st.text_input("Nome da escola")
            endereco = st.text_area("Endereço")
            
            if st.form_submit_button("Adicionar Escola"):
                if nome and endereco:
                    st.success(f"Escola {nome} adicionada com sucesso!")
                else:
                    st.error("Por favor, preencha todos os campos")

def reports_page():
    """Página de relatórios e análises"""
    st.title("📊 Relatórios e Análises")
    
    tab1, tab2, tab3 = st.tabs(["Relatórios Gerais", "Análise por Escola", "Evolução Individual"])
    
    with tab1:
        st.subheader("Relatórios Gerais")
        
        # Métricas gerais
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Média Geral de Postura", "72.5%", "+2.3%")
        
        with col2:
            st.metric("Estudantes com Postura Excelente", "25%", "+5%")
        
        with col3:
            st.metric("Necessitam Atenção", "15%", "-3%")
        
        # Gráfico de distribuição
        st.subheader("Distribuição de Classificações Posturais")
        
        labels = ["Excelente", "Boa", "Regular", "Ruim"]
        values = [25, 40, 25, 10]
        
        fig = px.bar(x=labels, y=values, title="Distribuição por Classificação")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Análise por Escola")
        
        # Seletor de escola
        escola_selecionada = st.selectbox(
            "Selecione uma escola",
            ["Escola ABC", "Escola XYZ", "Colégio Central"]
        )
        
        # Dados mockados para a escola selecionada
        st.write(f"**Relatório para:** {escola_selecionada}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total de Estudantes", "150")
            st.metric("Avaliações Realizadas", "120")
        
        with col2:
            st.metric("Média de Postura", "75.2%")
            st.metric("Última Avaliação", "15/01/2024")
    
    with tab3:
        st.subheader("Evolução Individual")
        
        # Seletor de estudante
        estudante_selecionado = st.selectbox(
            "Selecione um estudante",
            ["João Silva", "Maria Santos", "Pedro Oliveira"]
        )
        
        # Gráfico de evolução
        dates = pd.date_range("2024-01-01", periods=6, freq="M")
        scores = [65, 68, 72, 75, 78, 80]
        
        df_evolution = pd.DataFrame({"Data": dates, "Score": scores})
        
        fig = px.line(df_evolution, x="Data", y="Score", 
                     title=f"Evolução Postural - {estudante_selecionado}")
        st.plotly_chart(fig, use_container_width=True)

# Função principal
def main():
    # Inicializar estado da sessão
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # Verificar se está logado
    if not st.session_state.logged_in:
        login_page()
        return
    
    # Sidebar com menu
    with st.sidebar:
        st.title("🏥 Menu")
        
        # Informações do usuário
        if hasattr(st.session_state, 'user') and st.session_state.user:
            st.write(f"**Usuário:** {st.session_state.user.get('nome', 'N/A')}")
            st.write(f"**Tipo:** {st.session_state.user.get('tipo_usuario', 'N/A')}")
            st.markdown("---")
        
        # Menu de navegação
        selected = option_menu(
            menu_title=None,
            options=["Dashboard", "Análise Postural", "Exercícios", "Estudantes", "Escolas", "Relatórios"],
            icons=["house", "camera", "person-arms-up", "people", "building", "graph-up"],
            menu_icon="cast",
            default_index=0,
        )
        
        st.markdown("---")
        
        # Botão de logout
        if st.button("🚪 Sair"):
            st.session_state.logged_in = False
            st.session_state.user = None
            if hasattr(st.session_state, 'analysis_results'):
                del st.session_state.analysis_results
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

