# 🚀 Instruções de Execução - PosturaAI v2.0

## 📋 Pré-requisitos

Antes de executar o sistema, certifique-se de ter instalado:

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Git (para controle de versão)

## 🔧 Configuração do Ambiente

### 1. Preparação do Projeto

Navegue até o diretório do projeto:
```bash
cd avaliacao_postural_python_finalizado/avaliacao_postural_python
```

### 2. Instalação das Dependências

#### Backend (Flask)
```bash
cd backend
pip install -r requirements.txt
```

#### Frontend (Streamlit)
```bash
# Volte para o diretório raiz do projeto
cd ../frontend
pip install streamlit streamlit-option-menu plotly
```

### 3. Dependências Específicas

Instale as bibliotecas de visão computacional:
```bash
pip install numpy==1.26.4
pip install mediapipe
pip install opencv-python==4.5.5.648
```

## 🚀 Executando o Sistema

### 1. Iniciando o Backend

Abra um terminal e execute:
```bash
cd backend
python src/main.py
```

O backend estará disponível em: `http://localhost:5000`

### 2. Iniciando o Frontend

Abra um segundo terminal e execute:
```bash
cd frontend
streamlit run app_final.py
```

O frontend estará disponível em: `http://localhost:8501`

## 🌐 Acessando o Sistema

1. Abra seu navegador web
2. Acesse: `http://localhost:8501`
3. Você verá a tela de login do PosturaAI

## 👤 Criando sua Primeira Conta

1. Clique na aba "📝 Registro"
2. Preencha os campos:
   - Nome completo
   - Email
   - Senha
   - Tipo de usuário (Estudante/Professor)
3. Clique em "✨ Criar conta"
4. Retorne à aba "🔐 Login" e faça login

## 🔍 Usando a Análise Postural

1. Após fazer login, clique em "Análise Postural" no menu lateral
2. Clique em "Browse files" ou arraste uma imagem
3. Selecione uma imagem de pessoa em pé (formato JPG, PNG)
4. Aguarde o processamento
5. Visualize os resultados da análise

## 📊 Explorando o Dashboard

O dashboard principal mostra:
- Número total de estudantes, avaliações e exercícios
- Gráficos de evolução das avaliações
- Distribuição das classificações posturais
- Estatísticas de crescimento mensal

## 🛠️ Funcionalidades Disponíveis

### Menu Principal
- **Dashboard**: Visão geral do sistema
- **Análise Postural**: Upload e análise de imagens
- **Exercícios**: Biblioteca de exercícios posturais
- **Estudantes**: Gerenciamento de estudantes
- **Escolas**: Gerenciamento de instituições
- **Relatórios**: Relatórios detalhados

### Análise Postural Inteligente
- Upload de imagens via drag & drop
- Análise automática usando IA
- Detecção de pontos posturais
- Relatório detalhado com scores
- Recomendações personalizadas
- Histórico de avaliações

## 🔧 Solução de Problemas

### Erro de Dependências
Se encontrar erros de dependências, execute:
```bash
pip uninstall numpy opencv-python mediapipe
pip install numpy==1.26.4
pip install mediapipe
pip install opencv-python==4.5.5.648
```

### Porta em Uso
Se as portas 5000 ou 8501 estiverem em uso:
- Backend: Altere a porta em `src/main.py` (linha final)
- Frontend: Use `streamlit run app_final.py --server.port 8502`

### Problemas de CORS
Se houver problemas de comunicação entre frontend e backend, verifique se o CORS está habilitado no arquivo `src/main.py`.

## 📱 Compatibilidade

O sistema foi testado e é compatível com:
- **Navegadores**: Chrome, Firefox, Safari, Edge
- **Sistemas**: Windows, macOS, Linux
- **Dispositivos**: Desktop, tablet, mobile (responsivo)

## 🔒 Segurança

- Todas as senhas são criptografadas
- Tokens JWT para autenticação segura
- Validação de dados de entrada
- Proteção contra ataques comuns

## 📈 Performance

Para melhor performance:
- Use imagens com resolução entre 800x600 e 1920x1080
- Formatos recomendados: JPG, PNG
- Tamanho máximo: 20MB por imagem
- Certifique-se de ter boa conexão com a internet

## 🆘 Suporte

Em caso de problemas:
1. Verifique se todas as dependências estão instaladas
2. Confirme se ambos os serviços (backend e frontend) estão rodando
3. Consulte os logs no terminal para mensagens de erro
4. Verifique a documentação técnica em `MELHORIAS_IMPLEMENTADAS.md`

## 🎯 Dicas de Uso

- Para melhores resultados na análise postural, use imagens com boa iluminação
- A pessoa deve estar em pé, de perfil ou frontal
- Evite roupas muito largas que possam ocultar a postura
- Use fundo neutro sempre que possível

---

**PosturaAI v2.0** - Sistema Inteligente de Avaliação Postural Digital

*Desenvolvido com tecnologia de ponta para profissionais da saúde e educação*

