# Guia de Instalação - Avaliação Postural Digital (Python)

## Pré-requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

## Instalação

### 1. Clone ou baixe o projeto

```bash
# Se usando git
git clone <url-do-repositorio>
cd avaliacao_postural_python

# Ou simplesmente extraia o arquivo ZIP do projeto
```

### 2. Instale as dependências do backend

```bash
cd backend
pip install -r requirements.txt
```

### 3. Instale as dependências do frontend

```bash
# Volte para o diretório raiz
cd ..
pip install streamlit streamlit-option-menu streamlit-webrtc
```

## Executando a Aplicação

### 1. Inicie o backend (Flask)

```bash
cd backend
python src/main.py
```

O backend estará rodando em `http://localhost:5000`

### 2. Inicie o frontend (Streamlit) - Em outro terminal

```bash
cd frontend
streamlit run app.py
```

O frontend estará disponível em `http://localhost:8501`

## Funcionalidades Disponíveis

### ✅ Sistema de Autenticação
- Login e registro de usuários
- Diferentes tipos de usuário (estudante, profissional, administrador)
- Autenticação JWT

### ✅ Dashboard Interativo
- Métricas em tempo real
- Gráficos de evolução das avaliações
- Distribuição por classificação postural

### ✅ Análise Postural com IA
- Upload de imagens para análise
- Detecção automática de pontos corporais
- Métricas de alinhamento postural
- Relatórios detalhados

### ✅ Exercícios Posturais Interativos (2D)
- **Alongamento Cervical**: Exercícios para pescoço e cervical
- **Fortalecimento do Core**: Exercícios para músculos abdominais
- **Postura Consciente**: Exercícios de consciência corporal
- **Relaxamento Guiado**: Sessões de relaxamento

### ✅ Gestão de Dados
- Gerenciamento de estudantes
- Controle de escolas
- Relatórios detalhados

## Principais Melhorias da Versão Python

1. **Interface Unificada**: Todo o sistema agora roda em Python, eliminando a necessidade de gerenciar React + Flask separadamente.

2. **Módulo VR Adaptado**: O módulo de Realidade Virtual foi convertido para uma versão 2D interativa mais acessível, mantendo todas as funcionalidades de exercícios posturais.

3. **Facilidade de Manutenção**: Código mais limpo e organizado, totalmente em Python.

4. **Melhor Performance**: Interface Streamlit otimizada para carregamento rápido.

## Estrutura do Projeto

```
avaliacao_postural_python/
├── backend/                 # API Flask
│   ├── src/
│   │   ├── main.py         # Servidor principal
│   │   ├── models/         # Modelos de dados
│   │   ├── routes/         # Rotas da API
│   │   └── services/       # Serviços (análise postural, etc.)
│   └── requirements.txt
├── frontend/               # Interface Streamlit
│   └── app.py             # Aplicação principal
└── README.md              # Documentação
```

## Suporte

Para dúvidas ou problemas, consulte a documentação ou entre em contato com o desenvolvedor.

