# Sistema de Avaliação Postural Digital - Versão Python

## Descrição
Sistema completo de avaliação postural digital desenvolvido inteiramente em Python, com backend Flask e frontend Streamlit. Inclui análise postural com IA, gerenciamento de estudantes e escolas, e módulo de exercícios posturais interativos.

## Funcionalidades Principais

### ✅ Backend (Flask)
- **Autenticação JWT**: Sistema completo de login e registro
- **Análise Postural com IA**: Processamento de imagens usando MediaPipe
- **API REST Completa**: Endpoints para usuários, estudantes, escolas, avaliações
- **Banco de Dados SQLite**: Persistência de dados local
- **CORS Habilitado**: Integração frontend-backend

### ✅ Frontend (Streamlit)
- **Interface Responsiva**: Design moderno e intuitivo
- **Dashboard Interativo**: Estatísticas e visualizações
- **Módulo de Exercícios**: Versão 2D interativa dos exercícios posturais
- **Gerenciamento**: Estudantes, escolas e relatórios
- **Análise Postural**: Upload de imagens e visualização de resultados

### ✅ Funcionalidades Avançadas
- **Análise Postural**: Detecção de pontos corporais e métricas
- **Exercícios Interativos**: Versão 2D dos exercícios de realidade virtual
- **Relatórios**: Gráficos de evolução postural
- **Painel de Gestão**: Para escolas e clínicas

## Estrutura do Projeto

```
avaliacao_postural_python/
├── backend/                          # Backend Flask
│   ├── src/
│   │   ├── main.py                   # Aplicação principal
│   │   ├── models/                   # Modelos de dados
│   │   ├── routes/                   # Rotas da API
│   │   ├── services/                 # Serviços (análise postural)
│   │   └── database/                 # Banco de dados SQLite
│   └── requirements.txt              # Dependências Python
├── frontend/                         # Frontend Streamlit
│   └── app.py                        # Aplicação Streamlit
└── README.md                         # Este arquivo
```

## Instalação e Execução

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Backend (Flask)
```bash
cd backend
pip install -r requirements.txt
python src/main.py
```

O backend estará disponível em: `http://localhost:5000`

### Frontend (Streamlit)
```bash
cd frontend
pip install streamlit streamlit-option-menu plotly
streamlit run app.py
```

O frontend estará disponível em: `http://localhost:8501`

## Tecnologias Utilizadas

### Backend
- **Flask**: Framework web Python
- **SQLite**: Banco de dados
- **MediaPipe**: Análise postural com IA
- **OpenCV**: Processamento de imagens
- **JWT**: Autenticação
- **CORS**: Integração frontend-backend

### Frontend
- **Streamlit**: Framework para aplicações web em Python
- **Plotly**: Gráficos e visualizações interativas
- **Pandas**: Manipulação de dados
- **Pillow**: Processamento de imagens
- **Requests**: Comunicação com API

## Funcionalidades Detalhadas

### 1. Sistema de Autenticação
- Registro e login de usuários
- Tipos: Administrador, Profissional de Saúde, Gestor Educacional
- Interface Streamlit para autenticação

### 2. Análise Postural
- Upload de imagens através do Streamlit
- Detecção automática de pontos corporais
- Cálculo de métricas posturais
- Visualização de resultados com imagens anotadas

### 3. Módulo de Exercícios (Versão 2D)
- 4 exercícios interativos adaptados:
  - Alongamento Cervical (5 min)
  - Fortalecimento do Core (10 min)
  - Postura Consciente (8 min)
  - Relaxamento Guiado (12 min)
- Interface 2D com instruções passo-a-passo
- Simulação de progresso e controles interativos

### 4. Painel de Gestão
- Gerenciamento de estudantes
- Gerenciamento de escolas
- Relatórios e análises
- Visualizações gráficas com Plotly

## API Endpoints

### Autenticação
- `POST /api/auth/register` - Registro de usuário
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout

### Estudantes
- `GET /api/estudantes` - Listar estudantes
- `POST /api/estudantes` - Criar estudante
- `PUT /api/estudantes/<id>` - Atualizar estudante
- `DELETE /api/estudantes/<id>` - Deletar estudante

### Escolas
- `GET /api/escolas` - Listar escolas
- `POST /api/escolas` - Criar escola
- `PUT /api/escolas/<id>` - Atualizar escola
- `DELETE /api/escolas/<id>` - Deletar escola

### Análise Postural
- `POST /api/posture/analyze` - Analisar postura
- `GET /api/posture/history` - Histórico de avaliações

## Diferenças da Versão Original

### Migração do Frontend
- **De:** React + JavaScript
- **Para:** Streamlit + Python
- **Benefícios:** Desenvolvimento mais rápido, sintaxe Python familiar, menos complexidade

### Adaptação do Módulo VR
- **De:** WebXR + A-Frame (Realidade Virtual)
- **Para:** Interface 2D interativa com Streamlit
- **Funcionalidades:** Instruções passo-a-passo, simulação de progresso, controles interativos

### Simplificação da Arquitetura
- **Menos dependências:** Sem Node.js, npm, ou bibliotecas JavaScript
- **Stack unificado:** Tudo em Python
- **Facilidade de manutenção:** Uma linguagem para todo o projeto

## Como Usar

1. **Inicie o backend Flask** (porta 5000)
2. **Inicie o frontend Streamlit** (porta 8501)
3. **Acesse** `http://localhost:8501` no navegador
4. **Faça login** ou crie uma conta
5. **Explore** as funcionalidades:
   - Dashboard com estatísticas
   - Análise postural com upload de imagens
   - Exercícios posturais interativos
   - Gerenciamento de estudantes e escolas
   - Relatórios e análises

## Contribuição
Este projeto foi desenvolvido como uma versão Python do sistema original de avaliação postural digital, mantendo todas as funcionalidades principais em uma stack tecnológica unificada.

## Licença
Projeto desenvolvido para fins educacionais e profissionais.

